"""CLI entry point for the Njuskalo apartment listing scraper."""
import argparse
import re
import subprocess

import plotext as plt
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table


def parse_args():
    """Parse and return CLI arguments."""
    p = argparse.ArgumentParser(description="Njuskalo apartment parser")
    p.add_argument("--open", action="store_true", help="Open result file after parsing")
    p.add_argument("--iter", action="store_true", help="Retry empty pages before skipping")
    p.add_argument("--clean", action="store_true", help="Delete all previous data files")
    p.add_argument("--pages", type=int, default=100, help="Max pages to scrape (default: 100)")
    p.add_argument("--min-price", type=int, help="Override min price from config")
    p.add_argument("--max-price", type=int, help="Override max price from config")
    p.add_argument("--max-square", type=int, help="Override max square meters from config")
    p.add_argument("--graph", action="store_true", help="Show price distribution chart")
    return p.parse_args()


def main():
    """Run the scraper."""
    # pylint: disable=import-outside-toplevel
    from parser import scraper, storage, driver
    from parser import config as parser_config

    flags = parse_args()
    console = Console()

    if flags.min_price:
        parser_config["parser"]["min_price"] = flags.min_price
    if flags.max_price:
        parser_config["parser"]["max_price"] = flags.max_price
    if flags.max_square:
        parser_config["parser"]["max_square"] = flags.max_square

    console.print(Rule("[bold]Njuskalo Apartment Parser[/bold]"))
    console.print()

    if flags.clean:
        removed = storage.clean_data()
        console.print(f"[dim]Removed {removed} previous file(s)[/dim]\n")

    collected_data, count_ads = scraper.collect_data(flags.pages, retry=flags.iter)
    file_path = storage.save_to_excel(collected_data)
    driver.quit()

    if collected_data:
        console.print()
        table = Table(show_lines=True)
        table.add_column("Price", style="bold", no_wrap=True)
        table.add_column("Link", style="cyan")
        for item in collected_data:
            table.add_row(item["price"] or "—", item["link"])
        console.print(table)

    console.print()
    if file_path:
        console.print(Panel(
            f"[green]✓[/green] [bold]{count_ads}[/bold] new listings found\n"
            f"[green]✓[/green] Saved → [cyan]{file_path}[/cyan]",
            border_style="green",
            title="Done",
        ))
        if flags.open:
            with subprocess.Popen(
                ["xdg-open", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            ):
                pass
    else:
        console.print(Panel(
            "[yellow]No new listings found.[/yellow]",
            border_style="yellow",
            title="Done",
        ))

    if flags.graph:
        prices = []
        for item in storage.load_full_data():
            if item["price"]:
                match = re.search(r"\d+", item["price"].replace(".", "").replace(",", ""))
                if match:
                    prices.append(int(match.group()))
        if prices:
            bucket_start = (min(prices) // 100) * 100
            bucket_end = ((max(prices) // 100) + 1) * 100
            x_values, counts = [], []
            for start in range(bucket_start, bucket_end, 100):
                x_values.append(start + 50)
                counts.append(sum(1 for p in prices if start <= p < start + 100))

            console.print()
            plt.clf()
            plt.plot(x_values, counts, marker="braille")
            plt.title("Price distribution per 100€")
            plt.ylabel("Price range (€)")
            plt.xlabel("Listings")
            print(plt.build())

        console.input("\n[dim]Press Enter to exit...[/dim]")


if __name__ == "__main__":
    main()
