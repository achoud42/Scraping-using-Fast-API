import json
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

class ProductDataProcessor:
    def __init__(self):
        pass

    def process_and_save(self, raw_data, file_name):
        """
        Process the raw product data and save it to a specified JSON file.

        Args:
        - raw_data (str): The raw product data as a string.
        - file_name (str): The name of the JSON file to save the processed data.

        Returns:
        - None
        """
        try:
            # Split the raw data into individual products
            products = raw_data.strip().split("\nBuy Now")
            product_data = []
            product_count = 0

            for product in products:
                # Extract product title
                title_match = re.search(r"^.*?(?=\nRated|Starting at:|₹)", product, re.DOTALL)
                product_title = title_match.group(0).strip() if title_match else "Unknown Title"

                # Extract product price
                price_match = re.search(r"₹([\d,]+\.?\d*)", product)
                product_price = float(price_match.group(1).replace(",", "")) if price_match else 0.0
                product_count +=1


                # Add processed data to the list
                product_data.append({
                    "product_title": product_title,
                    "product_price": product_price,
                })

            # Save the data to a JSON file
            with open(file_name, "a", encoding="utf-8") as f:
                json.dump(product_data, f, ensure_ascii=False, indent=4)

            return product_count

        except Exception as e:
            print(f"An error occurred: {e}")


