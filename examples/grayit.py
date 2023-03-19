from typing import List
from io import BytesIO
from PIL import Image as PILImage
from funix import funix
from funix.hint import Image
from funix.widget.builtin import BytesImage
import numpy as np


def rgb_image_to_gray_image(image: bytes) -> bytes:
    img = PILImage.open(BytesIO(image))
    width, height = img.width, img.height
    grays = np.zeros((height, width), dtype=np.uint8)
    for y in range(height):
        for x in range(width):
            if img.mode == "RGBA":
                r, g, b, _ = img.getpixel((x, y))
            elif img.mode == "RGB":
                r, g, b = img.getpixel((x, y))
            else:
                raise Exception("Unsupported image mode")
            gray = int(pow((r**2.2 + (1.5*g)**2.2 + (0.6*b)**2.2)/(1**2.2+1.5**2.2+0.6**2.2), 1/2.2))
            grays[y][x] = gray
    file = PILImage.fromarray(grays)
    output = BytesIO()
    file.save(output, format="PNG")
    return output.getvalue()


@funix(
    title="Convert colored images to gray images",
)
def gray_it(image: List[BytesImage]) -> List[Image]:
    return [rgb_image_to_gray_image(img) for img in image]
