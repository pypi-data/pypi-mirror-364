from __future__ import annotations

import asyncio
import logging
import mimetypes
import sys
from pathlib import Path
from typing import Literal

from watchfiles import BaseFilter
from watchfiles import Change
from watchfiles import awatch

from vortex.colour import Colour
from vortex.models import DesignObject
from vortex.models import DesignObjectAmbiguousError
from vortex.models import DesignObjectNotFound
from vortex.models import DesignPath
from vortex.models import DesignType
from vortex.models import InvalidDesignPathError
from vortex.models import JavaClassVersion
from vortex.models import PuakmaApplication
from vortex.models import PuakmaServer
from vortex.spinner import Spinner
from vortex.workspace import Workspace

logger = logging.getLogger("vortex")

_CLASS_EXT = ".class"

WorkspaceChange = tuple[Change, DesignPath, PuakmaApplication]


def _error(change: Change, name: str, msg: str) -> Literal[False]:
    msg = f"Failed to process '{name}': {msg}"
    logger.warning(f"({change.raw_str()}) {msg}")
    return False


class _WorkspaceFilter(BaseFilter):
    ignore_files: tuple[str, ...] = (
        ".DS_Store",
        PuakmaApplication.MANIFEST_FILE,
    )

    def __init__(self, workspace: Workspace, server: PuakmaServer) -> None:
        self.workspace = workspace
        self.server = server

    def __call__(self, change: Change, _path: str) -> bool:
        def _err(msg: str) -> bool:
            return _error(change, path.name, msg)

        path = Path(_path)
        _is_class_file = path.suffix == _CLASS_EXT

        do_event = (change in (Change.modified, Change.added) and path.is_file()) or (
            change == Change.deleted and not _is_class_file
        )

        if not do_event or path.name in self.ignore_files:
            return False
        try:
            design_path = DesignPath(self.workspace, path)
        except InvalidDesignPathError as e:
            return _err(str(e))
        else:
            design_server_host = design_path.app.host
            if design_server_host != self.server.host:
                msg = f"({design_server_host}) does not match ({self.server.host})"
                return _err(msg)
        return True


