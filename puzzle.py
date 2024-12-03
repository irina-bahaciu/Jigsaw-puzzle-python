import pygame
import pygame_gui
import os
import random

# Initialize Pygame and pygame_gui
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
BG_COLOR = (255, 255, 255)  # White background
GREEN_BORDER_COLOR = (0, 255, 0)  # Green border
FPS = 60

# Paths
IMAGE_PATH = "pic.jpg"
if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError(f"Image file not found at {IMAGE_PATH}")

# Initialize pygame_gui Manager
manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

# Create the display window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Jigsaw Puzzle")

# Clock for FPS
clock = pygame.time.Clock()

ROWS = 3
COLS = 3

# Variables for puzzle settings  # Default grid size
BORDER_PADDING = 50
dragging = None  # Track which piece is being dragged
locked_pieces = set()  # Set of locked pieces
piece_positions = []  # Positions of the pieces
pieces = []  # Puzzle pieces
grid = []  # Grid for snapping

# Load image
original_image = pygame.image.load(IMAGE_PATH)
image_width, image_height = original_image.get_size()

# Ensure the window is large enough
WINDOW_WIDTH = max(WINDOW_WIDTH, image_width + BORDER_PADDING * 2)
WINDOW_HEIGHT = max(WINDOW_HEIGHT, image_height + BORDER_PADDING * 2)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

# Green border rectangle
green_border_rect = pygame.Rect(
    (BORDER_PADDING, BORDER_PADDING, image_width, image_height)
)

# Dropdown menu initialization (above functions)
dropdown_menu = pygame_gui.elements.UIDropDownMenu(
    options_list=["3x3", "4x4", "5x5"],
    starting_option="3x3",  # Default is 3x3
    relative_rect=pygame.Rect((250, 150), (300, 50)),
    manager=manager,
)
# Update grid size based on dropdown selection
def update_grid_size(selected_option):
    global ROWS
    global COLS
    if selected_option == ('3x3', '3x3'):
        ROWS = 3
        COLS = 3
    if selected_option == ('4x4', '4x4'):
        ROWS = 4
        COLS = 4
    elif selected_option == ('5x5', '5x5'):
        ROWS = 5
        COLS = 5
    
    generate_pieces()

# Split image into pieces
def split_image(image, rows, cols):
    piece_width = image.get_width() // cols
    piece_height = image.get_height() // rows
    pieces = []
    for row in range(rows):
        for col in range(cols):
            x = col * piece_width
            y = row * piece_height
            piece_surface = image.subsurface(
                pygame.Rect(x, y, piece_width, piece_height)
            )
            pieces.append(piece_surface)
    return pieces

# Generate puzzle pieces and their random positions
def generate_pieces():
    global pieces, piece_positions, locked_pieces, grid
    piece_width = image_width // COLS
    piece_height = image_height // ROWS
    pieces = split_image(original_image, ROWS, COLS)
    piece_positions = []
    for _ in pieces:
        rand_x = random.randint(0, WINDOW_WIDTH - piece_width)
        rand_y = random.randint(0, WINDOW_HEIGHT - piece_height)
        while green_border_rect.collidepoint(rand_x, rand_y):
            rand_x = random.randint(0, WINDOW_WIDTH - piece_width)
            rand_y = random.randint(0, WINDOW_HEIGHT - piece_height)
        piece_positions.append([rand_x, rand_y])
    
    grid = [
        (BORDER_PADDING + col * piece_width, BORDER_PADDING + row * piece_height)
        for row in range(ROWS)
        for col in range(COLS)
    ]
    locked_pieces = set()

# Set the game state
in_game = False

# Create other UI elements
title_label = pygame_gui.elements.UILabel(
    relative_rect=pygame.Rect((250, 50), (300, 50)),
    text="Jigsaw Puzzle",
    manager=manager,
)

start_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((250, 250), (300, 50)),
    text="Start Game",
    manager=manager,
)

# Main loop
running = True

while running:
    time_delta = clock.tick(FPS) / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if in_game:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = event.pos
                for i in range(len(piece_positions) -1, -1, -1): #iterate backwards
                    if i in locked_pieces:
                        continue
                    x, y = piece_positions[i]
                    piece_width = image_width // COLS
                    piece_height = image_height // ROWS
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
                piece_width = image_width // COLS
                piece_height = image_height // ROWS
                piece_positions[dragging] = [mouse_x - piece_width // 2, mouse_y - piece_height // 2]

        manager.process_events(event)

        if event.type == pygame.USEREVENT:
            if event.user_type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
                if event.ui_element == dropdown_menu:
                    update_grid_size(dropdown_menu.selected_option)

            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    update_grid_size(dropdown_menu.selected_option)
                    in_game = True

                    # Remove UI elements from the screen
                    title_label.kill()
                    dropdown_menu.kill()
                    start_button.kill()

    if in_game:
        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, GREEN_BORDER_COLOR, green_border_rect, 3)
        for i, piece in enumerate(pieces):
            x, y = piece_positions[i]
            screen.blit(piece, (x, y))
    else:
        screen.fill(BG_COLOR)

    manager.update(time_delta)
    manager.draw_ui(screen)
    pygame.display.flip()

pygame.quit()
