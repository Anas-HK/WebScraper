import csv
import time
import json
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class KijijiAutosScraper:
    def __init__(self, driver_path, headless=True):
        self.driver_path = driver_path
        self.setup_driver(headless)
        self.base_url = "https://www.kijijiautos.ca/cars/best-first-cars/"

    def setup_driver(self, headless):
        options = Options()
        options.use_chromium = True
        if headless:
            options.add_argument('--headless')
        self.driver = webdriver.Edge(executable_path=self.driver_path)
        self.wait = WebDriverWait(self.driver, 10)

    def scroll_page(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        for _ in range(4):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def get_image(self, listing):
        try:
            img_element = listing.find_element(By.CSS_SELECTOR, 'div.b1E1YI img.q1E1YI')
            img_url = img_element.get_attribute('src') or img_element.get_attribute('data-src')
            return img_url or "N/A"
        except Exception as e:
            return "N/A"

    def get_price(self, listing):
        price_selectors = [
            'span[data-testid="searchResultItemPrice"]',
            'div.g3uM7V.gcN7dZ div.h3uM7V span.G2jAym',
            'div[data-testid="VehicleListItem-price"] div.h3uM7V span.G2jAym'
        ]
        for selector in price_selectors:
            try:
                price_element = listing.find_element(By.CSS_SELECTOR, selector)
                if price_element and price_element.is_displayed():
                    return price_element.text.strip()
            except NoSuchElementException:
                continue
        
        return "N/A"

    def scrape_page(self):
        self.driver.get(self.base_url)
        time.sleep(3)
        self.scroll_page()

        listings = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="SearchResultListItem"]'))
        )

        data = []
        for listing in listings[:100]:
            try:
                title = listing.find_element(By.CSS_SELECTOR, 'h2.G2jAym').text.strip()
                price = self.get_price(listing)
                img_url = self.get_image(listing)

                data.append({'title': title, 'price': price, 'img_url': img_url})
                print(f"Scraped: {title} - {price} - {img_url}")

            except Exception as e:
                print(f"Error processing listing: {e}")
                continue

        return data

    def save_data_to_json(self, data):
        with open('kijiji_autos_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(data)} listings to kijiji_autos_data.json")

    def save_data_to_csv(self, data):
        with open('kijiji_autos_data.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['title', 'price', 'img_url'])
            writer.writeheader()
            writer.writerows(data)
        print(f"Saved {len(data)} listings to kijiji_autos_data.csv")

    def close(self):
        self.driver.quit()


def main():
    driver_path = r"C:/Users/anash/OneDrive/Desktop/driver/msedgedriver.exe"
    scraper = KijijiAutosScraper(driver_path, headless=False)

    try:
        data = scraper.scrape_page()
        scraper.save_data_to_json(data)
        scraper.save_data_to_csv(data)
    except Exception as e:
        print(f"Critical error: {str(e)}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
