from PIL import Image, ImageOps, ImageDraw
from pathlib import Path
from typing import Tuple, List, Optional
from enum import Enum
from dataclasses import dataclass


class Style(Enum):
    CORNER = "corner"
    DIAGONAL = "diagonal"


class Corner(Enum):
    BOTTOM_LEFT = "bottom_left"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_RIGHT = "bottom_right"


@dataclass
class ImageProcessingConfig:
    output_image_size: Tuple[int, int]
    logo_location: Tuple[int, int]
    logo: Image.Image
    triangle: Optional[List[Tuple[int, int]]]


def generate_triangle(
    corner: Corner, img_width: int, img_height: int
) -> List[Tuple[int, int]]:
    if corner == Corner.BOTTOM_LEFT:
        return [(0, 400), (600, 800), (0, img_height)]
    elif corner == Corner.TOP_LEFT:
        return [(0, 0), (600, 0), (0, 400)]
    elif corner == Corner.TOP_RIGHT:
        return [(600, 0), (img_width, 0), (img_width, 400)]
    elif corner == Corner.BOTTOM_RIGHT:
        return [(600, 800), (img_width, 400), (1200, 800)]


def logo_paste_location(
    corner: Corner, img_width: int, img_height: int, logo: Image.Image, margin: int = 50
) -> Tuple[int, int]:
    logo_width, logo_height = logo.size

    left = margin
    right = img_width - margin - logo_width
    top = margin
    bottom = img_height - margin - logo_height

    locations = {
        Corner.BOTTOM_LEFT: (left, bottom),
        Corner.TOP_LEFT: (left, top),
        Corner.TOP_RIGHT: (right, top),
        Corner.BOTTOM_RIGHT: (right, bottom),
    }
    return locations[corner]


def get_logo(style: Style) -> Image.Image:
    if style == Style.DIAGONAL:
        logo_path = Path("./media/AWT_LOGO_TRANSPARENT.png")
    elif style == Style.CORNER:
        logo_path = Path("./media/AWT_LOGO_WHITE.jpg")
    return Image.open(logo_path)


def handle_transparency(image: Image.Image) -> Image.Image:
    if image.mode in ("P", "LA", "RGBA", "CMYK"):
        image = image.convert("RGBA")
    return image


def generate_image_config(
    style: Style,
    image_size: Tuple[int, int],
    corner: Corner,
    logo: Image.Image,
    margin: int,
) -> ImageProcessingConfig:
    img_width, img_height = image_size

    logo = get_logo(style)
    logo = logo.convert('RGBA')
    logo_coordinates = logo_paste_location(corner, img_width, img_height, logo, margin)

    if style == Style.DIAGONAL:
        triangle_coords = generate_triangle(corner, img_width, img_height)
    else:
        triangle_coords = None

    image_config = ImageProcessingConfig(
        output_image_size=image_size,
        logo=logo,
        logo_location=logo_coordinates,
        triangle=triangle_coords,
    )

    return image_config


def create_logo_image(
    image_path: Path, output_path: Path, image_config: ImageProcessingConfig
) -> None:
    image: Image.Image = Image.open(image_path)
    fitted_image = ImageOps.fit(image, image_config.output_image_size)

    if image_config.triangle:
        draw = ImageDraw.Draw(fitted_image)
        draw.polygon(image_config.triangle, fill="white")

    fitted_image = fitted_image.convert("RGBA")
    fitted_image.paste(
        im=image_config.logo, box=image_config.logo_location, mask=image_config.logo
    )
    file_name = (output_path / (image_path.stem + "_logo")).with_suffix(".png")
    fitted_image.save(file_name)
