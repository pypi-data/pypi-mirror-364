#!/usr/bin/env python3

import pyautogui
import time
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, BarColumn, TextColumn
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.align import Align

# Configuration
VERSION = "0.3.0"  # This will be automatically updated by the semver workflow
SQUARE_SIZE = 100
MOVE_DURATION = 0.25
INTERVAL = 60

# Enable safety feature (for emergency stop: move mouse to corner)
pyautogui.FAILSAFE = True

# Initialize rich console
console = Console()


def move_in_square():
    # Save current position
    start_x, start_y = pyautogui.position()

    console.print(
        f"🎯 Starting square movement from position [bold cyan]({start_x}, {start_y})[/bold cyan]")

    # Create a progress bar for the square movement
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
        transient=True
    ) as progress:

        task = progress.add_task("Moving in square pattern...", total=4)

        # Move right
        progress.update(task, description="Moving right ➡️")
        pyautogui.moveTo(start_x + SQUARE_SIZE, start_y,
                         duration=MOVE_DURATION, tween=pyautogui.easeInOutQuad)
        progress.advance(task)

        # Move down
        progress.update(task, description="Moving down ⬇️")
        pyautogui.moveTo(start_x + SQUARE_SIZE, start_y + SQUARE_SIZE,
                         duration=MOVE_DURATION, tween=pyautogui.easeInOutQuad)
        progress.advance(task)

        # Move left
        progress.update(task, description="Moving left ⬅️")
        pyautogui.moveTo(start_x, start_y + SQUARE_SIZE,
                         duration=MOVE_DURATION, tween=pyautogui.easeInOutQuad)
        progress.advance(task)

        # Move up (back to start)
        progress.update(task, description="Moving up ⬆️")
        pyautogui.moveTo(start_x, start_y,
                         duration=MOVE_DURATION, tween=pyautogui.easeInOutQuad)
        progress.advance(task)

    console.print("✅ [bold green]Square movement completed[/bold green]")


def wait_with_progress(seconds):
    """Wait for specified seconds with a progress bar"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        TextColumn("/ {task.fields[total_time]}s"),
        console=console
    ) as progress:

        task = progress.add_task(
            "⏳ Waiting until next movement...",
            total=seconds,
            total_time=seconds
        )

        for i in range(seconds):
            time.sleep(1)
            progress.advance(task, 1)


def start_patrol():
    # Create a beautiful startup panel
    startup_text = Text.assemble(
        ("🐭 MousePatrol ", "bold magenta"),
        (f"v{VERSION}", "dim"),
        ("\n\nKeeping your system active by moving the mouse in a set interval", ""),
        ("\n\n📋 Configuration:", "bold"),
        (f"\n  • Shape: Square", "cyan"),
        (f"\n  • Interval: {INTERVAL}s", "cyan"),
        ("\n\n🛡️  Safety Features:", "bold"),
        ("\n  • Press Ctrl+C to exit", "yellow"),
        ("\n  • Move mouse to upper-left corner for emergency stop", "yellow"),
    )

    startup_panel = Panel(
        Align.center(startup_text),
        border_style="bright_blue",
        padding=(1, 2)
    )

    console.print()
    console.print(startup_panel)
    console.print()

    try:
        # Initial 30-second delay before starting mouse movements
        console.print("🚀 [bold yellow]Starting in 30 seconds...[/bold yellow]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            TextColumn("/ 30s"),
            console=console
        ) as progress:

            task = progress.add_task(
                "⏳ Preparing to start mouse patrol...",
                total=30
            )

            for i in range(30):
                time.sleep(1)
                progress.advance(task, 1)

        console.print("✅ [bold green]Starting mouse patrol now![/bold green]")
        console.print()

        cycle_count = 0
        while True:
            cycle_count += 1

            # Show cycle header
            console.rule(f"[bold blue]Cycle #{cycle_count}[/bold blue]")

            move_in_square()

            wait_with_progress(INTERVAL)
            console.print()

    except KeyboardInterrupt:
        console.print("\n🛑 [bold red]Program terminated by user.[/bold red]")
        console.print("👋 [dim]Thanks for using MousePatrol![/dim]")
    except pyautogui.FailSafeException:
        console.print(
            "\n🚨 [bold red]Emergency stop: Mouse moved to corner.[/bold red]")
        console.print("👋 [dim]MousePatrol stopped safely.[/dim]")


def main():
    start_patrol()


if __name__ == "__main__":
    main()
