"""
Main entry point for the YouVideo Downloader application.

This script initializes the PySide6 application, creates the main window,
and starts the application's event loop.

Modules:
    PySide6.QtWidgets.QApplication: Provides the main application object for the GUI.
    ui.main_window.MainWindow: Imports the main window class for the application.
    sys: Used for accessing command-line arguments and exiting the application.

Execution:
    When run as the main module, this script creates a QApplication instance,
    instantiates the MainWindow, displays it, and starts the event loop.
"""

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QIcon
from ui.welcome_screen import WelcomeScreen
from ui.main_window import MainWindow
import sys

from utils.pathfinder import resource_path

def main():
    """
    Initializes and runs the main application.

    Creates a QApplication instance, displays a welcome screen, and upon user continuation,
    closes the welcome screen and shows the main application window. Exits the application
    when the main event loop finishes.
    """
    app = QApplication(sys.argv)
    app_icon = resource_path("assets/icons/appicon.png")
    app.setWindowIcon(QIcon(app_icon))

    main_win = MainWindow()

    def show_main():
        welcome.close()
        main_win.show()

    welcome = WelcomeScreen(on_continue=show_main)
    welcome.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
