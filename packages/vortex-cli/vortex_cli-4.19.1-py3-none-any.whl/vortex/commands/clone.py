from __future__ import annotations

import asyncio
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from vortex import util
from vortex.models import DatabaseConnection
from vortex.models import DesignObject
from vortex.models import DesignObjectParam
from vortex.models import DesignType
from vortex.models import JavaClassVersion
from vortex.models import PuakmaApplication
from vortex.models import PuakmaServer
from vortex.spinner import Spinner
from vortex.workspace import Workspace

logger = logging.getLogger("vortex")


def _save_objs(
    workspace: Workspace,
    server: PuakmaServer,
    objs: list[DesignObject],
    save_resources: bool,
) -> None:
    resource_ext_only = workspace.get_resource_ext_only(server)
    for obj in objs:
        if not obj.is_valid:
            logger.warning(f"Unable to save invalid design object {obj}")
        elif (
            not save_resources
            and obj.design_type == DesignType.RESOURCE
            and obj.file_ext
            and not obj.is_jar_library
        ):
            continue
        elif (
            save_resources
            and obj.design_type == DesignType.RESOURCE
            and resource_ext_only is not None
            and obj.file_ext
            and obj.file_ext.lower().lstrip(".") not in resource_ext_only
        ):
            continue
        else:
            obj.save(workspace)


def _aparse_design_objs(
    objs: list[dict[str, Any]], app: PuakmaApplication
) -> list[DesignObject]:
    ret: list[DesignObject] = []
    for obj in objs:
        design_type_id = int(obj["type"])
        name = obj["name"]
        id_ = int(obj["id"])
        ret.append(
            DesignObject(
                id_,
                name,
                app,
                DesignType(design_type_id),
                obj["ctype"],
                obj["data"],
                obj["src"],
                inherit_from=obj["inherit"],
                comment=obj["comment"],
            )
        )
    return ret


def _parse_app_xml(
    server: PuakmaServer, app_xml: ET.Element, app_id: int
) -> tuple[PuakmaApplication, ET.Element]:
    app_ele = app_xml.find("puakmaApplication", namespaces=None)
    if not app_ele:
        raise ValueError(f"Application [{app_id}] does not exist")

    db_connections: list[DatabaseConnection] = []
    for db_ele in app_xml.findall(".//database"):
        db_conn = DatabaseConnection(
            int(db_ele.attrib["id"]),
            db_ele.attrib["name"],
            db_ele.attrib["dbName"],
            db_ele.attrib["driver"],
            db_ele.attrib["url"],
            db_ele.attrib["userName"],
            db_ele.attrib["pwd"],
        )
        db_connections.append(db_conn)

    java_version_ele = app_xml.find('.//sysProp[@name="java.class.version"]')
    if java_version_ele is None or java_version_ele.text is None:
        raise ValueError("Java class version not specified")
    major, minor = (int(v) for v in java_version_ele.text.split(".", maxsplit=1))
    version: JavaClassVersion = (major, minor)
    app = PuakmaApplication(
        id_=int(app_ele.attrib["id"]),
        name=app_ele.attrib["name"],
        group=app_ele.attrib["group"],
        inherit_from=app_ele.attrib["inherit"],
        template_name=app_ele.attrib["template"],
        java_class_version=version,
        host=server.host,
        db_connections=tuple(db_connections),
    )
    return app, app_ele


def _match_and_validate_design_objs(
    app: PuakmaApplication,
    design_objs: list[DesignObject],
    design_elements: list[ET.Element],
) -> list[DesignObject]:
    new_objects: list[DesignObject] = []
    for ele in design_elements:
        id_ = int(ele.attrib["id"])
        objs = [obj for obj in design_objs if obj.id == id_]
        is_jar_library = ele.attrib.get("library", "false") == "true"
        package = ele.attrib.get("package", None)
        package_dir = Path(*package.split(".")) if package else None

        param_eles = ele.findall(".//designParam")
        params = []
        for param_ele in param_eles:
            param = DesignObjectParam(
                param_ele.attrib["name"], param_ele.attrib["value"]
            )
            params.append(param)
        try:
            obj = objs.pop()
            obj.is_jar_library = is_jar_library or obj.file_ext == ".jar"
            obj.package_dir = package_dir
            obj.params = params
        except IndexError:
            design_type = DesignType(int(ele.attrib["designType"]))

            obj = DesignObject(
                id_,
                ele.attrib["name"],
                app,
                design_type,
                ele.attrib["contentType"],
                "",
                "",
                is_jar_library,
                package_dir,
                "",
                ele.attrib["inherit"],
                params=params,
            )
        new_objects.append(obj)
    return new_objects


async def _aclone_app(
    workspace: Workspace,
    server: PuakmaServer,
    app_id: int,
    get_resources: bool,
) -> tuple[PuakmaApplication | None, int]:
    """Clone a Puakma Application into a newly created directory"""

    resources_ext_only = workspace.get_resource_ext_only(server)
    app_xml, _obj_rows = await asyncio.gather(
        server.app_designer.aget_application_xml(app_id),
        PuakmaApplication.afetch_design_objects(
            server, app_id, get_resources, resources_ext_only
        ),
    )

    try:
        app, app_ele = _parse_app_xml(server, app_xml, app_id)
    except (ValueError, KeyError) as e:
        logger.error(e)
        return None, 1

    eles = app_ele.findall("designElement", namespaces=None)
    objs = _aparse_design_objs(_obj_rows, app)
    app.design_objects = _match_and_validate_design_objs(app, objs, eles)
    app_dir = workspace.mkdir(app, True)

    for dir_ in DesignType.dirs():
        (app_dir / dir_).mkdir()

    try:
        logger.debug(f"Saving {len(objs)} Design Objects for [{app}]...")
        await asyncio.to_thread(
            _save_objs, workspace, server, app.design_objects, get_resources
        )
    except asyncio.CancelledError:
        util.rmtree(app_dir)
        return None, 1

    logger.info(f"Successfully cloned {app}")

    return app, 0


async def _aclone_apps(
    workspace: Workspace,
    server: PuakmaServer,
    app_ids: set[int],
    get_resources: bool,
    open_urls: bool,
) -> int:
    tasks = []
    async with server as s:
        await s.server_designer.ainitiate_connection()
        for app_id in app_ids:
            task = asyncio.create_task(_aclone_app(workspace, s, app_id, get_resources))
            tasks.append(task)

        ret = 0
        for done in asyncio.as_completed(tasks):
            try:
                app, _ret = await done
                if open_urls and app:
                    util.open_app_urls(app)
                ret |= _ret
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
        else:
            workspace.update_vscode_settings(server=server)
    return ret


def clone(
    workspace: Workspace,
    server: PuakmaServer,
    app_ids: list[int],
    *,
    get_resources: bool = False,
    open_urls: bool = False,
    reclone: bool = False,
) -> int:
    if reclone:
        app_ids.extend(app.id for app in workspace.listapps(server))

    unique_app_ids = set(app_ids)
    with (
        workspace.exclusive_lock(),
        Spinner(f"Cloning {len(unique_app_ids)} application(s)..."),
    ):
        return asyncio.run(
            _aclone_apps(workspace, server, unique_app_ids, get_resources, open_urls)
        )
