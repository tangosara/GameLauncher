import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import subprocess

class GameLauncher:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Game Launcher")
        self.window.geometry("650x600")
        
        # Set up dark theme
        self.window.configure(bg='#2b2b2b')
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure colors for ttk widgets
        style.configure('TFrame', background='#2b2b2b')
        style.configure('TButton', 
                       background='#3b3b3b',
                       foreground='white',
                       borderwidth=1,
                       focuscolor='none',
                       padding=5)
        style.map('TButton',
                  background=[('active', '#404040')])
        style.configure('TLabel', 
                       background='#2b2b2b',
                       foreground='white')
        style.configure('TEntry', 
                       fieldbackground='#3b3b3b',
                       foreground='white',
                       insertcolor='white')
        
        # Dictionary to store game configurations
        self.games = {}
        
        # Define available tags
        self.tags = ["All", "Racing", "Open World", "Lightweight", "Tools", "Gacha", "Emulators", "Comfort"]
        self.current_tag = "All"
        
        # Create tag buttons at the top
        self.tag_frame = ttk.Frame(self.window)
        self.tag_frame.pack(fill=tk.X, padx=10, pady=5)
        
        for tag in self.tags:
            btn = ttk.Button(self.tag_frame, text=tag,
                           command=lambda t=tag: self.filter_by_tag(t))
            btn.pack(side=tk.LEFT, padx=2, pady=2)
        
        # Create main frame with scrollbar
        self.main_frame = ttk.Frame(self.window)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure grid
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)
        self.scrollable_frame.grid_columnconfigure(2, weight=1)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack scrollbar components
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create menu
        self.menu_bar = tk.Menu(self.window)
        self.window.config(menu=self.menu_bar)
        
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Add Game", command=self.add_game)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.window.quit)
        
        # Load existing games
        self.load_games()
        
        # Update canvas colors
        self.canvas.configure(bg='#2b2b2b')
        self.scrollable_frame.configure(style='TFrame')
        
    def add_game(self):
        dialog = GameConfigDialog(self.window)
        if dialog.result:
            name, game_exe, launcher_exe, directory, tags = dialog.result
            if name == "DELETE":  # Handle deletion
                return
            self.games[name] = {
                'game_exe': game_exe,
                'launcher_exe': launcher_exe,
                'directory': directory,
                'tags': tags
            }
            self.save_games()
            self.filter_by_tag(self.current_tag)
            
    def create_game_button(self, game_name):
        # Calculate grid position (3 columns)
        num_buttons = len(self.scrollable_frame.winfo_children())
        row = num_buttons // 4
        col = num_buttons % 4
        
        # Create frame for the game button
        frame = ttk.Frame(self.scrollable_frame)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights for the frame
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame.grid_columnconfigure(1, weight=1)
        self.scrollable_frame.grid_columnconfigure(2, weight=1)
        
        # Main game button
        btn = ttk.Button(frame, text=game_name, 
                         command=lambda: self.show_launch_options(game_name))
        btn.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def show_launch_options(self, game_name):
        game = self.games[game_name]
        dialog = tk.Toplevel(self.window)
        dialog.title(f"Launch {game_name}")
        dialog.geometry("300x250")  # Made slightly taller for the extra button
        dialog.configure(bg='#2b2b2b')  # Maintain dark theme
        
        ttk.Button(dialog, text="Launch Game", 
                  command=lambda: self.launch_exe(game['game_exe'], dialog)).pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(dialog, text="Launch Launcher", 
                  command=lambda: self.launch_exe(game['launcher_exe'], dialog)).pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(dialog, text="Open Directory", 
                  command=lambda: self.open_directory(game['directory'], dialog)).pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(dialog, text="Edit directories", 
                  command=lambda: [dialog.destroy(), self.edit_game(game_name)]).pack(fill=tk.X, padx=20, pady=5)
        
        ttk.Button(dialog, text="Cancel", 
                  command=dialog.destroy).pack(fill=tk.X, padx=20, pady=5)
        
    def launch_exe(self, path, dialog):
        if path:
            try:
                # Try to launch normally first
                if os.name == 'nt':  # Windows systems
                    subprocess.Popen(f'"{path}"', shell=True)
                else:
                    subprocess.Popen([path])
                dialog.destroy()
            except PermissionError:
                # If permission denied, try to elevate
                try:
                    if os.name == 'nt':
                        # Use cmd /c to properly handle paths with spaces
                        cmd = f'powershell.exe Start-Process "{path}" -Verb RunAs'
                        subprocess.Popen(cmd, shell=True)
                    else:
                        subprocess.Popen(['sudo', path])
                    dialog.destroy()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to launch with elevation: {str(e)}\n\nTry running the launcher as administrator.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to launch: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No executable path specified")
            
    def open_directory(self, path, dialog):
        if path:
            try:
                os.startfile(path)
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open directory: {str(e)}")
        else:
            messagebox.showwarning("Warning", "No directory specified")
            
    def save_games(self):
        with open('games.json', 'w') as f:
            json.dump(self.games, f)
            
    def load_games(self):
        try:
            with open('games.json', 'r') as f:
                self.games = json.load(f)
                for game_name in self.games:
                    self.create_game_button(game_name)
        except FileNotFoundError:
            pass
        
    def edit_game(self, game_name):
        current_config = self.games[game_name]
        dialog = GameConfigDialog(self.window, 
                                name=game_name,
                                game_exe=current_config['game_exe'],
                                launcher_exe=current_config['launcher_exe'],
                                directory=current_config['directory'],
                                tags=current_config.get('tags', []))
        
        if dialog.result:
            # Remove old entry
            del self.games[game_name]
            
            # Add updated entry
            new_name, game_exe, launcher_exe, directory, tags = dialog.result
            self.games[new_name] = {
                'game_exe': game_exe,
                'launcher_exe': launcher_exe,
                'directory': directory,
                'tags': tags
            }
            
            # Save changes and refresh display
            self.save_games()
            self.filter_by_tag(self.current_tag)

    def filter_by_tag(self, tag):
        self.current_tag = tag
        # Clear current display
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Show games with selected tag
        for game in self.games:
            if tag == "All" or tag in self.games[game].get('tags', []):
                self.create_game_button(game)

