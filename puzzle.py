#Making a photo into svg pieces and then making the pieces from svg to png. No pygame so far.

import os
from pyjigsaw import jigsawfactory
import subprocess

# Paths
image_path = "C:/Users/irina/.vscode/workspace/Proiect_Puzzle/giorno.png"
output_dir = "C:/Users/irina/.vscode/workspace/Proiect_Puzzle/tmp"
png_output_dir = os.path.join(output_dir, "png_pieces")

# Ensure paths exist
if not os.path.exists(image_path):
    print(f"Error: Image file not found at {image_path}")
    exit()

print(f"Image file found at: {image_path}")

if not os.path.exists(output_dir):
    os.makedirs(output_dir)
    print(f"Created output directory at: {output_dir}")

if not os.path.exists(png_output_dir):
    os.makedirs(png_output_dir)
    print(f"Created PNG output directory at: {png_output_dir}")


# Function to convert SVG to PNG
def convert_svg_to_png(svg_file, png_file):
    try:
        subprocess.run(
            [
                "inkscape",
                svg_file,
                "--export-type=png",
                "--export-filename",
                png_file,
            ],
            check=True,
        )
        print(f"Converted {svg_file} to {png_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {svg_file} to PNG: {e}")


# Create jigsaw cut template and generate SVG pieces
try:
    # Generate puzzle template
    cut = jigsawfactory.Cut(3, 3, image=image_path, use_image=True)
    jig = jigsawfactory.Jigsaw(cut, image_path)

    print("Puzzle template created successfully.")
    print("Generating SVG jigsaw pieces...")

    # Generate SVG jigsaw pieces in output_dir
    jig.generate_svg_jigsaw(output_dir)
    print("Jigsaw pieces generated successfully!")

    # Convert SVG files to PNG
    for svg_file in os.listdir(output_dir):
        if svg_file.endswith(".svg"):
            svg_path = os.path.join(output_dir, svg_file)
            png_path = os.path.join(png_output_dir, os.path.splitext(svg_file)[0] + ".png")
            convert_svg_to_png(svg_path, png_path)

    print("All SVG files have been converted to PNG.")

except PermissionError as e:
    print(f"PermissionError while generating jigsaw: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")


