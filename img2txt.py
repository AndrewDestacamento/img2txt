import sys
import time

from PIL import Image

# Double the size for detecting a decompression bomb DOS attack
# Implies the user has a minimum of 0.54GB of RAM in case a large image is used
Image.MAX_IMAGE_PIXELS = 178_956_971


OUTPUT_WIDTH = 300
CHARACTERS = "@OXoxv;:,. "  # Characters in descending size and density, Dark text on light background
# CHARACTERS = " .,:;vxoXO@" # Characters in ascending size and density, Light text on dark background


def character(percentage):
    # Acts somewhat like a lookup table, where 0.0 is the first character and 1.0 is the last value
    return CHARACTERS[int(percentage * len(CHARACTERS))]


def luminance(r, g, b):
    # Conversion from 8-bit standard RGB to float linear RGB
    # Repurposed code by Björn Ottosson (https://bottosson.github.io/posts/colorwrong/#what-can-we-do)
    r, g, b = map(
        lambda i: i / 3_294.6 if i < 10.31475 else ((40 * i + 561) / 10_761) ** 2.4,
        [r, g, b],
    )
    # Conversion from float linear RGB to float Oklab, just the luminance estimate
    # Oklab by Björn Ottosson (https://bottosson.github.io/posts/oklab/#converting-from-linear-srgb-to-oklab)
    lu = (
        0.2104542553
        * (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
        + 0.793617785
        * (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
        - 0.0040720468
        * (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    )
    return lu


with Image.open(sys.argv[1]) as image:
    try:
        text_file = open(f"{sys.argv[1]}.txt", "x")
    except FileExistsError:
        while True:
            overwrite = input("File for output_path already exists. Overwrite? [Y/n]: ")
            match overwrite.lower():
                case "y":
                    text_file = open(f"{sys.argv[1]}.txt", "w")
                    break
                case "n":
                    exit(
                        "Declined to overwrite file. Try using a new filename. Exiting now..."
                    )
                case _:
                    print(
                        "Invalid input in overwrite prompt. Repeating overwrite prompt..."
                    )
    print()

    start_time = time.time()

    resized_image = image.copy().resize(
        size=(OUTPUT_WIDTH, int(round(OUTPUT_WIDTH / 2 * image.height / image.width))),
        resample=Image.Resampling.LANCZOS,
    )

    for y in range(resized_image.height):
        for x in range(resized_image.width):
            pixel_value = resized_image.getpixel((x, y))
            match resized_image.mode:
                case "RGB" | "RGBA":
                    R, G, B = pixel_value[0:3]
                case "P":
                    R, G, B = resized_image.getpalette()[
                        3 * pixel_value : 3 * (pixel_value + 1)
                    ]
                case "L" | "1":
                    R, G, B = [pixel_value] * 3
                case _:
                    raise TypeError(f"Unsupported color mode {resized_image.mode}")
            text_file.write(character(luminance(R, G, B)))
        text_file.write("\n")

text_file.close()

elapsed_time = time.time() - start_time
efficency = image.height * image.width / elapsed_time

print(
    f"Processing time: {elapsed_time:.4f} seconds at {round(efficency):_} pixels/second"
)
print(f"Text written to {sys.argv[1]}.txt")
