from PIL import Image
from pathlib import Path

def convert_webp_to_ico(webp_path_str, ico_path_str):
    """
    Converts a .webp image to a .ico file.
    """
    webp_path = Path(webp_path_str)
    ico_path = Path(ico_path_str)

    if not webp_path.exists():
        print(f"❌ Error: Input file not found at {webp_path}")
        return False

    try:
        # Open the webp image
        img = Image.open(webp_path)

        # Define standard icon sizes
        icon_sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        
        # Save as .ico with multiple sizes
        img.save(ico_path, format='ICO', sizes=icon_sizes)
        
        print(f"✅ Successfully converted {webp_path.name} to {ico_path.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to convert image: {e}")
        return False

if __name__ == "__main__":
    # Convert the user-provided icon
    base_dir = Path(__file__).parent
    convert_webp_to_ico(
        str(base_dir / "icono.webp"),
        str(base_dir / "endless_sky_translator.ico")
    )
