from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QScrollArea, QGridLayout)
from PyQt6.QtCore import Qt
from add_game_dialog import AddGameDialog
from game_card import GameCard
from game import Game
import json
from pathlib import Path
from edit_game_dialog import EditGameDialog

class GameLauncher(QMainWindow):
    def __init__(self):
        super().__init__()
        self.games = []
        self.setup_ui()
        self.load_games()
        
    def setup_ui(self):
        self.setWindowTitle("Game Launcher")
        self.setMinimumSize(800, 600)
        
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Add Game button
        add_button = QPushButton("Add Game")
        add_button.clicked.connect(self.show_add_dialog)
        layout.addWidget(add_button)
        
        # Scroll area for game cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container for game cards
        self.games_container = QWidget()
        self.games_layout = QGridLayout(self.games_container)
        self.games_layout.setSpacing(4)  # Reduce spacing between cards
        self.games_layout.setContentsMargins(4, 4, 4, 4)  # Reduce margins
        scroll.setWidget(self.games_container)
        layout.addWidget(scroll)
        
    def show_add_dialog(self):
        dialog = AddGameDialog(self)
        if dialog.exec():
            game = dialog.get_game_data()
            self.games.append(game)
            self.save_games()
            self.refresh_games()
    
    def refresh_games(self):
        # Clear existing cards
        while self.games_layout.count():
            item = self.games_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add game cards
        for i, game in enumerate(self.games):
            row = i // 3
            col = i % 3
            card = GameCard(game, self)
            self.games_layout.addWidget(card, row, col)
    
    def save_games(self):
        games_data = []
        for game in self.games:
            games_data.append({
                'name': game.name,
                'direct_launch': game.direct_launch,
                'launcher_path': str(game.launcher_path) if game.launcher_path else None,
                'game_exe_path': str(game.game_exe_path),
                'mod_launcher_path': str(game.mod_launcher_path) if game.mod_launcher_path else None,
                'game_directory': str(game.game_directory),
                'trainer_path': str(game.trainer_path) if game.trainer_path else None,
                'cover_image': str(game.cover_image) if game.cover_image else None,
                'play_action': game.play_action
            })
        
        with open('games.json', 'w') as f:
            json.dump(games_data, f)
    
    def load_games(self):
        try:
            with open('games.json', 'r') as f:
                games_data = json.load(f)
                
            self.games = []
            for game_data in games_data:
                game = Game(
                    name=game_data['name'],
                    direct_launch=game_data['direct_launch'],
                    launcher_path=Path(game_data['launcher_path']) if game_data.get('launcher_path') else None,
                    game_exe_path=Path(game_data['game_exe_path']),
                    mod_launcher_path=Path(game_data['mod_launcher_path']) if game_data['mod_launcher_path'] else None,
                    game_directory=Path(game_data['game_directory']),
                    trainer_path=Path(game_data['trainer_path']) if game_data.get('trainer_path') else None,
                    cover_image=Path(game_data['cover_image']) if game_data.get('cover_image') else None,
                    play_action=game_data.get('play_action', 'default')
                )
                self.games.append(game)
                
            self.refresh_games()
        except FileNotFoundError:
            pass 

    def delete_game(self, game):
        # Remove game from list
        self.games = [g for g in self.games if g != game]
        # Save changes
        self.save_games()
        # Refresh display
        self.refresh_games() 