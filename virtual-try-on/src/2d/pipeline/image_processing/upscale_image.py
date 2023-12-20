import io
import vertexai
from PIL import Image as PIL_Image
from vertexai.preview.vision_models import Image, ImageGenerationModel


PROJECT_ID = "meesho-vto-thp-1023"
LOCATION = "us-central1"
vertexai.init(project=PROJECT_ID, location=LOCATION)


def paste_image_in_center(image_path):
    # Load the image using OpenCV
    image = PIL_Image.open(image_path)

    # Create a white image with dimensions 1024x1024
    white_image = PIL_Image.new('RGB', (1024, 1024), color=(255, 255, 255))

    # Calculate the center coordinates of the white image
    center_x = white_image.width // 2
    center_y = white_image.height // 2

    # Calculate the offset coordinates for the image to be pasted
    offset_x = center_x - image.width // 2
    offset_y = center_y - image.height // 2

    # Paste the image onto the white image at the offset coordinates
    white_image.paste(image, (offset_x, offset_y))

    return white_image


def upscale(image_path, output_path):
    # Load ImageGen model
    model = ImageGenerationModel.from_pretrained("imagegeneration@002")

    # Get 1024x1024 image
    white_image = paste_image_in_center(image_path=image_path)

    # Vertex AI Vision Image format
    image_bytes_io = io.BytesIO()
    white_image.save(image_bytes_io, format='PNG')
    image_bytes = image_bytes_io.getvalue()

    # Create Vertex AI Vision `Image` object
    base_img = Image(image_bytes=image_bytes)

    # Upscale image and save the output
    images = model.upscale_image(base_img)
    images.save(location=output_path)
