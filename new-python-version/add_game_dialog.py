from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QRadioButton, QFileDialog,
                            QButtonGroup, QWidget)
from PyQt6.QtCore import Qt
from pathlib import Path
from game import Game
from icon_extractor import extract_icon_from_exe
import tempfile
import shutil

class AddGameDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add New Game")
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Game Name
        name_layout = QHBoxLayout()
        name_label = QLabel("Game Name:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Launch Type
        launch_group = QButtonGroup(self)
        self.direct_launch = QRadioButton("Direct Launch (exe)")
        self.launcher_required = QRadioButton("Requires Launcher")
        launch_group.addButton(self.direct_launch)
        launch_group.addButton(self.launcher_required)
        self.direct_launch.setChecked(True)
        layout.addWidget(self.direct_launch)
        layout.addWidget(self.launcher_required)
        
        # Game Executable Path (always required)
        game_exe_layout = QHBoxLayout()
        self.game_exe_input = QLineEdit()
        game_exe_button = QPushButton("Browse")
        game_exe_button.clicked.connect(self.browse_game_exe)
        game_exe_layout.addWidget(QLabel("Game Executable:"))
        game_exe_layout.addWidget(self.game_exe_input)
        game_exe_layout.addWidget(game_exe_button)
        layout.addLayout(game_exe_layout)
        
        # Launcher Path section
        self.launcher_section = QWidget()
        launcher_layout = QHBoxLayout(self.launcher_section)
        self.launcher_input = QLineEdit()
        launcher_button = QPushButton("Browse")
        launcher_button.clicked.connect(self.browse_launcher_path)
        launcher_layout.addWidget(QLabel("Launcher Path:"))
        launcher_layout.addWidget(self.launcher_input)
        launcher_layout.addWidget(launcher_button)
        layout.addWidget(self.launcher_section)
        self.launcher_section.hide()  # Hidden by default
        
        # Cover Image Options
        cover_options_layout = QHBoxLayout()
        self.use_custom_cover = QRadioButton("Use Custom Cover")
        self.use_exe_icon = QRadioButton("Use Game Icon")
        self.no_cover = QRadioButton("No Cover")
        cover_group = QButtonGroup(self)
        cover_group.addButton(self.use_custom_cover)
        cover_group.addButton(self.use_exe_icon)
        cover_group.addButton(self.no_cover)
        self.no_cover.setChecked(True)
        cover_options_layout.addWidget(self.use_custom_cover)
        cover_options_layout.addWidget(self.use_exe_icon)
        cover_options_layout.addWidget(self.no_cover)
        layout.addLayout(cover_options_layout)
        
        # Custom Cover Image section
        self.cover_section = QWidget()
        cover_layout = QHBoxLayout(self.cover_section)
        self.cover_input = QLineEdit()
        cover_button = QPushButton("Browse")
        cover_button.clicked.connect(self.browse_cover_image)
        cover_layout.addWidget(QLabel("Cover Image:"))
        cover_layout.addWidget(self.cover_input)
        cover_layout.addWidget(cover_button)
        layout.addWidget(self.cover_section)
        self.cover_section.hide()  # Hidden by default
        
        # Trainer Options
        trainer_options = QHBoxLayout()
        self.has_trainer = QRadioButton("Has Trainer")
        self.no_trainer = QRadioButton("No Trainer")
        trainer_group = QButtonGroup(self)
        trainer_group.addButton(self.has_trainer)
        trainer_group.addButton(self.no_trainer)
        self.no_trainer.setChecked(True)
        trainer_options.addWidget(self.has_trainer)
        trainer_options.addWidget(self.no_trainer)
        layout.addLayout(trainer_options)
        
        # Trainer Path section
        self.trainer_section = QWidget()
        trainer_layout = QHBoxLayout(self.trainer_section)
        self.trainer_path_input = QLineEdit()
        trainer_path_button = QPushButton("Browse")
        trainer_path_button.clicked.connect(self.browse_trainer_path)
        trainer_layout.addWidget(QLabel("Trainer Path:"))
        trainer_layout.addWidget(self.trainer_path_input)
        trainer_layout.addWidget(trainer_path_button)
        layout.addWidget(self.trainer_section)
        self.trainer_section.hide()  # Hidden by default
        
        # Mod Launcher Options
        mod_options = QHBoxLayout()
        self.has_mod_launcher = QRadioButton("Has Mod Launcher")
        self.no_mod_launcher = QRadioButton("No Mod Launcher")
        mod_group = QButtonGroup(self)
        mod_group.addButton(self.has_mod_launcher)
        mod_group.addButton(self.no_mod_launcher)
        self.no_mod_launcher.setChecked(True)
        mod_options.addWidget(self.has_mod_launcher)
        mod_options.addWidget(self.no_mod_launcher)
        layout.addLayout(mod_options)
        
        # Mod Launcher Path section
        self.mod_section = QWidget()
        mod_layout = QHBoxLayout(self.mod_section)
        self.mod_path_input = QLineEdit()
        mod_path_button = QPushButton("Browse")
        mod_path_button.clicked.connect(self.browse_mod_path)
        mod_layout.addWidget(QLabel("Mod Launcher Path:"))
        mod_layout.addWidget(self.mod_path_input)
        mod_layout.addWidget(mod_path_button)
        layout.addWidget(self.mod_section)
        self.mod_section.hide()  # Hidden by default
        
        # Game Directory
        dir_layout = QHBoxLayout()
        self.dir_input = QLineEdit()
        dir_button = QPushButton("Browse")
        dir_button.clicked.connect(self.browse_directory)
        dir_layout.addWidget(QLabel("Game Directory:"))
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(dir_button)
        layout.addLayout(dir_layout)
        
        # Play Button Action
        play_action_layout = QVBoxLayout()
        play_action_label = QLabel("Play Button Action:")
        play_action_layout.addWidget(play_action_label)
        
        self.play_action_group = QButtonGroup(self)
        self.play_default = QRadioButton("Default (Game/Launcher)")
        self.play_game = QRadioButton("Always Game Exe")
        self.play_launcher = QRadioButton("Always Launcher")
        self.play_mods = QRadioButton("Mod Launcher")
        self.play_trainer = QRadioButton("Trainer")
        
        self.play_default.setChecked(True)
        play_action_layout.addWidget(self.play_default)
        play_action_layout.addWidget(self.play_game)
        play_action_layout.addWidget(self.play_launcher)
        play_action_layout.addWidget(self.play_mods)
        play_action_layout.addWidget(self.play_trainer)
        
        for button in [self.play_mods, self.play_trainer]:
            button.setEnabled(False)
        
        layout.addLayout(play_action_layout)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")
        save_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
        # Connect signals
        self.launcher_required.toggled.connect(self.toggle_launcher_section)
        self.has_trainer.toggled.connect(self.toggle_trainer_section)
        self.has_mod_launcher.toggled.connect(self.toggle_mod_section)
        self.use_custom_cover.toggled.connect(self.toggle_cover_section)
        self.has_mod_launcher.toggled.connect(self.update_play_options)
        self.has_trainer.toggled.connect(self.update_play_options)
        self.launcher_required.toggled.connect(self.update_play_options)
        
    def toggle_trainer(self, checked):
        self.trainer_path_input.setEnabled(checked)
        
    def toggle_mod_launcher(self, checked):
        self.mod_path_input.setEnabled(checked)
        
    def toggle_cover_input(self, checked):
        self.cover_input.setEnabled(self.use_custom_cover.isChecked())
        
    def toggle_launcher_input(self, checked):
        self.launcher_input.setEnabled(checked)
        
    def browse_game_exe(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Game Executable", "", "Executable (*.exe)")
        if file_path:
            self.game_exe_input.setText(file_path)
            # Auto-fill directory if empty
            if not self.dir_input.text():
                self.dir_input.setText(str(Path(file_path).parent))
    
    def browse_mod_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Mod Launcher", "", "Executable (*.exe)")
        if file_path:
            self.mod_path_input.setText(file_path)
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Game Directory")
        if directory:
            self.dir_input.setText(directory)
    
    def browse_cover_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Cover Image", "", "Images (*.png *.jpg *.jpeg)")
        if file_path:
            self.cover_input.setText(file_path)
    
    def browse_trainer_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Trainer", "", "Executable (*.exe)")
        if file_path:
            self.trainer_path_input.setText(file_path)
    
    def browse_launcher_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Game Launcher", "", "Executable (*.exe)")
        if file_path:
            self.launcher_input.setText(file_path)
    
    def get_game_data(self) -> Game:
        game_exe_path = Path(self.game_exe_input.text())
        cover_path = None
        
        if self.use_custom_cover.isChecked() and self.cover_input.text():
            cover_path = self.save_cover_image(Path(self.cover_input.text()))
        elif self.use_exe_icon.isChecked():
            cover_path = self.save_exe_icon(game_exe_path)
        
        # Determine play action
        play_action = "default"
        if self.play_game.isChecked():
            play_action = "game"
        elif self.play_launcher.isChecked():
            play_action = "launcher"
        elif self.play_mods.isChecked():
            play_action = "mods"
        elif self.play_trainer.isChecked():
            play_action = "trainer"
        
        return Game(
            name=self.name_input.text(),
            direct_launch=self.direct_launch.isChecked(),
            launcher_path=Path(self.launcher_input.text()) if self.launcher_required.isChecked() else None,
            game_exe_path=game_exe_path,
            mod_launcher_path=Path(self.mod_path_input.text()) if self.has_mod_launcher.isChecked() else None,
            game_directory=Path(self.dir_input.text()),
            trainer_path=Path(self.trainer_path_input.text()) if self.has_trainer.isChecked() else None,
            cover_image=cover_path,
            play_action=play_action
        )
    
    def save_cover_image(self, source_path: Path) -> Path:
        # Create covers directory if it doesn't exist
        covers_dir = Path("covers")
        covers_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        dest_path = covers_dir / f"{self.name_input.text()}_{source_path.name}"
        
        # Copy the image
        shutil.copy2(source_path, dest_path)
        return dest_path
    
    def save_exe_icon(self, exe_path: Path) -> Path | None:
        # Create covers directory if it doesn't exist
        covers_dir = Path("covers")
        covers_dir.mkdir(exist_ok=True)
        
        # Generate icon filename
        icon_path = covers_dir / f"{self.name_input.text()}_icon.png"
        
        # Extract and save icon
        return extract_icon_from_exe(exe_path, icon_path)

    def toggle_launcher_section(self, checked):
        self.launcher_section.setVisible(checked)

    def toggle_trainer_section(self, checked):
        self.trainer_section.setVisible(checked)

    def toggle_mod_section(self, checked):
        self.mod_section.setVisible(checked)

    def toggle_cover_section(self, checked):
        self.cover_section.setVisible(checked)

    def update_play_options(self, checked):
        # Enable/disable options based on what's available
        self.play_mods.setEnabled(self.has_mod_launcher.isChecked())
        self.play_trainer.setEnabled(self.has_trainer.isChecked())
        self.play_launcher.setEnabled(self.launcher_required.isChecked())
        
        # If current selection is no longer valid, switch to default
        if not self.play_mods.isEnabled() and self.play_mods.isChecked():
            self.play_default.setChecked(True)
        if not self.play_trainer.isEnabled() and self.play_trainer.isChecked():
            self.play_default.setChecked(True)
        if not self.play_launcher.isEnabled() and self.play_launcher.isChecked():
            self.play_default.setChecked(True) 