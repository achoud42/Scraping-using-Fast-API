from fastapi import FastAPI, Query
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import json
import uuid

# Initialize FastAPI app
app = FastAPI()

# Configure the paths for storing scraped data
DATA_FILE = "scraped_data.json"
IMAGE_FOLDER = "images"

# Ensure the image folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

@app.post("/scrape/")
async def scrape_catalog(
    base_url: str,
    pages_limit: int = Query(5, description="Limit the number of pages to scrape."),
    proxy: str = Query(None, description="Proxy string in the format 'http://proxy:port'.")
):
   

    scraped_data = []

    try:
        for page in range(1, pages_limit + 1):
            # Navigate to the catalog page
            page_url = f"{base_url}?page={page}"
            driver.get(page_url)

            # Locate products on the page
            products = driver.find_elements(By.CLASS_NAME, "product-card")  # Adjust based on the site's structure

            for product in products:
                try:
                    # Extract product details
                    product_title = product.find_element(By.CLASS_NAME, "product-title").text  # Adjust selectors
                    product_price = product.find_element(By.CLASS_NAME, "product-price").text  # Adjust selectors
                    product_image_url = product.find_element(By.TAG_NAME, "img").get_attribute("src")  # Adjust selectors

                    # Download the product image
                    image_path = download_image(product_image_url)

                    # Append product data to the list
                    scraped_data.append({
                        "product_title": product_title,
                        "product_price": product_price,
                        "path_to_image": image_path
                    })

                except Exception as e:
                    print(f"Error processing a product: {e}")

    finally:
        # Close the WebDriver
        driver.quit()

    # Save the scraped data to a JSON file
    save_data_to_file(scraped_data)

    return {"status": "success", "products_scraped": len(scraped_data)}


def download_image(image_url):
    """Download an image and save it locally."""
    import requests

    image_name = f"{uuid.uuid4()}.jpg"
    image_path = os.path.join(IMAGE_FOLDER, image_name)

    try:
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(image_path, "wb") as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
    except Exception as e:
        print(f"Error downloading image {image_url}: {e}")
        image_path = None

    return image_path


def save_data_to_file(data):
    """Save scraped data to a JSON file."""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


# Run the FastAPI application with:
# uvicorn filename:app --reload
