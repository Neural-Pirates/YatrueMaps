import io
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv(
    "API_KEY"
)  # Placing it here js for now.. Dont send too many requests in testing..
genai.configure(api_key=API_KEY)


def verify_image(file_content, content_type):
    """
    Returns 1 if it contains a road image
    Returns 0 if it contains a map image
    Returns None if it contains None

    """
    file_stream = io.BytesIO(file_content)
    myfile = genai.upload_file(file_stream, mime_type=content_type)

    model = genai.GenerativeModel("gemini-1.5-pro")

    question = f"This ia a request through an API so follow instructions strictly or the program will crash. Classify whether this image has a road or map or None. Answer 1 if it has road, 0 if it has a map, 2 if doesnot have any. Dont write anything else."

    result = model.generate_content([myfile, "\n\n", question])

    if result == "0":
        return "Map"
    elif result == "1":
        return "Road"
    return None
