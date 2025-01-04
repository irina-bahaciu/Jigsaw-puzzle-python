import pygame
import pygame_gui
import pickle
import os
import random
import sqlite3
import tkinter as tk
from database import insert_user, validate_user, insert_record
from tkinter import Tk, messagebox
from tkinter.filedialog import askopenfilename

# Initialize Pygame and pygame_gui
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
BG_COLOR = (39, 64, 1)
BORDER_COLOR = (242, 159, 5)
FPS = 60

# Game States
LOGIN_SCREEN = "login_screen"
HOME_SCREEN = "home_screen"
GAME_SCREEN = "game_screen"

# Paths
SAVE_PATH = "puzzle_save.txt"  # Save file for puzzle progress

# Initialize pygame_gui Manager
manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

# Create the display window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Jigsaw Puzzle")

# Variables
username = None
timer_running = False
start_time = None
elapsed_time = 0
clock = pygame.time.Clock()
running = True
logged_in = False
game_state = LOGIN_SCREEN
puzzle_completed = False
state_logged = False

# Timer font
timer_font = pygame.font.Font(None, 36)  # Default font, size 36

# Default grid size
ROWS = 3
COLS = 3

# Variables for puzzle settings
BORDER_PADDING = 50
dragging = None  # Track which piece is being dragged
locked_pieces = set()  # Set of locked pieces
piece_positions = []  # Positions of the pieces
pieces = []  # Puzzle pieces
grid = []  # Grid for snapping

# Function to reset the timer
def reset_timer():
    global start_time, elapsed_time, timer_running
    start_time = pygame.time.get_ticks()
    elapsed_time = 0
    timer_running = True

# Function to update the timer
def update_timer():
    global elapsed_time
    if timer_running and start_time is not None:
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000  # Convert to seconds

# Function to render the timer
def render_timer():
    minutes = elapsed_time // 60
    seconds = elapsed_time % 60
    timer_text = f"Time: {minutes:02}:{seconds:02}"
    timer_surface = timer_font.render(timer_text, True, (255, 255, 255))
    screen.blit(timer_surface, (20, 20))

# Function to pause the timer
def pause_timer():
    global timer_running
    timer_running = False

# Function to resume the timer
def resume_timer():
    """Resumes the timer from the saved state."""
    global timer_running, start_time
    if timer_running:
        start_time = pygame.time.get_ticks() - elapsed_time * 1000  # Adjust for elapsed time

def save_timer_state():
    try:
        timer_data = {
            "elapsed_time": elapsed_time,  # Save the elapsed time
            "timer_running": timer_running,  # Save the timer state
        }
        with open("timer_state.pkl", "wb") as timer_file:
            pickle.dump(timer_data, timer_file)
        print("Timer state saved!")
    except Exception as e:
        print(f"Error saving timer state: {e}")

def load_timer_state():
    global elapsed_time, timer_running
    try:
        with open("timer_state.pkl", "rb") as timer_file:
            timer_data = pickle.load(timer_file)
            elapsed_time = timer_data.get("elapsed_time", 0)
            timer_running = timer_data.get("timer_running", False)
            print("Timer state loaded successfully!")
    except FileNotFoundError:
        print("No timer state found!")
        elapsed_time = 0
        timer_running = False
    except Exception as e:
        print(f"Error loading timer state: {e}")

def choose_image():
    Tk().withdraw()  # Hide the root window
    file_path = askopenfilename(
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")],
        title="Select an image for the puzzle"
    )
    return file_path

# Function to scale image to fit within the window
def scale_image_to_fit(image, max_width, max_height):
    image_width, image_height = image.get_size()
    
    # Calculate the scale factor based on the window size
    width_ratio = max_width / image_width
    height_ratio = max_height / image_height
    
    # Use the smaller scale factor to maintain the aspect ratio
    scale_factor = min(width_ratio, height_ratio)
    
    # Calculate new dimensions
    new_width = int(image_width * scale_factor)
    new_height = int(image_height * scale_factor)
    
    # Scale the image
    scaled_image = pygame.transform.scale(image, (new_width, new_height))
    
    return scaled_image

