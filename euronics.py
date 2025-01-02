from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import csv

options = Options()
options.add_argument("--headless")  # Disable visible browser window
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

url = "https://www.euronics.ee/telefonid/nutitelefonid/nutitelefonid/apple?f=CgN0b3AiBQhFEI8dMAQ&p=1"
driver.get(url)

with open('data_files/euronics.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(
        ['Image URL', 'Product Name', 'Original Price', 'Discount Price', 'Product URL', 'Availability',
         'Seller'])

    # Wait for products to load
    WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.product-card')))

    products = driver.find_elements(By.CSS_SELECTOR, '.product-card')
    print(f"Found {len(products)} product items.")

    for product in products:
        try:
            name = product.get_attribute('data-product-name').replace(",", "")
            original_price = ""
            discount_price = ""

            discount_old_element = product.find_elements(By.CLASS_NAME, "discount__old")
            price_container = product.find_element(By.CLASS_NAME, "price")

            if discount_old_element:
                # If product has a discount
                original_price = discount_old_element[0].text.strip().replace('\u00a0', '').replace('€', '').strip()
                price_lines = price_container.text.split('\n')
                if len(price_lines) > 1:
                    discount_price = price_lines[1].strip().replace('\u00a0', '').replace('€', '').strip()
            else:
                # If product does not have a discount
                label_element = price_container.find_elements(By.CLASS_NAME, "label")
                if label_element:
                    label_text = label_element[0].text.strip()
                    if "Hind:" in label_text:
                        original_price = price_container.text.replace(label_text, "").strip()
                        original_price = original_price.replace('\u00a0', '').replace('€', '').strip()
                discount_price = ""  # No discount price in this case

            url_element = product.find_element(By.CSS_SELECTOR, '.product-card__image-div a')
            url = url_element.get_attribute('href') if url_element else ""

            img_url_element = product.find_element(By.CSS_SELECTOR, '.product-card__image')
            img_url = img_url_element.get_attribute('src') if img_url_element else ""

            availability = "In Stock" if product.find_elements(By.CLASS_NAME, 'badge--success') else "Out of Stock"
            seller = "Euronics"

            writer.writerow([img_url, name, original_price, discount_price, url, availability, seller])

        except Exception as e:
            print(f"Error extracting data for a product: {e}")
            continue

driver.quit()
print("Data has been successfully written to 'data_files/euronics.csv'.")

