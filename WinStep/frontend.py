import streamlit as st
from PIL import Image
from backend import upload_image_to_imgbb, format_response, analyze_image
from pytrends.request import TrendReq
from datetime import datetime
import urllib.request
import requests
from time import sleep
from stqdm import stqdm
from streamlit_custom_notification_box import custom_notification_box
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json


# Function to upload and display image
def upload_and_display_image():
    st.header("Capture a product image to upload")
    img = st.camera_input("Please allow camera permissions if necessary")
    #if img is not None:
     #   st.image(img, caption="Captured Image", use_column_width=True)
      #  for _ in stqdm(range(50), desc="Processing Image", mininterval=1):
       #   sleep(1)
    return img

# Function to get the current date
def get_current_date():
    st.header("Enter date of product initial shelf stockage")
    curDate = st.date_input(
        "When ready press proceed to access camera upload",
        value=None,
        min_value=None,
        max_value=None,
        key=None,
        help=None,
        on_change=None,
        args=None,
        kwargs=None,
        format="YYYY-MM-DD",
        disabled=False,
        label_visibility="visible"
    )
    date_time = None
    try:
      date_time = curDate.strftime("%Y/%m/%d")
    except:
      pass
    return date_time

# Function to get image value
def get_image_value(img):
    if img is not None:
        return img.getvalue()
    return None

# Function to get and upload logo
def get_logo(url):

    # This statement requests the resource at
    # the given link, extracts its contents
    # and saves it in a variable
    data = requests.get(url).content

    # Opening a new file named img with extension .jpg
    # This file would store the data of the image file
    f = open('logo.png','wb')

    # Storing the image data inside the data variable to the file
    f.write(data)
    f.close()

    if open:
      st.logo("logo.png")

# Function to upload image to imgbb and get the URL
def upload_image(val, imgbb_api_key):
    if val is not None:
        image_url = upload_image_to_imgbb(val, imgbb_api_key)
        if image_url:
            for _ in stqdm(range(10), desc="Processing Image", mininterval=1):
                sleep(0.3)
            #st.link_button("Image URL", image_url)
            styles = {
                      'material-icons': {'color': 'white'},
                      'text-icon-link-close-container': {'box-shadow': '#3896de 0px 4px'},
                      'notification-text': {'font-family': 'monaco'},
                      'close-button': {'font-family': 'monaco'},
                      'link': {'font-family': 'monaco'}
                      }

            custom_notification_box(icon='open_in_new', textDisplay='Successfully Uploaded!', externalLink='Link', url=image_url, styles=styles, key="foo")
            return image_url
        else:
            st.error("Failed to upload image. Please try again.")
    return None

# Function to analyze the image
def analyze_uploaded_image(image_url, date_time):
    if image_url:
        with st.spinner('Analyzing the image...'):
            response_content = analyze_image(image_url, date_time)
        st.success('Analysis complete!')
        return response_content
    return None

# Function to format and display the response
def display_analysis_results(response_content):
    if response_content:
        formatted_response = format_response(response_content)
        st.markdown(formatted_response)
    else:
        st.error("Failed to parse the response. Please ensure the model is providing a valid JSON response.")
    return None

# Function to fetch all categories from Firebase
def fetch_all_categories(db):
    collections = db.collections()
    return [collection.id for collection in collections]

# Function to fetch data from Firebase
def fetch_data_from_firebase(db, category):
    collection_ref = db.collection(category)
    docs = collection_ref.stream()
    data = []
    for doc in docs:
        doc_dict = doc.to_dict()
        doc_dict['id'] = doc.id
        data.append(doc_dict)
    return data

# Function to display all products in a grid format
def display_products_grid(db):
    categories = fetch_all_categories(db)
    for category in categories:
        st.subheader(f"Category: {category}")
        products = fetch_data_from_firebase(db, category)
        cols = st.columns(4)  # Adjust the number of columns based on the desired grid layout
        for index, product in enumerate(products):
            with cols[index % 4]:
                st.image(product["Image URL"], use_column_width=True)
                st.write(product["Product name"])
                if st.button("View Details", key=f"{product['id']}"):
                    st.session_state["selected_product"] = product
                    st.session_state["page"] = "Product Details"

# Function to display detailed information about a product
def display_product_details():
    product = st.session_state.get("selected_product", {})
    if product:
        st.image(product["Image URL"], use_column_width=True)
        st.write("### Product Details")
        for key, value in product.items():
            if key != "Image URL" and key != "id":
                st.write(f"**{key.replace('_', ' ').capitalize()}**: {value}")
        if st.button("Back to Product List"):
              st.session_state["page"] = "Review Data"

