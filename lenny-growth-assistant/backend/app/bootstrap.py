"""Bootstrap the public starter knowledge base without committing raw data."""

import io
import logging
import shutil
import urllib.request
import zipfile
from pathlib import Path

from .db import SessionLocal
from .ingest import DATA_ROOT, ingest, knowledge_base_ready
from .models import Document

logger = logging.getLogger(__name__)
DATA_URL = "https://github.com/LennysNewsletter/lennys-newsletterpodcastdata/archive/refs/heads/main.zip"


def download_starter_dataset() -> None:
    DATA_ROOT.parent.mkdir(parents=True, exist_ok=True)
    if DATA_ROOT.exists():
        shutil.rmtree(DATA_ROOT)

    logger.info("downloading_lenny_starter_dataset")
    with urllib.request.urlopen(DATA_URL, timeout=45) as response:
        payload = response.read()

    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        root_names = [n for n in archive.namelist() if n.endswith("/")]
        root = root_names[0].split("/")[0] if root_names else "lennys-newsletterpodcastdata-main"
        target = DATA_ROOT.parent / root
        archive.extractall(DATA_ROOT.parent)
        if target != DATA_ROOT:
            if DATA_ROOT.exists():
                shutil.rmtree(DATA_ROOT)
            target.rename(DATA_ROOT)

    logger.info("lenny_starter_dataset_ready", extra={"path": str(DATA_ROOT)})


def ensure_knowledge_base() -> None:
    if knowledge_base_ready():
        return
    try:
        download_starter_dataset()
        ingest()
        with SessionLocal() as db:
            count = db.query(Document).count()
        logger.info("knowledge_base_ready", extra={"documents": count})
    except Exception:
        logger.exception("knowledge_base_bootstrap_failed")
        # Let the API start so /health remains available. Chat will return a
        # grounded "no excerpts" response until ingestion is repaired.
