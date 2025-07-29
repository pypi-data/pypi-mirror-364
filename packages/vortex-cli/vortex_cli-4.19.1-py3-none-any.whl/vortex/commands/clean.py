from __future__ import annotations

import logging
import shutil

from vortex.models import PuakmaServer
from vortex.workspace import Workspace

logger = logging.getLogger("vortex")


def clean(workspace: Workspace, server: PuakmaServer, include_all: bool = False) -> int:
    cloned_apps = workspace.listapps(None if include_all else server)
    if cloned_apps:
        host_dirs = set(workspace.path / app.host for app in cloned_apps)
        with workspace.exclusive_lock():
            for host_dir in host_dirs:
                shutil.rmtree(host_dir)
                logger.debug(f"Deleted directory '{host_dir}'")
            workspace.update_vscode_settings()
    logger.info("Workspace cleaned")
    return 0
