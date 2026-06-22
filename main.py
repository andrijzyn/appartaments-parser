from parser import scraper, storage, driver

if __name__ == "__main__":
    collected_data, count_ads = scraper.collect_data(100)
    storage.save_to_excel(collected_data)
    driver.quit()
    print(f"✅ Total ads collected: {count_ads}")