class GameConfigDialog:
    def __init__(self, parent, name='', game_exe='', launcher_exe='', directory='', tags=None):
        self.result = None
        tags = tags or []
        
        dialog = tk.Toplevel(parent)
        dialog.title("Edit Game" if name else "Add Game")
        dialog.geometry("400x600")  # Changed from 500 to 600 height
        dialog.configure(bg='#2b2b2b')
        
        ttk.Label(dialog, text="Game Name:").pack(padx=20, pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.insert(0, name)  # Pre-fill existing name
        name_entry.pack(fill=tk.X, padx=20)
        
        game_exe_var = tk.StringVar(value=game_exe)  # Pre-fill existing values
        launcher_exe_var = tk.StringVar(value=launcher_exe)
        directory_var = tk.StringVar(value=directory)
        
        ttk.Label(dialog, text="Game Executable:").pack(padx=20, pady=5)
        ttk.Entry(dialog, textvariable=game_exe_var, state='readonly').pack(fill=tk.X, padx=20)
        ttk.Button(dialog, text="Browse", 
                  command=lambda: self.browse_file(game_exe_var)).pack(pady=5)
        
        ttk.Label(dialog, text="Launcher Executable:").pack(padx=20, pady=5)
        ttk.Entry(dialog, textvariable=launcher_exe_var, state='readonly').pack(fill=tk.X, padx=20)
        ttk.Button(dialog, text="Browse", 
                  command=lambda: self.browse_file(launcher_exe_var)).pack(pady=5)
        
        ttk.Label(dialog, text="Game Directory:").pack(padx=20, pady=5)
        ttk.Entry(dialog, textvariable=directory_var, state='readonly').pack(fill=tk.X, padx=20)
        ttk.Button(dialog, text="Browse", 
                  command=lambda: self.browse_directory(directory_var)).pack(pady=5)
        
        # Add tag selection
        ttk.Label(dialog, text="Tags:").pack(padx=20, pady=5)
        tag_frame = ttk.Frame(dialog)
        tag_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tag_vars = {}
        for tag in ["Racing", "Open World", "Lightweight", "Tools", "Gacha", "Emulators", "Comfort"]:
            var = tk.BooleanVar(value=tag in tags)
            tag_vars[tag] = var
            cb = ttk.Checkbutton(tag_frame, text=tag, variable=var)
            cb.pack(anchor=tk.W)
        
        # Add Delete button if editing an existing entry
        if name:
            ttk.Button(dialog, text="Delete", 
                      command=lambda: self.delete_entry(dialog, name_entry.get().strip())).pack(pady=5)
        
        def save():
            if name_entry.get().strip():
                selected_tags = [tag for tag, var in tag_vars.items() if var.get()]
                self.result = (name_entry.get().strip(), 
                             game_exe_var.get(), 
                             launcher_exe_var.get(), 
                             directory_var.get(),
                             selected_tags)
                dialog.destroy()
            else:
                messagebox.showwarning("Warning", "Please enter a game name")
                
        ttk.Button(dialog, text="Save", command=save).pack(pady=20)
        
        dialog.transient(parent)
        dialog.grab_set()
        parent.wait_window(dialog)
    
    def delete_entry(self, dialog, name):
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?"):
            self.result = ("DELETE", "", "", "")  # Special flag for deletion
            dialog.destroy()
            
    def browse_file(self, var):
        filename = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
        if filename:
            var.set(filename)
            
    def browse_directory(self, var):
        directory = filedialog.askdirectory()
        if directory:
            var.set(directory)

if __name__ == "__main__":
    app = GameLauncher()
    app.window.mainloop()
