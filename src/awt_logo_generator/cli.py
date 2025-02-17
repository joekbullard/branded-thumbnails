import argparse
from pathlib import Path
from .image_processing import Corner, Style, create_logo_image, generate_image_config, get_logo

def is_path(path: str) -> str:
    if Path(path).exists():
        return path
    raise argparse.ArgumentTypeError(f"{path} is not a valid path")


def is_dir(path: str) -> str:
    if Path(path).is_dir():
        return path
    raise argparse.ArgumentTypeError(f"{path} is not a valid directory")

def is_positive_int(value: str) -> int:
    int_value = int(value)
    if int_value  >= 0:
        return int_value
    raise argparse.ArgumentTypeError(f"{value} is an invalid positive integer. It must be 0 or greater.")

def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Logo Generator")
    parser.add_argument("input_path", help="Path to input file or directory", type=is_path)
    parser.add_argument("output_path", help="Path to output directory", type=is_dir)
    parser.add_argument("-c", "--corner", help="Logo position in the image", choices=[corner.value for corner in Corner], default="bottom_left")
    parser.add_argument("-s", "--style", help="Style of logo to be added to the image", choices=[style.value for style in Style], default="corner")
    parser.add_argument("-m", "--margin", help="Margin size in pixels", type=is_positive_int, default=20)
    parser.add_argument("-w", "--width", help="Width of output image", type=is_positive_int, default=1200)
    parser.add_argument("-y", "--height", help="Height of output image", type=is_positive_int, default=800)
    return parser.parse_args()

def main():
    args = parse_arguments()

    input_path = Path(args.input_path)
    output_path = Path(args.output_path)
    corner = Corner(args.corner)
    style = Style(args.style)
    margin = args.margin
    image_size = (args.width, args.height)
    logo = get_logo(style)
    config = generate_image_config(style, image_size, corner, logo, margin)

    image_files = []

    if input_path.is_dir():
        image_files.extend(
            file_path
            for file_path in input_path.iterdir()
            if file_path.suffix.lower() in {".jpg", ".png", ".webp"}
        )
    else:
        image_files.append(input_path)
    
    
    for img_file in image_files:
        create_logo_image(img_file, output_path, config)


if __name__ == "__main__":
    main()
