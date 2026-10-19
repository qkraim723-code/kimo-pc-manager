"""Generates original application icons (.ico and .png) with matching theme branding."""

from pathlib import Path
from PIL import Image, ImageDraw


def create_app_icon(output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    size = 256
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # 1. Dark green rounded base
    # Color #17251F
    bg_color = (23, 37, 31, 255)
    border_color = (53, 74, 64, 255)
    accent_color = (199, 243, 107, 255)

    draw.rounded_rectangle([(10, 10), (size - 10, size - 10)], radius=48, fill=bg_color, outline=border_color, width=4)

    # 2. Inner lime green rounded badge (#C7F36B)
    badge_rect = [(50, 50), (size - 50, size - 50)]
    draw.rounded_rectangle(badge_rect, radius=36, fill=accent_color)

    # 3. Dark Monitor icon inside the badge
    dark_pen = (18, 32, 25, 255)
    # Monitor screen
    draw.rounded_rectangle([(80, 80), (size - 80, 165)], radius=12, fill=None, outline=dark_pen, width=10)
    # Stand
    draw.line([(128, 165), (128, 195)], fill=dark_pen, width=10)
    draw.line([(100, 195), (156, 195)], fill=dark_pen, width=10)

    png_path = output_dir / "icon.png"
    ico_path = output_dir / "icon.ico"

    img.save(png_path, format="PNG")
    img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])

    print(f"Icons generated at {output_dir}")


if __name__ == "__main__":
    assets_dir = Path(__file__).resolve().parent
    create_app_icon(assets_dir)
