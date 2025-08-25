from js import document, console, Uint8Array, window, File, navigator, Blob, URL
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

# Install packages for offline use
async def install_packages():
    status = document.getElementById("status")
    status.innerText = "Installing Python packages..."
    await micropip.install(["pillow"])
    status.innerText = "Packages installed!"

window.triggerPyInstall = create_proxy(install_packages)

async def _upload_change_and_zip(file_input):
    from PIL import Image
    from pyodide.ffi import to_js

    file_list = file_input.files
    fileCount = file_input.files.length
    user_agent = navigator.userAgent
    is_mobile = any(keyword in user_agent for keyword in ["Mobi", "Android", "iPhone", "iPad", "iPod"])


    output = document.getElementById("output_upload_pillow")
    output.replaceChildren("Processing...")


    if not is_mobile:
        zip_stream = io.BytesIO()

        # Create an in-memory zip archive
        with zipfile.ZipFile(zip_stream, mode="w", compression=zipfile.ZIP_DEFLATED) as zipf:
            for index, file in enumerate(file_list):
                document.getElementById("output_upload_pillow").replaceChildren("Processing ", index+1, " of ", fileCount)
                # Save processed image to zip buffer
                final_image = await process_and_resize(file, index)
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
    else:
        # Mobile: download each image individually
       # Store processed images for download
        processed_images = []

        # Mobile: prepare images and store them
        output.replaceChildren("Preparing downloads...")
        for index, file in enumerate(file_list):
            final_image = await process_and_resize(file, index)
            image_stream = io.BytesIO()
            final_image.save(image_stream, format="PNG")
            image_bytes = image_stream.getvalue()
            processed_images.append((image_bytes, f"processed_image_{index+1}.png"))

        # Create "Download All" button
        output.replaceChildren("")  # Clear previous content once downloads are ready
        download_all_btn = document.createElement("button")
        download_all_btn.textContent = "Download All Images"
        output.appendChild(download_all_btn)

        # Define download function
        def download_all_images(event=None):
            from js import Blob, URL
            for image_bytes, filename in processed_images:
                blob = Blob.new([to_js(image_bytes)], { "type": "image/png" })
                url = URL.createObjectURL(blob)
                link = document.createElement("a")
                link.href = url
                link.download = filename
                document.body.appendChild(link)
                link.click()
                document.body.removeChild(link)
                URL.revokeObjectURL(url)

        # Attach event listener
        download_all_btn.addEventListener("click", create_proxy(download_all_images))

            
# Process single image and return processed image
async def process_and_resize(file, index):
    from PIL import Image
    array_buf = Uint8Array.new(await file.arrayBuffer())
    my_bytes = io.BytesIO(bytearray(array_buf))
    my_image = Image.open(my_bytes)

    selected_size = document.querySelector('input[name="size_select"]:checked')
    size_value = selected_size.value
    size_map = {
        "vertical": (1080, 1350),
        "square": (1080, 1080),
        "landscape": (1080, 566),
        "story": (1080, 1920)
    }
    finalWidth, finalHeight = size_map.get(size_value, (1080, 1350))

    finalBorder = int(document.getElementById("borderWidth").value)
    hexColor = document.getElementById("backColor").value
    finalCanvasR, finalCanvasG, finalCanvasB = hexToRGB(hexColor)

    return process_image(my_image, finalWidth, finalHeight, finalBorder, finalCanvasR, finalCanvasG, finalCanvasB)



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