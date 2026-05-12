"""Logging mínimo para scripts PRODAM. Importar com:
    from logging_config import get_logger
    logger = get_logger(__name__)
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_DIR = Path(__file__).parent.parent / "PRODAM_DOCS" / "logs"
_LOG_DIR.mkdir(exist_ok=True)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        fh = RotatingFileHandler(
            _LOG_DIR / "prodam.log",
            maxBytes=5_000_000,
            backupCount=3,
            encoding="utf-8",
        )
        fh.setLevel(logging.DEBUG)
        fmt = logging.Formatter(
            "%(asctime)s %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
        fmt.converter = lambda *a: __import__("time").gmtime()
        fh.setFormatter(fmt)
        logger.addHandler(fh)
    return logger
