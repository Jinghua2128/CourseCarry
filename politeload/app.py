from __future__ import annotations

import sys
import sqlite3

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from .config import ConfigStore
from .core.database import PoliteLoadDatabase
from .ui import MainWindow
from .ui.theme import APP_STYLESHEET, configure_app_font
from .utils.logging import configure_logging
from .utils.paths import bundled_resource
from .version import __version__


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("PoliteLoad")
    app.setApplicationVersion(__version__)
    app.setOrganizationName("PoliteLoad")
    app.setStyle("Fusion")
    configure_app_font(app)
    app.setStyleSheet(APP_STYLESHEET)
    app.setWindowIcon(
        QIcon(str(bundled_resource("politeload", "resources", "politeload-icon.png")))
    )

    store = ConfigStore()
    config = store.load()
    configure_logging(config.logs_dir)
    database = PoliteLoadDatabase(config.database_path)
    try:
        database.initialize()
    except (OSError, sqlite3.Error) as error:
        QMessageBox.critical(None, "PoliteLoad could not start", str(error))
        return 1

    window = MainWindow(config, store, database)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
