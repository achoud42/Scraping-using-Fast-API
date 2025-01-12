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
from emailNotification import EmailNotification
import configparser

# Initialize FastAPI app
app = FastAPI()

config = configparser.ConfigParser()
config.read("config.ini")

# Retrieve configurations
SCRAPING_CONFIG = config["SCRAPING"]
EMAIL_CONFIG = config["EMAIL"]
SETTINGS_CONFIG = config["SETTINGS"]

allow_notification_button_xpath = SCRAPING_CONFIG["allow_notification_button_xpath"]
shop_element_xpath = SCRAPING_CONFIG["shop_element_xpath"]
PAGINATION_XPATH = SCRAPING_CONFIG["pagination_xpath"]

SMTP_SERVER = EMAIL_CONFIG["smtp_server"]
PORT = int(EMAIL_CONFIG["port"])
USERNAME = EMAIL_CONFIG["username"]
PASSWORD = EMAIL_CONFIG["password"]
RECIPIENT_EMAIL = EMAIL_CONFIG["recipient_email"]

DATA_FILE = SETTINGS_CONFIG["data_file"]

@app.post("/scrape/")
async def scrape_catalog(
    base_url: str,
    pages_limit: int = Query(5, description="Limit the number of pages to scrape."),
    proxy: str = Query(None, description="Proxy string in the format 'http://proxy:port'.")
):
   

    
    page = 0   
    notification = EmailNotification(
        smtp_server=SMTP_SERVER,
        port=PORT,
        username=USERNAME,
        password=PASSWORD,
        recipient_email=RECIPIENT_EMAIL,
    )
    
    processor = ProductDataProcessor()
    driver= ChromeWebDriver(proxy)
    driver.requestUrl(base_url,30)
    scraped_count =0
    try :
        # to handle allow button notification
        allow_button = ChromeWebDriver.clickElementByXPath(allow_notification_button_xpath)
    except Exception as e :
        print(str(e))

    try:
        while(page<=pages_limit) :            
            
            
            shop_data = ChromeWebDriver.waitUntil(EC.presence_of_element_located((By.XPATH, shop_element_xpath)), 10)
            shop_data = shop_data.encode('ascii', errors='replace').decode()
            ChromeWebDriver.clickElementByXPath(PAGINATION_XPATH)
            page +=1
            scraped_count += processor.process_and_save(shop_data, DATA_FILE)
           
    finally:
        # Close the WebDriver
        driver.close()
    message = f"Scraping completed. Total products scraped: {scraped_count}"
    notification.notify(message)

    return {"status": "success", "products_scraped": scraped_count}




# Run the FastAPI application with:
# uvicorn filename:app --reload
