import os
from PIL import Image
import pillow_avif

# Input and Output Folder Paths
input_folder = "static/image"
output_folder = "static/image/webp"

# Create Output Folder if Not Exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Supported Image Formats (Including AVIF)
supported_formats = (".jpg", ".jpeg", ".png", ".avif")

# Conversion Quality Settings
quality_settings = {
    "webp_quality": 80
}

# Loop Through All Files in Input Folder
for filename in os.listdir(input_folder):
    input_path = os.path.join(input_folder, filename)

    # Check if File has a Supported Format
    if filename.lower().endswith(supported_formats):
        try:
            # Open the Image
            with Image.open(input_path) as img:
                # Set Output Path with .webp Extension
                output_filename = os.path.splitext(filename)[0] + ".webp"
                output_path = os.path.join(output_folder, output_filename)

                # Convert and Save Image as WebP
                img.save(output_path, "WEBP", quality=quality_settings["webp_quality"])
                print(f"Converted: {input_path} → {output_path}")

        except Exception as e:
            print(f"Failed to convert {input_path}: {e}")

print("All images converted successfully!")
