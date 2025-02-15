from dataclasses import dataclass
from pathlib import Path

@dataclass
class Game:
    name: str
    direct_launch: bool  # True if game launches directly, False if needs launcher
    launcher_path: Path | None  # Path to launcher if needed
    game_exe_path: Path  # Path to actual game exe (for icon and direct launch)
    mod_launcher_path: Path | None  # Path to mod launcher if exists
    game_directory: Path  # Game's root directory
    trainer_path: Path | None = None  # Path to trainer executable
    cover_image: Path | None = None  # Path to game's cover image
    play_action: str = "default"  # Can be "default", "game", "launcher", "mods", or "trainer" 