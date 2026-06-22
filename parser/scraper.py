from selenium.webdriver.common.by import By
from . import config, driver, storage

seen_links = set()

def get_element_text(ad, by, value):
    """Get the text of an element."""
    try:
        return ad.find_element(by, value).text.strip()
    except Exception:
        return None


def get_element_attr(ad, by, value, attr):
    """Get an attribute of an element."""
    try:
        return ad.find_element(by, value).get_attribute(attr)
    except Exception:
        return None


def parse_listings(driver):
    """Parse the listings on the current page."""
    ads = driver.find_elements(By.CLASS_NAME, "EntityList-item")
    listings = []

    if not ads:
        return listings, 0
    for ad in ads:
        price = get_element_text(ad, By.CLASS_NAME, "price")
        link = get_element_attr(ad, By.TAG_NAME, "a", "href")
        if not link or not link.startswith("https://www.njuskalo.hr/nekretnine/") or link in seen_links:
            continue
        seen_links.add(link)
        listings.append({"price": price, "link": link})
    return listings, len(listings)


def collect_data(pages):
    """Collect data from multiple pages."""
    all_data = []
    total_ads = 0
    empty_pages = 0
    previous_links = storage.load_previous_data()
    for page in range(1, pages):
        url = (f"https://www.njuskalo.hr/iznajmljivanje-stanova?"
               f"geo[locationIds]=1248%2C1249%2C1250%2C1251%2C1252%2C1253&"
               f"price[min]={config["parser"]["min_price"]}&"
               f"price[max]={config["parser"]["max_price"]}&"
               f"page={page}&"
               f"livingArea[max]={config["parser"]["max_square"]}")
        driver.get(url)
        data, _ = parse_listings(driver)  # Ignore ad_count
        if not data:
            empty_pages += 1
            if empty_pages >= 2:
                break
            continue
        unique_data = [ad for ad in data if ad["link"] not in previous_links]
        unique_count = len(unique_data)
        all_data.extend(unique_data)
        print(f"✅ Page {page}: {unique_count} unique listings found")
        total_ads += unique_count
        empty_pages = 0
    return all_data, total_ads