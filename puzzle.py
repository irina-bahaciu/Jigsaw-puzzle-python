import pygame
import pygame_gui
import os
import random

# Initialize Pygame and pygame_gui
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
BG_COLOR = (39, 64, 1)
GREEN_BORDER_COLOR = (242, 159, 5)
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

# Dropdown menu for grid selection
dropdown_menu = pygame_gui.elements.UIDropDownMenu(
    options_list=["3x3", "4x4", "5x5", "6x6", "7x7", "8x8", "9x9", "10x10"],
    starting_option="3x3",  # Default is 3x3
    relative_rect=pygame.Rect((250, 150), (300, 50)),
    manager=manager,
)

# Update grid size based on dropdown selection
def update_grid_size(selected_option):
    global ROWS, COLS
    sizes = {
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

# Create in-game buttons
def create_in_game_buttons(manager):
    button_width = 150
    button_height = 35

    exit_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((1100, 50), (button_width, button_height)),
        text="Exit",
        manager=manager,
    )
    save_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((1100, 100), (button_width, button_height)),
        text="Save Progress",
        manager=manager,
    )
    reset_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((1100, 150), (button_width, button_height)),
        text="Reset Puzzle",
        manager=manager,
    )
    back_button = pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((1100, 200), (button_width, button_height)),
        text="Back to Start",
        manager=manager,
    )

    return exit_button, save_button, reset_button, back_button

# Set the game state
in_game = False
in_game_buttons = None

# Main menu elements
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
exit_button = pygame_gui.elements.UIButton(
    relative_rect=pygame.Rect((250, 350), (300, 50)),
    text="Exit",
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
                for i in range(len(piece_positions) - 1, -1, -1):  # Iterate backwards
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
            if event.user_type == pygame_gui.UI_BUTTON_PRESSED:
                if event.ui_element == start_button:
                    # Fullscreen mode
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    WINDOW_WIDTH, WINDOW_HEIGHT = screen.get_size()
                    manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))
                    green_border_rect = pygame.Rect(
                        (BORDER_PADDING, BORDER_PADDING, image_width, image_height)
                    )
                    update_grid_size(dropdown_menu.selected_option)
                    generate_pieces()
                    in_game = True

                    # Remove main menu elements
                    title_label.kill()
                    dropdown_menu.kill()
                    start_button.kill()
                    exit_button.kill()

                    # Create in-game buttons
                    in_game_buttons = create_in_game_buttons(manager)

                if in_game_buttons:
                    exit_button, save_button, reset_button, back_button = in_game_buttons

                    if event.ui_element == exit_button:
                        pygame.quit()
                        exit()

                    if event.ui_element == save_button:
                        with open("puzzle_save.txt", "w") as file:
                            for pos in piece_positions:
                                file.write(f"{pos[0]},{pos[1]}\n")
                        print("Progress saved!")

                    if event.ui_element == reset_button:
                        generate_pieces()
                        print("Puzzle reset!")

                    if event.ui_element == back_button:
                        in_game = False
                        # Restore main menu
                        title_label = pygame_gui.elements.UILabel(
                            relative_rect=pygame.Rect((250, 50), (300, 50)),
                            text="Jigsaw Puzzle",
                            manager=manager,
                        )
                        dropdown_menu = pygame_gui.elements.UIDropDownMenu(
                            options_list=["3x3", "4x4", "5x5", "6x6", "7x7", "8x8", "9x9", "10x10"],
                            starting_option="3x3",
                            relative_rect=pygame.Rect((250, 150), (300, 50)),
                            manager=manager,
                        )
                        start_button = pygame_gui.elements.UIButton(
                            relative_rect=pygame.Rect((250, 250), (300, 50)),
                            text="Start Game",
                            manager=manager,
                        )
                        exit_button = pygame_gui.elements.UIButton(
                            relative_rect=pygame.Rect((250, 350), (300, 50)),
                            text="Exit",
                            manager=manager,
                        )
                        # Remove in-game buttons
                        for button in in_game_buttons:
                            button.kill()
                        in_game_buttons = None

    manager.update(time_delta)

    screen.fill(BG_COLOR)

    if in_game:
        pygame.draw.rect(screen, GREEN_BORDER_COLOR, green_border_rect, 2)
        piece_width = image_width // COLS
        piece_height = image_height // ROWS
        for i, (piece, (x, y)) in enumerate(zip(pieces, piece_positions)):
            if i != dragging:
                screen.blit(piece, (x, y))
        if dragging is not None:
            screen.blit(pieces[dragging], piece_positions[dragging])

    manager.draw_ui(screen)

    pygame.display.update()

pygame.quit()
