import argparse
import subprocess

arg_parser = argparse.ArgumentParser(description="Njuskalo apartment parser")
arg_parser.add_argument("--open", action="store_true", help="Open result file after parsing")
arg_parser.add_argument("--iter", action="store_true", help="Retry empty pages before skipping")
arg_parser.add_argument("--clean", action="store_true", help="Delete all previous data files before running")
arg_parser.add_argument("--pages", type=int, default=100, help="Max pages to scrape (default: 100)")
arg_parser.add_argument("--min-price", type=int, help="Override min price from config")
arg_parser.add_argument("--max-price", type=int, help="Override max price from config")
arg_parser.add_argument("--max-square", type=int, help="Override max square meters from config")
flags = arg_parser.parse_args()

from parser import scraper, storage, driver
from parser import config as parser_config
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

console = Console()

if __name__ == "__main__":
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
            subprocess.Popen(
                ["xdg-open", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
    else:
        console.print(Panel("[yellow]No new listings found.[/yellow]", border_style="yellow", title="Done"))
