import argparse
import subprocess
from parser import scraper, storage, driver
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

console = Console()

if __name__ == "__main__":
    args = argparse.ArgumentParser()
    args.add_argument("-auto", action="store_true", help="Open the result file automatically after parsing")
    flags = args.parse_args()

    console.print(Rule("[bold]Njuskalo Apartment Parser[/bold]"))
    console.print()

    collected_data, count_ads = scraper.collect_data(100)
    file_path = storage.save_to_excel(collected_data)
    driver.quit()

    console.print()
    if file_path:
        console.print(Panel(
            f"[green]✓[/green] [bold]{count_ads}[/bold] new listings found\n"
            f"[green]✓[/green] Saved → [cyan]{file_path}[/cyan]",
            border_style="green",
            title="Done",
        ))
        if flags.auto:
            subprocess.Popen(
                ["xdg-open", file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
    else:
        console.print(Panel("[yellow]No new listings found.[/yellow]", border_style="yellow", title="Done"))
