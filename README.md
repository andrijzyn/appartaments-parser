That was an interesting task during the hardest period of my life.
I don't like looking for apartments that suit my budget and prioritized location.
Also because an internal Njuškalo filters are garbage.
The data requires additional post-processing.

I mainly used Selenium, a Firefox library for automated website testing.
It closes all antibot windows and scrapes data from the advertisement divs.
That was a problem for me because it's a bit broken in Njuškalo.

Additional Python libraries clean the data from other advertisements.
OpenPyXL converts all that data into an elegant .XLSX file.
The file updates after each execution of the script.

---

## Setup

```bash
pip install -r requirements.txt
```

Configure search parameters in `config.toml`:

```toml
[parser]
min_price = 200   # minimum rent (€)
max_price = 400   # maximum rent (€)
max_square = 45   # maximum area (m²)

[directories]
save = "data"     # output folder
```

## Usage

```bash
python main.py [options]
```

| Flag | Description |
|---|---|
| `--pages N` | Scrape up to N pages (default: 100) |
| `--min-price N` | Override minimum price from config |
| `--max-price N` | Override maximum price from config |
| `--max-square N` | Override maximum area from config |
| `--clean` | Delete all previous data files before running |
| `--graph` | Show price distribution chart in terminal |
| `--iter` | Retry empty pages before skipping |
| `--open` | Open the result file automatically when done |

## Examples

```bash
# Basic run
python main.py

# Quick scan of first 5 pages with a wider budget
python main.py --pages 5 --max-price 500

# Full re-scrape from scratch with chart
python main.py --clean --graph

# Check for updates and open result automatically
python main.py --open
```

## Output

Results are saved as `.xlsx` files in the `data/` folder, named by date and time (e.g. `njuskalo_listings 22 June 14-30.xlsx`). Each file contains two columns — **Price** and **Link** — sorted by price ascending. Links are clickable hyperlinks (Ctrl+click to open in browser).

On repeated runs, only new listings not seen in any previous file are saved. The script stops automatically when it finds no new listings across 2 consecutive pages.
