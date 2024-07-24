import os
import requests
import base64
import json
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

# Function to upload image to imgbb
def upload_image_to_imgbb(image_bytes, api_key):
    url = "https://api.imgbb.com/1/upload"
    payload = {
        "key": api_key,
        "image": base64.b64encode(image_bytes)
    }
    response = requests.post(url, payload)
    return response.json().get('data', {}).get('url')

# Function to format the response into markdown
def format_response(response_content):
    general_info = response_content.get("General Info", {})

    general_info_md = "### General Info\n"
    for key, value in general_info.items():
        general_info_md += f"- **{key}**: {value}\n"

    return general_info_md

# Function to analyze the image using Google Generative AI
def analyze_image(image_url, currentDate):
    # Set up the environment variable for Google API key
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDsYq_gHrR7aXmD6rUFMbil2cu2BwIcvc4"

    # Initialize the ChatGoogleGenerativeAI model
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")

    # Prepare the OCR prompt with explicit JSON format
    prompt_ocr = "Given the image of the retail product, please provide an estimate of expiry date, based on the current date (YYYY/MM/DD):" + currentDate + """
    Provide the response in JSON format with the following structure. Make sure the product category follows one of these... if unsure, guess closest category.

    Groceries
    Household Items
    Personal Care
    Clothing and Accessories
    Electronics
    Home and Garden
    Toys and Games
    Automotive
    Sporting Goods
    Books and Stationery
    Pharmacy and Health
    Pet Supplies

    Ensure your response doesn't have any additional quotes, and begins/ends with {}.

    {
      "General Info": {
          "Brand name": "value (either guess what brand or say generic, no other option)
          "Product name": "value" (NOT a brand, should be product type, ex. peanuts, chocolate, etc),
          "Product category": "value (broad category, must pick one of the above list)",
          "Color": "value",
          "Esimated shelf-life": "value" (MUST give a SINGLE HYPER SPECIFIC SHELF LIFE TIMING IN format x.xx years),
          "Material or fabric type": "value",
          "Usage or purpose": "value",
          "Unique selling points or features": "value",
          "Price in USD": "value" (MUST give a floating point guess, not a range or verbal answer),
          "Customer target group": "value",
          "Certifications or special labels": "value"
          "Expiry date": "value" (MUST give a SINGLE date in YYYY-MM-DD format, NOT a range)
      },
    }
    """

    # Create the message content with the image URL
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt_ocr},
            {"type": "image_url", "image_url": image_url},
        ]
    )

    # Invoke the model and get the response
    response = llm.invoke([message])
    try:
        response_content = json.loads(response.content)
        return response_content
    except json.JSONDecodeError:
        return None
