import base64
import requests
import subprocess
from PIL import Image
from io import BytesIO


def call_image_gen(input_image_path, output_mask_image_path, output_image_dir, background_image_prompt):
    # Load and encode your input 
    with open(input_image_path, "rb") as inp_img_file:
        encoded_inp_img = base64.b64encode(inp_img_file.read()).decode("utf-8")

    with open(output_mask_image_path, "rb") as mask_img_file:
        encoded_mask_img = base64.b64encode(mask_img_file.read()).decode("utf-8")

    # Call Image gen
    # Config
    PROJECT_ID = "meesho-vto-thp-1023"
    EDIT_IMAGE_COUNT = 4
    MODE = "backgroundEditing"

    # Construct the API endpoint URL
    endpoint = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{PROJECT_ID}/locations/us-central1/publishers/google/models/imagegeneration@002:predict".format(
        PROJECT_ID)

    # Construct the request payload
    request_payload = {
        "instances": [
            {
                "prompt": background_image_prompt+". make sure the background image is realistic. DO NOT PUT Reflection of product.",
                "image": {
                    "bytesBase64Encoded": encoded_inp_img
                },
                "mask": {
                    "image": {
                        "bytesBase64Encoded": encoded_mask_img
                    }
                }
            }
        ],
        "parameters": {
            "sampleCount": EDIT_IMAGE_COUNT,
            "negativePrompt": "DO NOT PUT Reflection. DO NOT edit image other than masked image. DO NOT DISTORT MAKSED IMAGE. MAKE SURE THE BACKGROUND IMAGE IS realistic",
            "mode": MODE,
            "IsProductImage":True,
            "disablePersonFace":True,
            "sampleImageSize": "4096",
            "mode": "upscale",
            "guidanceScale":15
        }
    }

    token = subprocess.run(
        "gcloud auth print-access-token", shell=True, capture_output=True, text=True
    ).stdout.strip()

    headers = {
        "Authorization": "Bearer " + token,
        "Content-Type": "application/json; charset=utf-8",
    }

    response = requests.post(
        endpoint,
        json=request_payload,
        headers=headers)

    # Process the response
    if response.status_code == 200:
        result = response.json()
        # Process the generated images in the 'result' variable
        generated_images = result.get("predictions", [])
        for idx, image_data in enumerate(generated_images):
            # Process each generated image data here
            # print(f"Generated Image {idx + 1}: {image_data}")
            img_bytes = base64.b64decode(image_data["bytesBase64Encoded"])
            img = Image.open(BytesIO(img_bytes))
            img.save(f"{output_image_dir}/OUTPUT_{idx}.png")

    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)
