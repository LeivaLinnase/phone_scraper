from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv
import time

options = Options()
options.add_argument("--headless")  # Disable visible browserWindow
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://onoff.ee/et/62-nutitelefonid?q=Br%C3%A4nd-Apple&resultsPerPage=125"
driver.get(url)

with open('data_files/onoff.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)

    writer.writerow(['Image URL', 'Product Name', 'Original Price', 'Discount Price', 'Product URL',
                     'Availability', 'Seller'])

    # Scroll down to load more products
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    # Wait for products to load
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.product_list_item')))

    products = driver.find_elements(By.CSS_SELECTOR, '.product_list_item')
    print(f"Found {len(products)} product items.")

    for product in products:
        try:
            name = product.find_element(By.CSS_SELECTOR, '.s_title_block a').text.replace(",", "")
            url = product.find_element(By.CSS_SELECTOR, '.s_title_block a').get_attribute('href')
            img_url = product.find_element(By.CSS_SELECTOR, '.product_img_link img').get_attribute('src')
            price_element = product.find_element(By.CSS_SELECTOR, '.price.st_discounted_price, .price')
            discounted_price = price_element.text

            try:
                original_price_element = product.find_element(By.CSS_SELECTOR, '.regular-price')
                original_price = original_price_element.text
            except:
                original_price = ""

            try:
                if product.find_element(By.CSS_SELECTOR, '.st_sticker_text'):
                    availability = "In Stock"
            except:
                availability = "Out of Stock"

            seller = "OnOff"
            writer.writerow(
                [img_url, name, original_price, discounted_price, url, availability, seller])

        except Exception as e:
            print(f"Error extracting data for a product: {e}")
            continue

driver.quit()
print("Data has been successfully written to 'onoff.csv'.")

