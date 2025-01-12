from fastapi import FastAPI, Query
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os
import json
import uuid
from ChromeWebDriver import *
from Process_data import ProductDataProcessor
# Initialize FastAPI app
app = FastAPI()

# Configure the paths for storing scraped data
DATA_FILE = "/Documents/scraped_data.json"
IMAGE_FOLDER = "/Documents/images/"

# Ensure the image folder exists
os.makedirs(IMAGE_FOLDER, exist_ok=True)

@app.post("/scrape/")
async def scrape_catalog(
    base_url: str,
    pages_limit: int = Query(5, description="Limit the number of pages to scrape."),
    proxy: str = Query(None, description="Proxy string in the format 'http://proxy:port'.")
):
   

    
    page = 0   
    allow_notification_button_xpath = '//*[@id="onesignal-slidedown-allow-button"]'
    shop_element_xpath = '//*[@class="mf-shop-content"]/ul'
    pagination_xpath = '//*[@class="next page-numbers"]'
    processor = ProductDataProcessor()
    driver= ChromeWebDriver(proxy)
    driver.requestUrl(base_url,30)
    try :
        # to handle allow button notification
        allow_button = ChromeWebDriver.clickElementByXPath(allow_notification_button_xpath)
    except Exception as e :
        print(str(e))

    try:
        while(page<=pages_limit) :            
            
            
            shop_data = ChromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, shop_element_xpath)), 10)
            shop_data = shop_data.encode('ascii', errors='replace').decode()
            ChromeWebDriver.clickElementByXPath(pagination_xpath)
            page +=1
            scraped_count = processor.process_and_save(shop_data, DATA_FILE)
           
    finally:
        # Close the WebDriver
        driver.close(

    

    return {"status": "success", "products_scraped": scraped_count}




# Run the FastAPI application with:
# uvicorn filename:app --reload
