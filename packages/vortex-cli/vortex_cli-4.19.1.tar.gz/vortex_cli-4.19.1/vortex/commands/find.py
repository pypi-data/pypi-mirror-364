from __future__ import annotations

from vortex.models import DesignType
from vortex.models import PuakmaServer
from vortex.util import render_objects
from vortex.workspace import Workspace


def find(
    workspace: Workspace,
    server: PuakmaServer,
    query: str,
    *,
    app_ids: list[int] | None = None,
    design_types: list[DesignType] | None = None,
    show_params: bool = False,
    show_ids_only: bool = False,
    strict_search: bool = False,
    search_parent_page: bool = False,
    search_inherits_from: bool = False,
) -> int:
    if app_ids:
        apps = [workspace.lookup_app(server, id_) for id_ in app_ids]
    else:
        apps = workspace.listapps(server)

    matches = []
    for app in apps:
        for obj in app.design_objects:
            value_to_search = obj.name
            if search_inherits_from:
                value_to_search = obj.inherit_from or ""
            elif search_parent_page:
                value_to_search = obj.parent_page or ""
            if (
                (not strict_search and (query.lower() in value_to_search.lower()))
                or (query == value_to_search)
            ) and (not design_types or obj.design_type in design_types):
                matches.append(obj)

    if show_ids_only:
        for obj in matches:
            print(obj.id)
    else:
        render_objects(matches, show_params=show_params)

    return 0