# Update grid size based on dropdown selection
def update_grid_size(selected_option):
    global ROWS, COLS
    sizes = {
        ('2x2', '2x2'): (2, 2),
        ('3x3', '3x3'): (3, 3),
        ('4x4', '4x4'): (4, 4),
        ('5x5', '5x5'): (5, 5),
        ('6x6', '6x6'): (6, 6),
        ('7x7', '7x7'): (7, 7),
        ('8x8', '8x8'): (8, 8),
        ('9x9', '9x9'): (9, 9),
        ('10x10', '10x10'): (10, 10),
    }
    if selected_option in sizes:
        ROWS, COLS = sizes[selected_option]
        generate_pieces()

# Split image into pieces
def split_image(scaled_image, rows, cols):
    piece_width = scaled_image.get_width() // cols
    piece_height = scaled_image.get_height() // rows
    pieces = []
    for row in range(rows):
        for col in range(cols):
            x = col * piece_width
            y = row * piece_height
            piece_surface = scaled_image.subsurface(
                pygame.Rect(x, y, piece_width, piece_height)
            )
            pieces.append(piece_surface)
    return pieces

# Generate puzzle pieces and their random positions
def generate_pieces():
    global pieces, piece_positions, locked_pieces, grid, using_saved_data
    piece_width = scaled_image_width // COLS
    piece_height = scaled_image_height // ROWS
    pieces = split_image(scaled_image, ROWS, COLS)

    # Use saved positions if using_saved_data is True
    if using_saved_data:
        # Do nothing, just keep the loaded positions
        print("Using saved positions for pieces.")
    else:
        # Generate random positions if not loading saved data
        piece_positions = []
        for _ in pieces:
            rand_x = random.randint(0, WINDOW_WIDTH - piece_width)
            rand_y = random.randint(0, WINDOW_HEIGHT - piece_height)
            while border_rect.collidepoint(rand_x, rand_y):
                rand_x = random.randint(0, WINDOW_WIDTH - piece_width)
                rand_y = random.randint(0, WINDOW_HEIGHT - piece_height)
            piece_positions.append([rand_x, rand_y])

    # Generate grid positions based on the loaded ROWS and COLS
    grid = [
        (BORDER_PADDING + col * piece_width, BORDER_PADDING + row * piece_height)
        for row in range(ROWS)
        for col in range(COLS)
    ]

# Save puzzle progress
def save_progress():
    try:
        save_data = {
            "piece_positions": piece_positions,
            "locked_pieces": list(locked_pieces),
            "rows": ROWS,
            "cols": COLS,
            "image_path": IMAGE_PATH, 
            "scaled_image_width": scaled_image_width,
            "scaled_image_height": scaled_image_height,
        }
        with open("saved_progress.pkl", "wb") as save_file:
            pickle.dump(save_data, save_file)
        print("Progress saved!")
    except Exception as e:
        print(f"Error saving progress: {e}")

