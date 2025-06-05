import os
import base64
from mimetypes import guess_type
from mistralai import Mistral

# Function to encode a local image into data URL 
def local_image_to_data_url(image_path):
    # Guess the MIME type of the image based on the file extension
    mime_type, _ = guess_type(image_path)
    if mime_type is None:
        mime_type = 'application/octet-stream'  # Default MIME type if none is found

    # Read and encode the image file
    with open(image_path, "rb") as image_file:
        base64_encoded_data = base64.b64encode(image_file.read()).decode('utf-8')

    # Construct the data URL
    return f"data:{mime_type};base64,{base64_encoded_data}"

ocr_client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))

ocr_response = ocr_client.ocr.process(
    model="mistral-ocr-latest",
    document={
        "type": "document_url",
        "document_url": local_image_to_data_url("handwritten.pdf")
    },
    include_image_base64=False
)

print(ocr_response)