import pygame
import sys
import subprocess
import os

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WINDOW_TITLE = "Pygame Game Launcher"

# Colors (feel free to customize)
COLOR_BACKGROUND = (25, 25, 35)       # Dark bluish-grey
COLOR_BUTTON = (50, 50, 70)          # Slightly lighter grey-blue
COLOR_BUTTON_HOVER = (80, 80, 100)    # Lighter hover color
COLOR_TEXT = (230, 230, 230)         # Light grey/off-white
COLOR_TITLE = (150, 180, 220)       # Light blue for title
COLOR_ERROR = (255, 100, 100)       # Red for errors

# Font
try:
    pygame.font.init()
    # Try a nicer system font if available, otherwise default
    TITLE_FONT_NAME = pygame.font.match_font('consolas, dejavusansmono, consolas, ubuntu mono, monospace')
    BUTTON_FONT_NAME = pygame.font.match_font('consolas, dejavusansmono, consolas, ubuntu mono, monospace')
    if TITLE_FONT_NAME is None: TITLE_FONT_NAME = pygame.font.get_default_font()
    if BUTTON_FONT_NAME is None: BUTTON_FONT_NAME = pygame.font.get_default_font()
    TITLE_FONT_SIZE = 48
    BUTTON_FONT_SIZE = 28
    MESSAGE_FONT_SIZE = 18
    TITLE_FONT = pygame.font.Font(TITLE_FONT_NAME, TITLE_FONT_SIZE)
    BUTTON_FONT = pygame.font.Font(BUTTON_FONT_NAME, BUTTON_FONT_SIZE)
    MESSAGE_FONT = pygame.font.Font(BUTTON_FONT_NAME, MESSAGE_FONT_SIZE) # Use button font for messages too
except Exception as e:
    print(f"Font loading error: {e}. Using default fonts.")
    pygame.font.init() # Ensure font module is initialized even if specific font fails
    TITLE_FONT = pygame.font.Font(None, 55)
    BUTTON_FONT = pygame.font.Font(None, 35)
    MESSAGE_FONT = pygame.font.Font(None, 22)


# --- Game Definitions ---
# IMPORTANT:
# - 'folder': The name of the subfolder containing the game.
# - 'file': The name of the main Python script to run *inside* that folder.
# - 'name': The display name for the button.
#
# Example File Structure:
# Your_Project_Folder/
# |--- launcher.py  (This script)
# |--- SpaceShooter/
# |    |--- game.py        <-- The main script for Space Shooter
# |    |--- assets/
# |    |    |--- player.png
# |    |    +--- ...
# |--- Platformer/
# |    |--- main.py        <-- The main script for Platformer
# |    |--- levels/
# |    |    +--- ...
# |    +--- ...
# |--- PuzzleMania/
# |    |--- puzzle_game.py <-- The main script for Puzzle Mania
# |    +--- ...
# +--- RetroRacer/
#      |--- racer.py       <-- The main script for Retro Racer
#      +--- ...

GAMES = [
    {"folder": "WallRunner", "file": "ga.py", "name": "Wall Runner"},
    {"folder": "MuseDash", "file": "fin.py", "name": "Rhytm Runner"},
    {"folder": "ZombieSurvival", "file": "game.py", "name": "Zombie Surviver"},
    {"folder": "PingPong", "file": "racer.py", "name": "Ping Pong"},
    # Add more games here following the same structure
]

# --- Button Class ---
class Button:
    def __init__(self, x, y, width, height, text, game_folder, game_file): # Added game_folder, game_file
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.game_folder = game_folder # Store the folder
        self.game_file = game_file     # Store the file within the folder
        self.is_hovered = False
        self.text_surface = BUTTON_FONT.render(text, True, COLOR_TEXT)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface):
        bg_color = COLOR_BUTTON_HOVER if self.is_hovered else COLOR_BUTTON
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        surface.blit(self.text_surface, self.text_rect)

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def handle_click(self):
        if self.is_hovered:
            full_path = os.path.join(self.game_folder, self.game_file)
            print(f"Attempting to launch: {full_path} from folder {self.game_folder}")
            # Pass both folder and file to the launch function
            return launch_game(self.game_folder, self.game_file)
        return None

