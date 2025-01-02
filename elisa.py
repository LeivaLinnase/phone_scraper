from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd

options = Options()
options.add_argument("--headless")  # Disable visible browserWindow
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://www.elisa.ee/seadmed/eraklient/nutitelefonid?vendor=APPLE&sortType=private_focus"
driver.get(url)

try:
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "eds-product-card"))
    )
    # Find all product cards
    product_cards = driver.find_elements(By.TAG_NAME, "eds-product-card")
    product_data = []
    for card in product_cards:
        href = card.get_attribute("href")
        buyout_price = card.get_attribute("ng-reflect-buyout-price")
        buyout_discount_price = card.get_attribute("ng-reflect-buyout-discount-price")
        name = card.get_attribute("ng-reflect-name")
        img_element = card.find_element(By.TAG_NAME, "img")
        img_src = img_element.get_attribute("src")

        product_data.append({
            "Image URL": img_src,
            "Product Name": name,
            "Original Price": buyout_price,
            "Discount Price": buyout_discount_price,
            "Product URL": f'https://www.elisa.ee/{href}',
            "Availability": "In Stock",
            "Seller": "Elisa"
        })

    df = pd.DataFrame(product_data)
    df.to_csv("data_files/elisa.csv", index=False)
    print("Data saved to data_files/elisa.csv")

except Exception as e:
    print("Error:", e)

finally:
    driver.quit()
