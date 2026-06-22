import re, os
from datetime import datetime
from openpyxl import Workbook, load_workbook
from . import config

save_dir = config["directories"]["save"]
os.makedirs(save_dir, exist_ok=True)

def get_latest_file():
    """Get the latest Excel file from the save directory."""
    files = [f for f in os.listdir(save_dir) if f.endswith(".xlsx")]
    if not files:
        return None
    files.sort(key=lambda x: os.path.getmtime(os.path.join(save_dir, x)), reverse=True)
    return os.path.join(save_dir, files[0])


def load_previous_data():
    """Load previously saved data from Excel files."""
    folder = save_dir
    files = sorted([f for f in os.listdir(folder) if f.endswith(".xlsx")],
                   key=lambda f: os.path.getmtime(os.path.join(folder, f)),
                   reverse=True)
    if not files:
        print("ℹ️ No previous data found.")
        return set()
    last_file = os.path.join(folder, files[0])
    try:
        wb = load_workbook(last_file, data_only=True)
        ws = wb.active
        previous_links = {row[1] for row in ws.iter_rows(min_row=2, values_only=True) if row[1]}
        wb.close()
        print(f"ℹ️ Loaded {len(previous_links)} previous listings from {last_file}")
        return previous_links
    except Exception as e:
        print(f"⚠️ Failed to load previous data: {e}")
        return set()


def save_to_excel(data):
    """Save the collected data to an Excel file."""
    if not data:
        print("ℹ️ No data to save.")
        return
    date_str = datetime.now().strftime("%d %B %H-%M")
    folder = save_dir
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"njuskalo_listings {date_str}.xlsx")

    def extract_price(item):
        price = item["price"]
        if price is None:
            return float("inf")  # or some large number to handle missing prices
        match = re.search(r"\d+", price.replace(".", "").replace(",", ""))
        return int(match.group()) if match else float("inf")

    data.sort(key=extract_price)
    wb = Workbook()
    ws = wb.active
    ws.append(["Price", "Link"])
    for item in data:
        ws.append([item["price"], item["link"]])
    wb.save(file_path)
    print(f"✅ Data saved in {file_path}")