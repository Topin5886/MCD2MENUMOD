"""Point d'entrée de MCD2 Item Forge.

Lancement :  python main.py      (ou double-clic sur lancer.bat)
"""

from __future__ import annotations

import logging
import platform
import sys

from PySide6.QtCore import QLibraryInfo, QLocale, QTimer, QTranslator
from PySide6.QtWidgets import QApplication, QMessageBox

from app import __app_name__, __version__
from app.core.catalog import Catalog
from app.core.errors import DataFileError
from app.core.settings import load_settings
from app.logging_setup import setup_logging
from app.paths import ENCHANTMENTS_FILE, ITEMS_FILE, LOGS_DIR, SETTINGS_FILE, ensure_userdata_dirs
from app.ui.main_window import MainWindow
from app.ui.theme import apply_theme, make_app_icon

log = logging.getLogger("app")


def _install_excepthook() -> None:
    """Toute erreur non prévue est journalisée et signalée, au lieu de fermer l'application en silence."""

    def hook(exc_type, exc, traceback) -> None:  # type: ignore[no-untyped-def]
        log.critical("Erreur non gérée", exc_info=(exc_type, exc, traceback))
        if QApplication.instance() is not None:
            QMessageBox.critical(
                None, "Erreur inattendue",
                f"{exc_type.__name__} : {exc}\n\nLe détail est enregistré dans userdata/logs/app.log.",
            )

    sys.excepthook = hook


def _load_qt_translations(app: QApplication) -> None:
    """Boutons et menus standards de Qt en français (Copier, Coller, Annuler...)."""
    translator = QTranslator(app)
    if translator.load(QLocale(QLocale.Language.French), "qtbase", "_", QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath)):
        app.installTranslator(translator)


def main() -> int:
    ensure_userdata_dirs()
    setup_logging(LOGS_DIR)
    log.info("Démarrage de %s %s (Python %s, %s)", __app_name__, __version__, platform.python_version(), platform.platform())

    if sys.platform == "win32":
        # Identifiant propre à l'application : la barre des tâches affiche son icône, pas celle de Python.
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("MCD2ItemForge")

    app = QApplication(sys.argv)
    app.setApplicationName(__app_name__)
    app.setApplicationVersion(__version__)
    app.setWindowIcon(make_app_icon())
    apply_theme(app)
    _load_qt_translations(app)
    _install_excepthook()

    try:
        catalog = Catalog.load(ITEMS_FILE, ENCHANTMENTS_FILE)
    except DataFileError as exc:
        log.error("Catalogue invalide : %s", exc)
        QMessageBox.critical(None, "Catalogue invalide", f"{exc}\n\nCorrige le fichier puis relance l'application.")
        return 1

    window = MainWindow(catalog, load_settings(SETTINGS_FILE))
    window.show()
    QTimer.singleShot(0, window.show_tutorial_if_first_launch)  # une fois la fenêtre affichée
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