# Load puzzle progress
def load_progress():
    global piece_positions, locked_pieces, ROWS, COLS, using_saved_data
    global scaled_image, scaled_image_width, scaled_image_height, border_rect, IMAGE_PATH
    try:
        with open("saved_progress.pkl", "rb") as save_file:
            save_data = pickle.load(save_file)

        # Reload the image from the saved path
        saved_image_path = save_data.get("image_path")
        if not saved_image_path or not os.path.exists(saved_image_path):
            raise FileNotFoundError(f"Saved image file not found at {saved_image_path}")
        
        IMAGE_PATH = saved_image_path  # Update IMAGE_PATH
        original_image = pygame.image.load(IMAGE_PATH)

        # Use saved dimensions for scaling
        scaled_image_width = save_data["scaled_image_width"]
        scaled_image_height = save_data["scaled_image_height"]
        scaled_image = pygame.transform.smoothscale(
           original_image, (scaled_image_width, scaled_image_height)
        )
        
        # Update border
        border_rect = pygame.Rect(
            (BORDER_PADDING, BORDER_PADDING, scaled_image_width, scaled_image_height)
        )

        # Load puzzle state
        piece_positions = save_data["piece_positions"]
        locked_pieces = set(save_data["locked_pieces"])
        ROWS = save_data["rows"]
        COLS = save_data["cols"]

        # Set flag to use saved data
        using_saved_data = True

        # Re-generate the grid
        piece_width = scaled_image_width // COLS
        piece_height = scaled_image_height // ROWS
        grid[:] = [
            (BORDER_PADDING + col * piece_width, BORDER_PADDING + row * piece_height)
            for row in range(ROWS)
            for col in range(COLS)
        ]

        # Generate pieces with existing positions
        generate_pieces()

        print("Progress loaded successfully!")
        return True
    except FileNotFoundError:
        print("No saved progress found!")
    except Exception as e:
        print(f"Error loading progress: {e}")
    return False

# Create in-game buttons
def create_in_game_buttons(manager):
    global save_button, reset_button, back_button
    save_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((1100, 50), (150, 35)), 
        text='Save progress', 
        manager=manager
    )
    reset_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((1100, 100), (150, 35)),
        text='Reset game', 
        manager=manager
    )
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((1100, 150), (150, 35)), 
        text='Back to menu', 
        manager=manager
    )
    return save_button, reset_button, back_button

# Function to check if the puzzle is complete
def is_puzzle_complete():
    for i, (piece_position) in enumerate(piece_positions):
        # Check if each piece is placed correctly in the grid position
        grid_x, grid_y = grid[i]
        if piece_position != [grid_x, grid_y]:
            return False
    return True

# Add a font for the congratulatory message
font = pygame.font.SysFont("Arial", 40)

# Function to display the congratulatory message
def display_congratulations():
    # Create a surface for the congratulations message
    congrats_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    congrats_surface.set_alpha(200)  # Set transparency
    congrats_surface.fill((0, 0, 0))  # Fill with black color

    # Render the congratulations text
    font = pygame.font.Font(None, 74)
    text_surface = font.render("Congratulations!", True, (255, 255, 255))
    text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
    congrats_surface.blit(text_surface, text_rect)

    # Blit the congratulations surface onto the main screen
    screen.blit(congrats_surface, (0, 0))
    pygame.display.update()

    # Wait for a few seconds to display the message
    pygame.time.wait(3000)

# Function to show error message
def show_error_message(message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showerror("Error", message)
    root.destroy()

# Create UI elements for registration and login
def create_login_ui():
    global title_label, username_label, password_label, username_input, password_input, signup_button, login_button, no_authentication_button
    title_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((250, 50), (300, 50)), text="Jigsaw Puzzle", manager=manager,)
    username_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, 200), (300, 50)), text="Username", manager=manager,)
    password_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((50, 270), (300, 50)), text="Password", manager=manager,)
    username_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((250, 200), (300, 50)), manager=manager)
    password_input = pygame_gui.elements.UITextEntryLine(relative_rect=pygame.Rect((250, 270), (300, 50)), manager=manager)
    password_input.set_text_hidden(True)
    signup_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((250, 340), (100, 50)), text='Sign Up', manager=manager)
    login_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((450, 340), (100, 50)), text='Log In', manager=manager)
    no_authentication_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((300, 400), (200, 50)), text='No Authentication', manager=manager)
    #return username_input, password_input, signup_button, login_button, no_authentication_button

