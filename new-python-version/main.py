import sys
from PyQt6.QtWidgets import QApplication
from game_launcher import GameLauncher

def main():
    app = QApplication(sys.argv)
    launcher = GameLauncher()
    launcher.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 