import  io # Python's native 

import PIL # the Python Image Library
import IPython 
import funix 

@funix.funix(
    title="Convert color images to grayscale images",
)
def gray_it(image: funix.hint.BytesImage) -> IPython.display.Image:
    img = PIL.Image.open(io.BytesIO(image))
    gray = PIL.ImageOps.grayscale(img) 
    output = io.BytesIO()
    gray.save(output, format="PNG")
    return output.getvalue()