# Main menu elements
def create_home_screen_ui():
    global title_label, dropdown_menu, start_button, continue_button, exit_button
    title_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((250, 50), (300, 50)),
        text="Jigsaw Puzzle",
        manager=manager,
    )
    dropdown_menu = pygame_gui.elements.UIDropDownMenu(
        options_list=["2x2", "3x3", "4x4", "5x5", "6x6", "7x7", "8x8", "9x9", "10x10"],
        starting_option="2x2",  # Default is 2x2
        relative_rect=pygame.Rect((250, 150), (300, 50)),
        manager=manager,
    )
    start_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((250, 250), (300, 50)),
        text="Start New Game",
        manager=manager,
    )
    continue_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((250, 350), (300, 50)),
        text="Continue Game",
        manager=manager,
    )
    exit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((250, 450), (300, 50)),
        text="Exit",
        manager=manager,
    )
    #return title_label, dropdown_menu, start_button, continue_button, exit_button

create_login_ui()

# Main loop
running = True
in_game = False  # Whether the game is in progress
in_game_buttons = None  # Buttons for the in-game screen

while running:
    time_delta = clock.tick(FPS) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if in_game:
            update_timer()  # Update the timer when the game is active

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                for i in range(len(piece_positions) - 1, -1, -1):  # Iterate backwards
                    if i in locked_pieces:
                        continue
                    x, y = piece_positions[i]
                    piece_width = scaled_image_width // COLS
                    piece_height = scaled_image_height // ROWS
                    if x <= mouse_x <= x + piece_width and y <= mouse_y <= y + piece_height:
                        dragging = i
                        break

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging is not None:
                    piece_x, piece_y = piece_positions[dragging]
                    grid_x, grid_y = grid[dragging]
                    if abs(piece_x - grid_x) < 10 and abs(piece_y - grid_y) < 10:
                        piece_positions[dragging] = [grid_x, grid_y]
                        locked_pieces.add(dragging)
                    dragging = None

            elif event.type == pygame.MOUSEMOTION and dragging is not None:
                mouse_x, mouse_y = event.pos
                piece_width = scaled_image_width // COLS
                piece_height = scaled_image_height // ROWS
                piece_positions[dragging] = [mouse_x - piece_width // 2, mouse_y - piece_height // 2]

        manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:

                if game_state == LOGIN_SCREEN:
                    if event.ui_element == signup_button:
                        username = username_input.get_text()
                        password = password_input.get_text()
                        if not insert_user(username, password):
                            show_error_message(f"Error: Username {username} is already in use.")
                        else:
                            print(f"User {username} registered.")
                    elif event.ui_element == login_button:
                        username = username_input.get_text()
                        password = password_input.get_text()
                        if validate_user(username, password):
                            print(f"User {username} logged in.")
                            logged_in = True
                            game_state = HOME_SCREEN
                            # Remove the input UI elements after login
                            username_label.kill()
                            password_label.kill()
                            username_input.kill()
                            password_input.kill()
                            signup_button.kill()
                            login_button.kill()
                            no_authentication_button.kill()
                            create_home_screen_ui()
                        else:
                            show_error_message(f"Error: Invalid user or password.")
                    elif event.ui_element == no_authentication_button:
                        print("No authentication selected.")
                        logged_in = False
                        game_state = HOME_SCREEN
                        username_label.kill()
                        password_label.kill()
                        username_input.kill()
                        password_input.kill()
                        signup_button.kill()
                        login_button.kill()
                        no_authentication_button.kill()
                        create_home_screen_ui()
                
                elif game_state == HOME_SCREEN:
                    if event.ui_element == exit_button:
                        pygame.quit()
                        running = False
                        exit()

                    if event.ui_element == continue_button:
                        if load_progress():
                            game_state = GAME_SCREEN
                            load_timer_state()
                            resume_timer()
                            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                            WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
                            manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
                            border_rect = pygame.Rect(
                                (BORDER_PADDING, BORDER_PADDING, scaled_image_width, scaled_image_height)
                            )
                            update_grid_size(dropdown_menu.selected_option)

                            in_game = True
                            title_label.kill()
                            continue_button.kill()
                            exit_button.kill()
                            dropdown_menu.kill()

                            in_game_buttons = create_in_game_buttons(manager)
                        else:
                            print("No saved progress found!")

                    if event.ui_element == start_button:
                        IMAGE_PATH = choose_image()

                        if IMAGE_PATH and os.path.exists(IMAGE_PATH):
                            original_image = pygame.image.load(IMAGE_PATH)
                            scaled_image = scale_image_to_fit(
                                original_image,
                                WINDOW_WIDTH - 2 * BORDER_PADDING,
                                WINDOW_HEIGHT - 2 * BORDER_PADDING
                            )
                            game_state = GAME_SCREEN
                            # Update the scaled image dimensions
                            scaled_image_width, scaled_image_height = scaled_image.get_size()

                            # Adjust the border rectangle
                            border_rect = pygame.Rect(
                                (BORDER_PADDING, BORDER_PADDING, scaled_image_width, scaled_image_height)
                            )

                            using_saved_data = False  # Starting a new game, use random positions
                            piece_positions = []  # Reset piece positions
                            locked_pieces = set()  # Reset locked pieces
                            generate_pieces()  # Generate a new set of pieces
                            reset_timer()
                            
                            # Fullscreen mode
                            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                            WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
                            manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
                            border_rect = pygame.Rect(
                                (BORDER_PADDING, BORDER_PADDING, scaled_image_width, scaled_image_height)
                            )
                            update_grid_size(dropdown_menu.selected_option)
                            
                            in_game = True
                            title_label.kill()
                            start_button.kill()
                            exit_button.kill()
                            dropdown_menu.kill()

                            in_game_buttons = create_in_game_buttons(manager)

                elif game_state == GAME_SCREEN:
                    if in_game_buttons: 
                        save_button, reset_button, back_button = in_game_buttons
                        
                        if event.ui_element == save_button:
                            save_progress()
                            print("Progress saved!")

                        if event.ui_element == reset_button:
                            using_saved_data = False  # Starting a new game, use random positions
                            piece_positions = []  # Reset piece positions
                            locked_pieces = set()
                            generate_pieces()  # Generate a new set of pieces
                            reset_timer()
                            print("Puzzle reset!")

                        if event.ui_element == back_button:
                            save_timer_state()
                            game_state = HOME_SCREEN
                            pause_timer()  # Pause the timer
                            using_saved_data = False  # Reset saved data usage flag
                            save_button.kill() 
                            reset_button.kill()
                            back_button.kill()
                            create_home_screen_ui()
                            for button in in_game_buttons:
                                button.kill()
                            in_game_buttons = None

    manager.update(time_delta)

    screen.fill(BG_COLOR)

    if game_state == LOGIN_SCREEN:
        manager.draw_ui(screen)
    elif game_state == HOME_SCREEN:
        manager.draw_ui(screen)
    elif game_state == GAME_SCREEN:
        # Transition to the home screen or main game logic
        render_timer()  # Render the timer on the screen
        pygame.draw.rect(screen, BORDER_COLOR, border_rect, 2)
        piece_width = scaled_image_width // COLS
        piece_height = scaled_image_height // ROWS
        for i, (piece, (x, y)) in enumerate(zip(pieces, piece_positions)):
            if i != dragging:
                screen.blit(piece, (x, y))
        if dragging is not None:
            screen.blit(pieces[dragging], piece_positions[dragging])
            
        # Check if the puzzle is complete
        if is_puzzle_complete() and not puzzle_completed:
            print("Puzzle is complete. Saving progress and inserting record.")
            display_congratulations()
            save_progress()
            timer_running = False
            puzzle_completed = True
            state_logged = True

            # Automatically save the record if logged in
            if logged_in:
                puzzle_image = IMAGE_PATH  # Use the IMAGE_PATH variable
                completion_time = elapsed_time  # Replace with actual completion time
                print(f"Inserting record: username={username}, puzzle_image={puzzle_image}, completion_time={completion_time}")
                insert_record(username, puzzle_image, completion_time)
                print("Record saved.")
        else:
            if not puzzle_completed and not state_logged:
                print("Puzzle not complete or already completed.")
                state_logged = True  # Set the flag to indicate state has been logged


    manager.draw_ui(screen)
    pygame.display.update()

pygame.quit()