# --- Game Launch Function ---
def launch_game(game_folder, game_file):
    """
    Launches the specified python game file, setting the
    working directory to the game's folder.
    """
    # Construct the full path to the script relative to the launcher's location
    script_path = os.path.join(game_folder, game_file)
    # The game's directory (will be used as the CWD for the subprocess)
    game_directory = game_folder

    # Check if the directory exists
    if not os.path.isdir(game_directory):
        print(f"Error: Game directory not found - {game_directory}")
        return f"Error: Directory '{game_directory}' not found."

    # Check if the script file exists within the directory
    if not os.path.exists(script_path):
        print(f"Error: Script file not found - {script_path}")
        return f"Error: Script '{game_file}' not found in '{game_folder}'."

    try:
        print(f"Launching '{game_file}' from directory '{game_directory}'...")
        # Use sys.executable to ensure the same Python interpreter is used
        # Use 'cwd' to set the working directory for the launched game
        # Pass only the script *filename* as the argument, because cwd handles the path
        process = subprocess.Popen(
            [sys.executable, game_file], # Command to run (python your_game_script.py)
            cwd=game_directory           # Set the Current Working Directory for the game
        )

        print(f"Launched '{script_path}'. Process ID: {process.pid}")
        # Return a user-friendly success message
        return f"Launched '{os.path.basename(game_folder)}/{game_file}'."
    except Exception as e:
        print(f"Error launching {script_path}: {e}")
        # Return a user-friendly error message
        return f"Error launching '{os.path.basename(game_folder)}/{game_file}'."

# --- Main Function ---
def main():
    pygame.init()
    # Determine the base directory where the launcher script is located
    # This helps ensure relative paths for game folders work correctly
    # even if the script is run from a different directory.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Change the current working directory to the script's directory
    # This makes relative paths in GAMES dictionary work as expected.
    os.chdir(base_dir)
    print(f"Launcher running from: {base_dir}")


    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    clock = pygame.time.Clock()

    # Create Buttons
    buttons = []
    button_width = 350
    button_height = 60
    button_spacing = 25 # Vertical space between buttons
    total_button_height = (button_height + button_spacing) * len(GAMES) - button_spacing
    start_y = (SCREEN_HEIGHT - total_button_height) // 2 + 50 # Start drawing below the title

    for i, game in enumerate(GAMES):
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = start_y + i * (button_height + button_spacing)
        # Pass game folder and file to the Button constructor
        buttons.append(Button(button_x, button_y, button_width, button_height,
                              game["name"], game["folder"], game["file"]))

    # Title Surface
    title_surface = TITLE_FONT.render(WINDOW_TITLE, True, COLOR_TITLE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, start_y // 2)) # Position title above buttons

    message = "" # To display status messages (e.g., launched, error)
    message_timer = 0 # How long to display the message

    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        # --- Event Handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left mouse button
                    for button in buttons:
                        status = button.handle_click()
                        if status: # If a button was clicked
                            message = status
                            message_timer = pygame.time.get_ticks() + 3000 # Show message for 3 seconds
                            break # Stop checking other buttons

        # --- Update ---
        for button in buttons:
            button.check_hover(mouse_pos)

        # Clear message if timer expires
        if message and pygame.time.get_ticks() > message_timer:
            message = ""
            message_timer = 0

        # --- Drawing ---
        screen.fill(COLOR_BACKGROUND)

        # Draw Title
        screen.blit(title_surface, title_rect)

        # Draw Buttons
        for button in buttons:
            button.draw(screen)

        # Draw Status Message
        if message:
            msg_color = COLOR_ERROR if "Error" in message else COLOR_TEXT
            message_surface = MESSAGE_FONT.render(message, True, msg_color)
            # Position message at the bottom center
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            screen.blit(message_surface, message_rect)


        pygame.display.flip() # Update the full screen
        clock.tick(60) # Limit frame rate

    pygame.quit()
    sys.exit()

# --- Run the UI ---
if __name__ == '__main__':
    main()