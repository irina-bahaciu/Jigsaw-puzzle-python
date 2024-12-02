import pygame
import os
import random

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600  # Adjust the window size as needed
BG_COLOR = (255, 255, 255)  # White background
GREEN_BORDER_COLOR = (0, 255, 0)  # Green border

# Grid size
ROWS, COLS = 3, 3  # Puzzle grid
BORDER_PADDING = 50  # Padding for the green border area

# Image path
IMAGE_PATH = "pic.jpg"

# Load the image
if not os.path.exists(IMAGE_PATH):
    raise FileNotFoundError(f"Image file not found at {IMAGE_PATH}")

original_image = pygame.image.load(IMAGE_PATH)
image_width, image_height = original_image.get_size()

# Set up piece dimensions
piece_width = image_width // COLS
piece_height = image_height // ROWS

# Ensure the window is large enough to accommodate the puzzle and some free space
WINDOW_WIDTH = max(WINDOW_WIDTH, image_width + BORDER_PADDING * 2)
WINDOW_HEIGHT = max(WINDOW_HEIGHT, image_height + BORDER_PADDING * 2)

# Create the display window
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Puzzle Game")

# Green border rectangle (adjusted to match the image size)
green_border_rect = pygame.Rect(
    (BORDER_PADDING, BORDER_PADDING, image_width, image_height)
)

# Function to split the image into pieces
def split_image(image, rows, cols):
    pieces = []
    for row in range(rows):
        for col in range(cols):
            x = col * piece_width
            y = row * piece_height
            # Handle edge cases where dimensions aren't evenly divisible
            width = piece_width if col < cols - 1 else image_width - x
            height = piece_height if row < rows - 1 else image_height - y
            piece_surface = image.subsurface(pygame.Rect(x, y, width, height))
            pieces.append(piece_surface)
    return pieces

# Generate puzzle pieces
pieces = split_image(original_image, ROWS, COLS)

# Randomize piece positions outside the green border
piece_positions = []
for _ in pieces:
    rand_x = random.randint(0, WINDOW_WIDTH - piece_width)
    rand_y = random.randint(0, WINDOW_HEIGHT - piece_height)
    # Ensure pieces start outside the green border area
    while green_border_rect.collidepoint(rand_x, rand_y):
        rand_x = random.randint(0, WINDOW_WIDTH - piece_width)
        rand_y = random.randint(0, WINDOW_HEIGHT - piece_height)
    piece_positions.append([rand_x, rand_y])

# Puzzle grid for snapping
grid = [
    (BORDER_PADDING + col * piece_width, BORDER_PADDING + row * piece_height)
    for row in range(ROWS)
    for col in range(COLS)
]

# State tracking
dragging = None  # The index of the piece being dragged
locked_pieces = set()  # Set of indices of locked pieces

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                mouse_x, mouse_y = event.pos
                for i in range(len(piece_positions)):
                    if i in locked_pieces:
                        continue  # Skip locked pieces
                    x, y = piece_positions[i]
                    # Check if the mouse clicked on a piece
                    if x <= mouse_x <= x + piece_width and y <= mouse_y <= y + piece_height:
                        dragging = i  # Start dragging this piece
                        break

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and dragging is not None:
                # Check if the piece is close enough to its target grid position
                piece_x, piece_y = piece_positions[dragging]
                grid_x, grid_y = grid[dragging]
                if abs(piece_x - grid_x) < 10 and abs(piece_y - grid_y) < 10:
                    # Snap the piece to the grid and lock it
                    piece_positions[dragging] = [grid_x, grid_y]
                    locked_pieces.add(dragging)
                dragging = None  # Stop dragging

        elif event.type == pygame.MOUSEMOTION:
            if dragging is not None:  # If a piece is being dragged
                mouse_x, mouse_y = event.pos
                piece_positions[dragging] = [mouse_x - piece_width // 2, mouse_y - piece_height // 2]

    # Draw everything
    screen.fill(BG_COLOR)  # Fill the background
    pygame.draw.rect(screen, GREEN_BORDER_COLOR, green_border_rect, 3)  # Draw the green border

    # Draw pieces
    for i, piece in enumerate(pieces):
        x, y = piece_positions[i]
        screen.blit(piece, (x, y))

    # Update the display
    pygame.display.flip()

pygame.quit()
