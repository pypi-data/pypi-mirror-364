"""
CV Toolbox CLI - Main entry point for the command line interface.

This module provides the main CLI interface for the CV Toolbox using Typer.
"""

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from lcvtoolbox.vision.geometry.primitives.point import Point3D
from lcvtoolbox.vision.geometry.primitives.points_array import Points3DArray

app = typer.Typer(
    name="cv-toolbox",
    help="Computer Vision Toolbox for road infrastructure analysis",
    rich_markup_mode="rich",
)
console = Console()


@app.command()
def hello(
    name: str | None = typer.Argument(None, help="Name to greet"),
    count: int = typer.Option(1, "--count", "-c", help="Number of greetings"),
    formal: bool = typer.Option(False, "--formal", "-f", help="Use formal greeting"),
) -> None:
    """
    Say hello to someone! 👋

    This is a simple hello world command to demonstrate the CV Toolbox CLI.
    """
    if name is None:
        name = "World"

    greeting = "Good day" if formal else "Hello"

    for i in range(count):
        if count > 1:
            rprint(f"[bold green]{greeting}[/bold green] [blue]{name}[/blue] [dim]({i + 1})[/dim]! 🚀")
        else:
            rprint(f"[bold green]{greeting}[/bold green] [blue]{name}[/blue]! 🚀")


@app.command()
def version() -> None:
    """Show the version of CV Toolbox."""
    rprint("[bold blue]CV Toolbox[/bold blue] version [green]1.0.0[/green]")
    rprint("Computer vision toolbox for road infrastructure analysis")


@app.command()
def demo() -> None:
    """
    Demonstrate CV Toolbox spatial primitives.

    Shows basic usage of Point and Points classes.
    """
    console.print("\n[bold blue]🎯 CV Toolbox Spatial Primitives Demo[/bold blue]\n")

    # Point demo
    console.print("[bold yellow]📍 Point Operations:[/bold yellow]")
    p1 = Point3D(1, 2, 3)
    p2 = Point3D(4, 5, 6)

    table = Table(title="Point Operations Results")
    table.add_column("Operation", style="cyan")
    table.add_column("Result", style="magenta")

    table.add_row("p1", str(p1))
    table.add_row("p2", str(p2))
    table.add_row("Distance", f"{p1.distance_to(p2):.2f}")
    table.add_row("Midpoint", str(p1.midpoint(p2)))
    table.add_row("p1 + p2", str(p1 + p2))
    table.add_row("p1 * 2", str(p1 * 2))

    console.print(table)

    # Points collection demo
    console.print("\n[bold yellow]📊 Points Collection:[/bold yellow]")
    points = Points3DArray([Point3D(1, 2, 3), Point3D(4, 5, 6), Point3D(7, 8, 9)])

    points_table = Table(title="Points Collection Results")
    points_table.add_column("Property", style="cyan")
    points_table.add_column("Value", style="magenta")

    points_table.add_row("Collection", str(points))
    points_table.add_row("Size", str(points.size))
    points_table.add_row("Centroid", str(points.centroid))
    points_table.add_row("Bounds", f"{points.bounds[0]} to {points.bounds[1]}")

    console.print(points_table)

    # Factory methods demo
    console.print("\n[bold yellow]🏭 Factory Methods:[/bold yellow]")

    factory_table = Table(title="Factory Methods Examples")
    factory_table.add_column("Method", style="cyan")
    factory_table.add_column("Description", style="green")
    factory_table.add_column("Size", style="magenta")

    circle = Points3DArray.circle(Point3D(0, 0), 1.0, 8)
    line = Points3DArray.line(Point3D(0, 0, 0), Point3D(10, 10, 10), 5)
    grid = Points3DArray.grid((0, 2), (0, 2), 3, 3)

    factory_table.add_row("Circle", "8 points in a circle", str(circle.size))
    factory_table.add_row("Line", "5 points along a line", str(line.size))
    factory_table.add_row("Grid", "3x3 grid of points", str(grid.size))

    console.print(factory_table)

    console.print("\n[bold green]✅ Demo completed successfully![/bold green]")


def main() -> None:
    """Main entry point for the CV Toolbox CLI."""
    app()


if __name__ == "__main__":
    main()
