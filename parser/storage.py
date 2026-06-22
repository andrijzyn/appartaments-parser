import re, os
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font
from rich.console import Console
from . import config

_console = Console()

save_dir: str = config["directories"]["save"]
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
        _console.print("[dim]No previous data found.[/dim]")
        return set()
    last_file = os.path.join(folder, files[0])
    try:
        wb = load_workbook(last_file, data_only=True)
        ws = wb.active
        assert ws is not None
        previous_links: set[str] = set()
        for row in ws.iter_rows(min_row=2, values_only=True):
            cell = row[1]
            if isinstance(cell, str):
                previous_links.add(cell)
        wb.close()
        _console.print(f"[dim]Loaded {len(previous_links)} previous listings from {last_file}[/dim]")
        return previous_links
    except Exception as e:
        _console.print(f"[yellow]⚠ Failed to load previous data: {e}[/yellow]")
        return set()


def save_to_excel(data):
    """Save the collected data to an Excel file."""
    if not data:
        return None
    date_str = datetime.now().strftime("%d %B %H-%M")
    folder = save_dir
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"njuskalo_listings {date_str}.xlsx")

    def extract_price(entry):
        price = entry["price"]
        if price is None:
            return float("inf")
        match = re.search(r"\d+", price.replace(".", "").replace(",", ""))
        return int(match.group()) if match else float("inf")

    data.sort(key=extract_price)
    wb = Workbook()
    ws = wb.active
    assert ws is not None
    ws.append(["Price", "Link"])
    link_style = Font(color="0563C1", underline="single")
    for item in data:
        ws.append([item["price"], item["link"]])
        cell = ws.cell(row=ws.max_row, column=2)
        cell.hyperlink = item["link"]
        cell.font = link_style
    wb.save(file_path)
    return file_path