import time
from datetime import datetime

import typer
from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.style import Style
from rich.theme import Theme as RichTheme

from constants import DEFAULT_THEME, THEMES, Theme

console = Console()


def run_pomodoro(interval: int, theme: Theme):
    """Runs the Pomodoro timer for the specified interval."""
    console.print(
        "🚀 Starting Pomodoro timer...", style=f"bold {theme['TEXT_COLOUR']}"
    )

    progress_theme = RichTheme(
        {
            "progress.elapsed": theme["TEXT_COLOUR"],
            "progress.percentage": theme["ALT"],
        }
    )

    with Progress(
        SpinnerColumn(style=Style(color=theme["ALT"])),
        TextColumn(
            "[progress.description]{task.description}",
        ),
        BarColumn(
            style=Style(color=theme["START"]),
            complete_style=Style(color=theme["END"]),
            finished_style=Style(color=theme["START"]),
        ),
        TextColumn("•"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TimeElapsedColumn(),
        console=Console(theme=progress_theme),
    ) as progress:
        task = progress.add_task(
            f"[{theme['TEXT_COLOUR']}]Pomodoro in progress...", total=interval * 60
        )
        for _ in range(interval * 60):
            time.sleep(1)
            progress.update(task, advance=1)

    completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    console.print(
        f"[bold {theme['END']}]🎉 The current Pomodoro interval has completed - {completion_time}[/]"
    )


def pomodoro(
    interval: int = typer.Option(
        ...,
        "--interval",
        "-i",
        help="The Pomodoro interval in minutes. (Required)",
    ),
    theme: str = typer.Option(
        "default",
        "--theme",
        "-t",
        help=f"The color theme to use. Available options: {', '.join(THEMES.keys())}",
    ),
):
    """A simple Pomodoro CLI tool."""
    selected_theme = THEMES.get(theme, DEFAULT_THEME)
    run_pomodoro(interval, selected_theme)


def main():
    """Main entry point for the application."""
    typer.run(pomodoro)


if __name__ == "__main__":
    main()
