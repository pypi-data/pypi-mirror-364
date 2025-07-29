from __future__ import annotations

import logging
from pathlib import Path

from vortex.models import PuakmaServer
from vortex.spinner import Spinner

logger = logging.getLogger("vortex")


def import_(server: PuakmaServer, pmx_path: Path, name: str, group: str) -> int:
    with Spinner("Importing..."):
        with open(pmx_path, "rb") as f:
            pmx_bytes = f.read()

        with server as s:
            app_id = s.download_designer.upload_pmx(group, name, pmx_bytes)
    logger.info(f"Created Application {group}/{name} [{app_id}] from {pmx_path.name}")
    return 0