# Main function to run the Streamlit app
def main():
    st.title("Shelf-Life Analysis Application")


    key_path_dict = {
        "type": "service_account",
        "project_id": "winstep-16ca4",
        "private_key_id": "e21fa56abf951b80ec13ef31b9760fee89f2c327",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC/CMWBasSZpF91\no/N354giNKF4Dp3sW/39CjnOjUsbIrrOLnuRXzC0Lfb27qsGMpjLfYEuZij/4vIU\nx3Mk47SjsyzCE6hOV2ykbbTK+NPCTFZ5ytFK+MWxfpRPYWd30u1+QE2ea0MFtSFx\nRR4x4Aot/MLrzCAOMfJPeV4T1ld+kiibB32PYJE28Mm5XBQMzfNfD1E1a5wAOtCO\nMoqLXXWmWie0pX4Z0O/iL9RuYs7bSDhNV8Jvrv9wtAvtxrMGtR6f2Q2JumXLgGgc\nOYox2FAOheNtduNojkN7gzl1hB/McwWNWxfR9wXRRVaR4efUeCzrgk2xk4vZkxrs\nDpaIAzaVAgMBAAECggEALIeSZlbpafj/SXBEpewB9xs2kkIx/LD61PuHuwaDfdlM\nGxiJtDqwoyddvHSoyAKOTEy+in7EytTvYfmV9QDhEBGJetnTLyPAztlFvdRfpBhg\nRfaJb8TqbDPZxWEqmatAsd+yWB2fm1p756fZYH3dUZfsJcPIqxZoaa8cR1p8vaNU\nEy4dck4kx4bk+gPA8TdxwHCfm2e5f7CB0+WwHa9BEdLE9be7DgRL1ELFv8BOoBYM\nDLe+rUmwbVaZP2OWqzAt6X/nAsipTXxLQPLdKxokfdAiJfDtIDEZRVGj0kk0mH85\nX9hzzLBsraXNoY/0vjwQTUAGllX7bCu6Mc39vG6D9wKBgQDi1zQEI8LuV+FFb/fh\n2kdvRqsiC+qU0q9Ym7vX3zlqJPvVzR59VLtr0E9LmOzFfGbkleN7s3neFgYv0wdC\nNzrH5IwUvqjTW+v0NzDrAv9FkAR+NCqp1kWAVV3zgHMWhe2k8xd3FiJAoABeBB4n\nLbV3xZwF6hBF715er5FvYA48dwKBgQDXl0OU5WSXY6/hT4ENvcjNR0PQ2VRNnLuD\nRMLC3vX9hy+i7aycepcDnLrwNCZfTEBED3gsm/npwobN61N6UNvXmIowEvCXXlnu\nOwyf/OmwMhio90EQJxKaEZf8d6SBrTcyN0dppgit/53Q36ZnkoMWDY2rBWow1uPh\nn1CPUtpEUwKBgQDMUzwvXmb/eXkYqrqFXbBqsyUDDejHFN+M2PpigFefHKEa/CAy\nlFgdzQ0f8yeS23NzAvBdRFTJjt0TxuoK4uS3mU30gahgebQXzn7psVFuv0LMywCC\n6ta/uiVeaJ1B9HES20SPqAhCXdz20o62i52hvQXE7giqdepzL4G46LTqEQKBgCF/\ngGG3Tuzy8VYZ61x+O6AhzZi63A1/J+eanIR47lHpWm5/bY2WwrYt+SHviHLQP0AU\nA0EzLx6yOg3u3baor7ANJJOZrcZnQ6PviuOlAY5+CjTezj47Q/mqeCojUO1RQ71K\nt47j3H9ks1nMFmgLbNDVZEjJe5mBGkFpZrQOVJm/AoGAEeDE7kEihF02FMcvKYwK\ni+rINaFK7mjGqZANugIv/ZeoOxtyTVbygtYUtwSTL/STxSiopCn0iBdK/g+rb8Jo\ncbAf5G26Og9T5M9SPkO3U4EjvfO1iHrEooiRoSfHgUjABFo2stKpcrkn4EoLr1Hn\n+jTtDP9qw47bBODXfLSnusg=\n-----END PRIVATE KEY-----\n",
        "client_email": "firebase-adminsdk-7ye8r@winstep-16ca4.iam.gserviceaccount.com",
        "client_id": "104601567201728476313",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-7ye8r%40winstep-16ca4.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com"
    }
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(key_path_dict)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    st.sidebar.title("Navigation")
    if "page" not in st.session_state:
        st.session_state["page"] = "Capture & Analyze"

    if st.sidebar.button("Capture & Analyze"):
        st.session_state["page"] = "Capture & Analyze"
    if st.sidebar.button("Review Data"):
        st.session_state["page"] = "Review Data"

    st.logo("https://i.ibb.co/FszJXsx/Infosys-logo-2-optimized.png")

    if st.session_state["page"] == "Capture & Analyze":
        # Get the current date
        date_time = get_current_date()
        if date_time:
            img = upload_and_display_image()
            if img:
                st.session_state["img"] = img
                val = get_image_value(img)
                if val:
                    imgbb_api_key = "7fbd8710350bbf47d40088ff68ce1607"
                    image_url = upload_image(val, imgbb_api_key)
                    if image_url:
                        response_content = analyze_uploaded_image(image_url, date_time)
                        return_tuple = (image_url, response_content)
                        display_analysis_results(response_content)

                        # Extract product category before popping General Info
                        product_category = response_content["General Info"]["Product category"]

                        general_info = response_content.pop("General Info")
                        general_info["Image URL"] = image_url

                        collection_ref = db.collection(product_category)
                        collection_ref.add(general_info)

    elif st.session_state["page"] == "Review Data":
        display_products_grid(db)

    if st.session_state["page"] == "Product Details":
        display_product_details()

if __name__ == "__main__":
    main()
