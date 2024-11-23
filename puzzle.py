import os
from pyjigsaw import jigsawfactory

# Paths
image_path = "C:/Users/irina/.vscode/workspace/Proiect_Puzzle/bluelock.jpg"
output_dir = "C:/Users/irina/.vscode/workspace/Proiect_Puzzle/tmp"

# Check image and output directory
if not os.path.exists(image_path):
    print(f"Error: Image file not found at {image_path}")
else:
    print(f"Image file found at: {image_path}")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created output directory at: {output_dir}")

# Create jigsaw cut template
try:
    cut = jigsawfactory.Cut(10, 10, image=image_path, use_image=True)
    print("Puzzle template created successfully.")
except Exception as e:
    print(f"Error creating puzzle template: {e}")

# Generate SVG jigsaw pieces
try:
    jig = jigsawfactory.Jigsaw(cut, image_path)
    print("Generating SVG jigsaw pieces...")
    jig.generate_svg_jigsaw(output_dir)
    print("Jigsaw pieces generated successfully!")
except PermissionError as e:
    print(f"PermissionError while generating SVG jigsaw: {e}")
except Exception as e:
    print(f"Unexpected error while generating SVG jigsaw: {e}")

