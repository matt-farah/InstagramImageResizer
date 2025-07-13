from PIL import Image, ImageOps
import os

folderToProcess = "/users/matt1125/Downloads/test"
finalHeight = 1350
finalWidth = 1080

def process_image (input, output, targetWidth, targetHeight):
    # Load. the image
    image = Image.open(input).convert("RGB")
    originalWidth, originalHeight = image.size
    print ("originalw",originalWidth,"originalh", originalHeight)
    
    #resize the image
    ratio = min(targetWidth / originalWidth, targetHeight /originalHeight)
    print(ratio)
    newSize = (int(originalWidth * ratio), int (originalHeight * ratio))
    resizedImage = image.resize(newSize)

    #create a new white canvas and center the image
    canvas = Image.new('RGB', (targetWidth,targetHeight), (255,255,255))
    offset_x = (targetWidth - resizedImage.width) // 2
    offset_y = (targetHeight - resizedImage.height) // 2
    canvas.paste (resizedImage, (offset_x, offset_y))

    canvas.save(output)
    print(f"Image saved to {output}")

with os.scandir(folderToProcess) as files:
    for file in files:
        name = file.name
        print("processing...", name)
        filePath = folderToProcess + "/" + name
        newFilePath = folderToProcess + "/" + "i_" + name
        print(filePath,newFilePath,finalWidth,finalHeight)
        process_image (filePath,newFilePath,finalWidth,finalHeight)


# process_image ("/Users/matt1125/Documents/Github/InstagramImageResizer/DSCF0462.JPG","/Users/matt1125/Documents/Github/InstagramImageResizer/Resized.jpg", 1080, 1350)