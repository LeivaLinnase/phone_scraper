from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

driver.get('https://www.klick.ee/telefonid-ja-lisad/mobiiltelefonid/nutitelefonid?tootja=5951')


def load_more_products():  # Click 'KUVA ROHKEM' button to load more products
    while True:
        try:
            show_more_button = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="category"]/div/div/div[2]/div[3]/nav/div/span'))
            )
            driver.execute_script("arguments[0].scrollIntoView();", show_more_button)
            driver.execute_script("arguments[0].click();", show_more_button)
            time.sleep(5)  # Allow new products to load
        except Exception as e:
            print(f"Error clicking 'KUVA ROHKEM' button: {e}")
            break  # Exit loop if no more "KUVA ROHKEM" button


load_more_products()

# Wait for product elements to load
WebDriverWait(driver, 30).until(
    EC.presence_of_all_elements_located((By.CLASS_NAME, 'product'))
)

products_before = driver.find_elements(By.CLASS_NAME, 'product')
print(f"Number of products before extraction: {len(products_before)}")

data = []
products = driver.find_elements(By.CLASS_NAME, 'product')
for product in products:
    try:
        name = product.find_element(By.CLASS_NAME, 'product-name').text.strip().replace(",", "")
        discounted_price_text = product.find_element(By.CLASS_NAME, 'price-special').text.strip() if \
            product.find_elements(By.CLASS_NAME, 'price-special') else None

        discounted_price = float(
            discounted_price_text.replace('€', '').replace(',', '.').strip()) if discounted_price_text else None

        discount_text = product.find_element(By.CLASS_NAME, 'price-discount').text.strip() if \
            product.find_elements(By.CLASS_NAME, 'price-discount') else None

        discount_amount = float(
            discount_text.replace('-', '').replace('€', '').replace(',', '.').strip()) if discount_text else 0

        if discounted_price is not None:
            original_price = discounted_price + discount_amount
        else:
            original_price_text = product.find_element(By.CLASS_NAME, 'price').text.strip()
            original_price = float(
                original_price_text.replace('€', '').replace(',', '.').strip()) if original_price_text else None

        url = product.find_element(By.TAG_NAME, 'a').get_attribute('href')
        image_url = product.find_element(By.TAG_NAME, 'img').get_attribute('srcset').split(',')[0].split(' ')[0]

        data.append({
            'Image URL': image_url,
            'Product Name': name,
            'Original Price': original_price,
            'Discount Price': discounted_price,
            'Product URL': url

        })
    except Exception as e:
        print(f"Error extracting data from product: {e}")
        continue

print(f"Number of products after extraction: {len(data)}")
df = pd.DataFrame(data)

# Add columns for availability and seller
df['Availability'] = 'Out of Stock'
df['Seller'] = 'Klick'

# Scrape availability details for each product
for index, row in df.iterrows():
    product_url = row['Product URL']
    try:
        driver.get(product_url)

        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h1'))
        )

        availability_buttons = driver.find_elements(By.XPATH, "//span[contains(text(), 'Saadavus poodides')]")
        if availability_buttons:
            df.at[index, 'Availability'] = 'In Stock'
    except Exception as e:
        print(f"Error checking stock for {product_url}: {e}")


df.to_csv('data_files/klick.csv', index=False)
print("Data saved to: data_files/klick.csv")

driver.quit()
