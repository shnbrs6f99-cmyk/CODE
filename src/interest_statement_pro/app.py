from __future__ import annotations

import logging

from .gui import MainWindow
from .logging_config import configure_logging
from .services import StatementProcessingService


def main() -> None:
    log_file = configure_logging()
    logging.getLogger(__name__).info("Starting application; log=%s", log_file)
    service = StatementProcessingService()
    window = MainWindow(service)
    window.mainloop()


if __name__ == "__main__":
    main()
