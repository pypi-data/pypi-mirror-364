from __future__ import annotations

import asyncio
import datetime
import logging
import zipfile
from io import BytesIO
from pathlib import Path

from vortex.models import PuakmaServer
from vortex.spinner import Spinner
from vortex.workspace import Workspace

logger = logging.getLogger("vortex")


def _save_bytes(data: bytes, output_path: Path) -> None:
    with open(output_path, "wb") as f:
        f.write(data)


async def _aexport(
    server: PuakmaServer,
    app_ids: set[int],
    output_dir: Path,
    timeout: int,
    include_source: bool,
) -> int:
    tasks = []

    async with server as s:
        await s.server_designer.ainitiate_connection()
        for app_id in app_ids:
            task = asyncio.create_task(
                _aexport_app_pmx(server, app_id, output_dir, timeout, include_source)
            )
            tasks.append(task)

        ret = 0
        for done in asyncio.as_completed(tasks):
            try:
                ret |= await done
            except (KeyboardInterrupt, Exception):
                for task in tasks:
                    task.cancel()
                raise
            except asyncio.CancelledError:
                logger.error("Operation Cancelled")
                for task in tasks:
                    task.cancel()
                ret = 1
                break
    return ret


async def _aexport_app_pmx(
    server: PuakmaServer,
    app_id: int,
    output_dir: Path,
    timeout: int,  # noqa: ASYNC109
    include_source: bool,
) -> int:
    ret_bytes = await server.download_designer.adownload_pmx(
        app_id, include_source, timeout
    )
    with zipfile.ZipFile(BytesIO(ret_bytes)) as zip_file:
        fname = zip_file.namelist()[0].replace(".pma", "")
        try:
            _, group, app_name = fname.split("~")
        except ValueError:
            # no group
            _, app_name = fname.split("~")
            group = ""

    now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    name = f"{group}~{app_name}" if group else app_name
    export_name = f"{server.host}~{name}~{app_id}~{now}.pmx"
    output_path = output_dir / export_name
    await asyncio.to_thread(_save_bytes, ret_bytes, output_path)
    logger.info(
        f"Successfully exported {group}/{app_name} [{app_id}] to {output_dir.resolve()}"
    )
    return 0


def export(
    workspace: Workspace,
    server: PuakmaServer,
    app_ids: set[int],
    *,
    timeout: int,
    include_source: bool,
    export_dir: Path | None = None,
) -> int:
    with (
        workspace.exclusive_lock(),
        Spinner(f"Exporting {len(app_ids)} application(s)..."),
    ):
        if export_dir is None:
            export_dir = workspace.exports_dir
        export_dir.mkdir(exist_ok=True)
        ret = asyncio.run(
            _aexport(server, app_ids, export_dir, timeout, include_source)
        )
        return ret
