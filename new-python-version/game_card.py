from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QFrame, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
import subprocess
import os
from game import Game
from edit_game_dialog import EditGameDialog

class GameCard(QWidget):
    def __init__(self, game: Game, parent=None):
        super().__init__(parent)
        self.game = game
        self.setup_ui()
        self.setStyleSheet("""
            GameCard {
                border: 1px solid #666666;
                border-radius: 4px;
                background-color: #303030;
                padding: 4px;
                margin: 3px;
            }
            GameCard QPushButton {
                min-width: 60px;
                max-width: none;
                padding: 4px;
                font-size: 9pt;
                background-color: #424242;
                border: 1px solid #999999;
                color: #000000;
            }
            GameCard QPushButton:hover {
                background-color: #d0d0d0;
            }
            GameCard QPushButton[text="Play"] {
                background-color: #4CAF50;
                color: white;
                border: 1px solid #388E3C;
                font-weight: bold;
                padding: 6px;
            }
            GameCard QPushButton[text="Play"]:hover {
                background-color: #45a049;
            }
            GameCard QPushButton[text="Delete"] {
                background-color: #ff4444;
                color: white;
                border: 1px solid #cc0000;
            }
            GameCard QPushButton[text="Delete"]:hover {
                background-color: #ff0000;
            }
            GameCard QLabel {
                min-height: 14px;
            }
        """)
        
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(4)  # Reduce spacing between elements
        
        # Game cover/icon and name in horizontal layout
        top_layout = QHBoxLayout()
        top_layout.setSpacing(6)  # Space between icon and name
        
        if self.game.cover_image and self.game.cover_image.exists():
            cover = QLabel()
            pixmap = QPixmap(str(self.game.cover_image))
            cover.setPixmap(pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, 
                                        Qt.TransformationMode.SmoothTransformation))
            top_layout.addWidget(cover)
        
        # Game name
        name_label = QLabel(self.game.name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
        font = name_label.font()
        font.setPointSize(9)
        name_label.setFont(font)
        top_layout.addWidget(name_label)
        
        layout.addLayout(top_layout)
        
        # Play button spanning full width
        play_button = QPushButton("Play")
        play_button.clicked.connect(self.launch_game)
        layout.addWidget(play_button)
        
        # Other buttons in a grid
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(2)  # Reduce spacing between buttons
        
        current_row = 0
        current_col = 0
        
        # Determine which buttons to show based on play action
        if self.game.play_action == "mods":
            # Show game/launcher button instead of mods
            if self.game.direct_launch:
                alt_button = QPushButton("Game")
                alt_button.clicked.connect(self.launch_game_exe)
            else:
                alt_button = QPushButton("Launcher")
                alt_button.clicked.connect(self.launch_launcher)
            buttons_layout.addWidget(alt_button, current_row, current_col)
            current_col += 1
        elif self.game.mod_launcher_path:
            mod_button = QPushButton("Mods")
            mod_button.clicked.connect(self.launch_mod_launcher)
            buttons_layout.addWidget(mod_button, current_row, current_col)
            current_col += 1
        
        if self.game.play_action == "trainer":
            # Show game/launcher button instead of trainer
            if self.game.direct_launch:
                alt_button = QPushButton("Game")
                alt_button.clicked.connect(self.launch_game_exe)
            else:
                alt_button = QPushButton("Launcher")
                alt_button.clicked.connect(self.launch_launcher)
            buttons_layout.addWidget(alt_button, current_row, current_col)
            current_col += 1
        elif self.game.trainer_path:
            trainer_button = QPushButton("Trainer")
            trainer_button.clicked.connect(self.launch_trainer)
            buttons_layout.addWidget(trainer_button, current_row, current_col)
            current_col += 1
        
        folder_button = QPushButton("Folder")
        folder_button.clicked.connect(self.open_directory)
        buttons_layout.addWidget(folder_button, current_row, current_col)
        current_col += 1
        
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_game)
        buttons_layout.addWidget(edit_button, current_row, current_col)
        current_col += 1
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_game)
        buttons_layout.addWidget(delete_button, current_row, current_col)
        
        layout.addLayout(buttons_layout)
        
        # Make layout more compact
        layout.setContentsMargins(4, 4, 4, 4)
        
        self.setLayout(layout)
        
    def launch_game(self):
        if self.game.play_action == "game":
            self.launch_game_exe()
        elif self.game.play_action == "launcher":
            self.launch_launcher()
        elif self.game.play_action == "mods":
            self.launch_mod_launcher()
        elif self.game.play_action == "trainer":
            self.launch_trainer()
        else:  # default behavior
            launch_path = self.game.launcher_path if not self.game.direct_launch else self.game.game_exe_path
            subprocess.Popen([str(launch_path)], cwd=str(self.game.game_directory))
        
    def launch_game_exe(self):
        subprocess.Popen([str(self.game.game_exe_path)], cwd=str(self.game.game_directory))
        
    def launch_launcher(self):
        if self.game.launcher_path:
            subprocess.Popen([str(self.game.launcher_path)], cwd=str(self.game.game_directory))
        
    def launch_mod_launcher(self):
        if self.game.mod_launcher_path:
            try:
                # Create a ProcessStartupInfo object with admin privileges
                import win32process
                import win32con
                import win32event
                import win32api

                # Launch with shell elevation prompt
                from win32com.shell.shell import ShellExecuteEx
                from win32com.shell import shellcon

                ShellExecuteEx(
                    lpVerb='runas',  # This requests elevation
                    lpFile=str(self.game.mod_launcher_path),
                    lpParameters='',  # Add parameters here if needed
                    nShow=win32con.SW_SHOWNORMAL,
                    fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                    lpDirectory=str(self.game.game_directory)
                )

            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", 
                                   f"Failed to launch mod launcher:\n{str(e)}")
    
    def launch_trainer(self):
        if self.game.trainer_path:
            try:
                # Launch trainer with admin privileges like mod launcher
                from win32com.shell.shell import ShellExecuteEx
                from win32com.shell import shellcon
                import win32con

                ShellExecuteEx(
                    lpVerb='runas',
                    lpFile=str(self.game.trainer_path),
                    lpParameters='',
                    nShow=win32con.SW_SHOWNORMAL,
                    fMask=shellcon.SEE_MASK_NOCLOSEPROCESS,
                    lpDirectory=str(self.game.game_directory)
                )
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Error", 
                                   f"Failed to launch trainer:\n{str(e)}")
    
    def open_directory(self):
        os.startfile(str(self.game.game_directory))
    
    def edit_game(self):
        dialog = EditGameDialog(self.game, self)
        if dialog.exec():
            updated_game = dialog.get_game_data()
            # Update the current game with new data
            for attr in ['name', 'direct_launch', 'launcher_path', 'game_exe_path',
                        'mod_launcher_path', 'game_directory', 'trainer_path', 
                        'cover_image', 'play_action']:
                setattr(self.game, attr, getattr(updated_game, attr))
            
            # Find parent GameLauncher to trigger save and refresh
            parent = self.parent()
            while parent:
                if hasattr(parent, 'save_games'):
                    parent.save_games()
                    parent.refresh_games()
                    break
                parent = parent.parent()

    def delete_game(self):
        from PyQt6.QtWidgets import QMessageBox
        
        # Show confirmation dialog
        reply = QMessageBox.question(
            self,
            'Confirm Delete',
            f'Are you sure you want to delete "{self.game.name}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Delete cover image if it exists
            if self.game.cover_image and self.game.cover_image.exists():
                try:
                    self.game.cover_image.unlink()
                except Exception as e:
                    print(f"Failed to delete cover image: {e}")
            
            # Find parent GameLauncher to remove game and refresh
            parent = self.parent()
            while parent:
                if hasattr(parent, 'delete_game'):
                    parent.delete_game(self.game)
                    break
                parent = parent.parent() 