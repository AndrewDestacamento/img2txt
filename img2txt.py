import sys
from PIL import Image

def character(percentage):
    #characters = " .:voO0" # Ascending characters, Light text on dark background
    characters = "0Oov:. " # Descending characters, Dark text on light background
    character_list = list(characters)
    return character_list[int(round(percentage * (len(character_list) - 1)))]

def luminance(r, g, b):
    # Conversion to liner sRGB
    # Repurposed code by Björn Ottosson (https://bottosson.github.io/posts/colorwrong/#what-can-we-do%3F)
    r, g, b = map(
        lambda i: i / 3294.6
        if i < 10.31475
        else ((40 * i + 561) / 10761) ** 2.4,
        [r, g, b],
    )
    # Oklab luminance estimate
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
        text_file = open(sys.argv[1] + ".txt", "x")
    except FileExistsError:
        while True:
            overwrite = input("File for output_path already exists. Overwrite? [Y/n]: ")
            if overwrite.lower() == "y":
                text_file = open(sys.argv[1] + ".txt", "w")
                break
            elif overwrite.lower() == "n":
                exit(
                    "Declined to overwrite file. Try using a new filename. Exiting now..."
                )
            else:
                print(
                    "Error: Invalid input in overwrite prompt. Repeating overwrite prompt..."
                )

    resized_image = image.copy().resize(    
        size=(300, int(round(300/2 * image.height / image.width))),
        resample=Image.Resampling.LANCZOS,
    )

    for y in range(resized_image.height):
        for x in range(resized_image.width):
            R, G, B = resized_image.getpixel((x, y))[0:3]
            L = luminance(R, G, B)
            text_file.write(character(L))
        text_file.write("\n")

text_file.close()

print("Text written to " + sys.argv[1] + ".txt")
