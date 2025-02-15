from PyQt6.QtWidgets import QDialog
from add_game_dialog import AddGameDialog
from game import Game
from pathlib import Path

class EditGameDialog(AddGameDialog):
    def __init__(self, game: Game, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Game")
        self.populate_fields(game)
    
    def populate_fields(self, game: Game):
        # Fill in existing game data
        self.name_input.setText(game.name)
        self.direct_launch.setChecked(game.direct_launch)
        self.launcher_required.setChecked(not game.direct_launch)
        self.game_exe_input.setText(str(game.game_exe_path))
        self.dir_input.setText(str(game.game_directory))
        
        # Handle mod launcher
        if game.mod_launcher_path:
            self.has_mod_launcher.setChecked(True)
            self.mod_path_input.setText(str(game.mod_launcher_path))
        else:
            self.no_mod_launcher.setChecked(True)
        
        # Handle trainer
        if game.trainer_path:
            self.has_trainer.setChecked(True)
            self.trainer_path_input.setText(str(game.trainer_path))
        else:
            self.no_trainer.setChecked(True)
        
        # Handle cover image
        if game.cover_image:
            if game.cover_image.name.endswith('_icon.png'):
                self.use_exe_icon.setChecked(True)
            else:
                self.use_custom_cover.setChecked(True)
                self.cover_input.setText(str(game.cover_image))
        else:
            self.no_cover.setChecked(True)
        
        # Handle launcher path
        if game.launcher_path:
            self.launcher_input.setText(str(game.launcher_path))
        else:
            self.no_launcher.setChecked(True)
        
        # Handle play action
        if game.play_action == "default":
            self.play_default.setChecked(True)
        elif game.play_action == "game":
            self.play_game.setChecked(True)
        elif game.play_action == "launcher":
            self.play_launcher.setChecked(True)
        elif game.play_action == "mods":
            self.play_mods.setChecked(True)
        elif game.play_action == "trainer":
            self.play_trainer.setChecked(True) 