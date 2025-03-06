# calculator/main.py
from PySide6.QtWidgets import QApplication # type: ignore
from ui.main_window import MainWindow

def main():
    app = QApplication([])  # Create the application
    window = MainWindow()    # Create the main window
    window.show()            # Show the window
    app.exec()               # Start the application's event loop

if __name__ == "__main__":
    main()