class WorkspaceWatcher:
    def __init__(
        self, workspace: Workspace, server: PuakmaServer, spinner: Spinner | None = None
    ) -> None:
        self.workspace = workspace
        self.server = server
        self.spinner = spinner
        self.filter = _WorkspaceFilter(workspace, server)
        self._dispatch_change = {
            Change.modified: self._update_design,
            Change.added: self._create_design,
            Change.deleted: self._delete_design,
        }

    async def watch(self) -> int:
        async with self.server as s:
            msg = await s.server_designer.ainitiate_connection()
            print(msg)
            _error = False
            changes = None
            dirs = self.workspace.listdir(s, strict=True)

            while True:
                try:
                    async for changes in awatch(*dirs, watch_filter=self.filter):
                        try:
                            await self._handle_changes(changes)
                        except (Exception, asyncio.CancelledError) as e:
                            logger.critical(e, stack_info=True)
                            _error = True
                            break
                except Exception as e:
                    logger.error(f"Error getting changes: {e}")
                    if changes:
                        try:
                            await self._handle_changes(changes)
                        except (Exception, asyncio.CancelledError) as e:
                            logger.critical(e, stack_info=True)
                            _error = True
                if _error:
                    break
        return 1 if _error else 0

    async def _handle_changes(self, changes: set[tuple[Change, str]]) -> None:
        apps: dict[int, PuakmaApplication] = {}
        modified: list[WorkspaceChange] = []
        added_or_deleted: list[WorkspaceChange] = []

        for change, _path in changes:
            path = Path(_path)
            _is_class_file = path.suffix == _CLASS_EXT
            if _is_class_file and change == Change.added:
                change = Change.modified
            design_path = DesignPath(self.workspace, path)

            app_id = design_path.app.id
            if app_id not in apps.keys():
                apps[app_id] = design_path.app
            app = apps[app_id]
            val = change, design_path, app

            if change == Change.modified:
                modified.append(val)
            elif change in [Change.added, Change.deleted]:
                added_or_deleted.append(val)

        if modified:
            await self._dispatch_modified(modified)
        if added_or_deleted:
            await self._dispatch_added_deleted(added_or_deleted)
        # now update the apps since design objects will have changed
        for app in apps.values():
            self.workspace.mkdir(app)

    async def _dispatch_modified(self, changes: list[WorkspaceChange]) -> None:
        tasks = [asyncio.create_task(self._update_design(*args)) for args in changes]
        for result in asyncio.as_completed(tasks):
            try:
                await result
            except asyncio.CancelledError as e:
                logger.error(f"Operation Cancelled. {e}")

    async def _dispatch_added_deleted(self, changes: list[WorkspaceChange]) -> None:
        # Do this synchronously since we will be prompting the user for confirmation
        for args in changes:
            change, design_path, _ = args
            task = asyncio.create_task(self._dispatch_change[change](*args))
            try:
                await task
            except asyncio.CancelledError as e:
                _error(change, design_path.fname, f"Operation Cancelled. {e}")

    async def _update_design(
        self, change: Change, design_path: DesignPath, app: PuakmaApplication
    ) -> bool:
        def _err_result(msg: str) -> Literal[False]:
            return _error(change, design_path.fname, msg)

        try:
            file_bytes = await asyncio.to_thread(design_path.path.read_bytes)
        except OSError as e:
            return _err_result(e.strerror)

        # If we are uploading a class file, lets verify
        # if it has been compiled correctly
        if design_path.ext == _CLASS_EXT:
            is_valid, msg = _validate_java_class_file(
                file_bytes, app.java_class_version
            )
            if not is_valid:
                return _err_result(msg)

        try:
            indx, obj = app.lookup_design_obj(design_path.design_name)
        except (DesignObjectNotFound, DesignObjectAmbiguousError) as e:
            return _err_result(str(e))

        upload_source = (
            obj.design_type.is_java_type and design_path.ext == ".java"
        ) or obj.design_type == DesignType.DOCUMENTATION

        if upload_source:
            obj.design_source = file_bytes
        else:
            obj.design_data = file_bytes

        ok = await obj.aupload(self.server.download_designer, upload_source)
        if ok:
            app.design_objects[indx] = obj
        return ok

    async def _create_design(
        self, change: Change, design_path: DesignPath, app: PuakmaApplication
    ) -> bool:
        def _err_result(msg: str) -> Literal[False]:
            return _error(change, design_path.fname, msg)

        name = design_path.design_name

        try:
            _, _obj = app.lookup_design_obj(design_path.design_name)
        except DesignObjectNotFound:
            # OK
            pass
        except DesignObjectAmbiguousError as e:
            return _err_result(str(e))
        else:
            return _err_result(f"Design Object {_obj} already exists in {app}")

        try:
            design_type = DesignType.from_name(design_path.design_dir)
        except ValueError:
            return _err_result(f"Invalid Design Type '{design_path.design_dir}'")

        content_type = (
            design_type.content_type() or mimetypes.guess_type(design_path)[0]
        )
        if not content_type:
            return _err_result("Unable to determine content type")

        # design_source = base64.b64encode(design_type.source_template(name)).decode()
        obj = DesignObject(-1, name, app, design_type, content_type, "", "")

        upload_source = False

        if design_type.is_java_type:
            obj.design_source = design_type.source_template(name)
            obj.save(self.workspace)
            upload_source = True

        try:
            file_bytes = design_path.path.read_bytes()
        except OSError as e:
            file_bytes = b""
            msg = f"Couldn't set the design contents from '{design_path}': {e}"
            logger.warning(msg)
        else:
            if upload_source:
                obj.design_source = file_bytes
            else:
                obj.design_data = file_bytes

        if not self._confirm_change(change, obj):
            return _err_result("Operation Cancelled")

        create_ok = await obj.acreate_or_update(self.server.app_designer)
        if create_ok:
            app.design_objects.append(obj)

        upload_design_ok = True
        if len(file_bytes) > 0:
            upload_design_ok = await obj.aupload(
                self.server.download_designer, upload_source
            )

        return upload_design_ok and create_ok

    async def _delete_design(
        self, change: Change, design_path: DesignPath, app: PuakmaApplication
    ) -> bool:
        def _err_result(msg: str) -> Literal[False]:
            return _error(change, design_path.fname, msg)

        try:
            _, obj = app.lookup_design_obj(design_path.design_name)
        except (DesignObjectNotFound, DesignObjectAmbiguousError) as e:
            return _err_result(str(e))

        if not self._confirm_change(change, obj):
            return _err_result("Operation Cancelled")

        await obj.adelete(self.server.app_designer)
        app.design_objects.remove(obj)
        return True

    def _confirm_change(self, change: Change, obj: DesignObject) -> bool:
        action = {
            change.deleted: Colour.colour("delete", Colour.RED),
            change.modified: "update",
            change.added: Colour.colour("create", Colour.GREEN),
        }[change]

        if self.spinner and self.spinner.running:
            self.spinner.stop()
        try:
            sys.stdout.write("\n")
            prompt = (
                f"Are you sure you wish to {action} {obj.design_type.name} {obj}? "
                "[Y/y] to confirm:"
            )
            sys.stdout.write(prompt)
            sys.stdout.flush()
            res = sys.stdin.readline().strip()
        except (KeyboardInterrupt, Exception) as e:
            raise asyncio.CancelledError(e) from e
        else:
            return res in ["Y", "y"]
        finally:
            sys.stdout.write("\n")
            sys.stdout.flush()
            if self.spinner and not self.spinner.running:
                self.spinner.start()


def _validate_java_class_file(
    class_file_bytes: bytes, expected_version: JavaClassVersion | None = None
) -> tuple[bool, str]:
    # https://en.wikipedia.org/wiki/Java_class_file#General_layout
    bytes_header = class_file_bytes[:8]
    if bytes_header[:4] != b"\xca\xfe\xba\xbe":
        return False, "Not a valid Java Class File"
    major_version = int.from_bytes(bytes_header[6:8], byteorder="big")
    minor_version = int.from_bytes(bytes_header[4:6], byteorder="big")
    compiled_version: JavaClassVersion = (major_version, minor_version)
    if expected_version and compiled_version[0] > expected_version[0]:
        return (
            False,
            f"File has been compiled with Java Class Version"
            f"{compiled_version} which is greater than {expected_version}",
        )
    return True, ""


def watch(workspace: Workspace, server: PuakmaServer) -> int:
    if not workspace.listdir():
        logger.error(f"No application directories to watch in workspace '{workspace}'")
        return 1
    with (
        workspace.exclusive_lock(),
        Spinner("Watching workspace, ^C to stop") as spinner,
    ):
        workspace.update_vscode_settings(server=server)
        watcher = WorkspaceWatcher(workspace, server, spinner)
        return asyncio.run(watcher.watch())
