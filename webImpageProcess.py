from js import document, console, Uint8Array, window, File
from pyodide.ffi import create_proxy
import io
import asyncio
import pyodide_js
import zipfile

# Setup to install Pillow
async def setup():
    await pyodide_js.loadPackage("micropip")
    import micropip
    await micropip.install("pillow")

asyncio.ensure_future(setup())

async def _upload_change_and_zip(file_input):
    from PIL import Image
    from pyodide.ffi import to_js

    file_list = file_input.files
    fileCount = file_input.files.length
    zip_stream = io.BytesIO()

    # Create an in-memory zip archive
    with zipfile.ZipFile(zip_stream, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for index, file in enumerate(file_list):
            document.getElementById("output_upload_pillow").replaceChildren("Processing ", index+1, " of ", fileCount)
            array_buf = Uint8Array.new(await file.arrayBuffer())
            my_bytes = io.BytesIO(bytearray(array_buf))
            my_image = Image.open(my_bytes)

            # Dynamic size selection
            selected_size = document.querySelector('input[name="size_select"]:checked')
            size_value = selected_size.value
            if size_value == "vertical":
                finalWidth, finalHeight = 1080, 1350
            elif size_value == "square":
                finalWidth, finalHeight = 1080, 1080
            elif size_value == "landscape":
                finalWidth, finalHeight = 1080, 566
            else:
                finalWidth, finalHeight = 1080, 1350

            # Get the border width and color
            borderElement = document.getElementById("borderWidth")
            finalBorder = int(borderElement.value)
            selectedColor = document.getElementById("backColor")
            hexColor = selectedColor.value

            console.log("back color", hexColor)
            console.log("border size", finalBorder)

            finalCanvasR, finalCanvasG, finalCanvasB = hexToRGB(hexColor)
            final_image = process_image(my_image, finalWidth, finalHeight, finalBorder, finalCanvasR, finalCanvasG, finalCanvasB)

            # Save processed image to zip buffer
            image_stream = io.BytesIO()
            final_image.save(image_stream, format="PNG")
            image_name = f"processed_image_{index+1}.png"
            zipf.writestr(image_name, image_stream.getvalue())

    zip_stream.seek(0)
    zip_blob = Uint8Array.new(zip_stream.getvalue())
    zip_file = File.new([zip_blob], "processed_images.zip", {type: "application/zip"})

    # Create and insert download link
    download_link = document.createElement("a")
    download_link.href = window.URL.createObjectURL(zip_file)
    download_link.download = "processed_images.zip"
    download_link.textContent = "Download processed images"
    document.getElementById("output_upload_pillow").replaceChildren(download_link)


# Resizing logic
def process_image(input, targetWidth, targetHeight, borderSize, canvasR, canvasG, canvasB):
    from PIL import Image, ImageOps
    image = input.convert("RGB")
    originalWidth, originalHeight = image.size

    ratio = min((targetWidth - borderSize) / originalWidth, (targetHeight - borderSize) / originalHeight)
    newSize = (int(originalWidth * ratio), int(originalHeight * ratio))
    resizedImage = image.resize(newSize)

    canvas = Image.new('RGB', (targetWidth, targetHeight), (canvasR, canvasG, canvasB))
    offset_x = (targetWidth - resizedImage.width) // 2
    offset_y = (targetHeight - resizedImage.height) // 2
    canvas.paste(resizedImage, (offset_x, offset_y))

    return canvas

# Setup form submit listener
submit_form = document.querySelector("form")

async def on_form_submit(e):
    e.preventDefault()
    file_input = document.getElementById("file-upload-pillow")
    if file_input.files.length == 0:
        console.log("No files selected")
        return
    await _upload_change_and_zip(file_input)

def hexToRGB(hex_str):
    hex_str = hex_str.lstrip("#")
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

submit_proxy = create_proxy(on_form_submit)
submit_form.addEventListener("submit", submit_proxy)
