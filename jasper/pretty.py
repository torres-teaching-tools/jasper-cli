from rich.console import Console
from rich.table import Table
from rich import box

console = Console()

def print_status(message, success=True):
    prefix = "[green]✓[/green]" if success else "[red]✗[/red]"
    console.print(f"{prefix} {message}")

def show_table(data, title="Badge Progress"):
    table = Table(title=title, box=box.SIMPLE_HEAVY)
    if not data:
        console.print("[yellow]No data to display[/yellow]")
        return

    for key in data[0]:
        table.add_column(str(key), style="cyan")

    for row in data:
        table.add_row(*[str(row[k]) for k in row])
    console.print(table)
