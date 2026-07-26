from __future__ import annotations

import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from types import TracebackType

from platformdirs import user_log_path


def configure_logging() -> Path:
    log_dir = user_log_path("InterestStatementGeneratorPro", "Jinesh")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "application.log"
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    if not root.handlers:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5_000_000,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        root.addHandler(console)

    def handle_exception(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_tb: TracebackType | None,
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        logging.getLogger("crash").critical(
            "Unhandled exception\n%s",
            "".join(traceback.format_exception(exc_type, exc_value, exc_tb)),
        )

    sys.excepthook = handle_exception
    return log_file
