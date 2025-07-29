CLI Guide
=========

The lcvtoolbox command-line interface provides convenient access to common functionality.

Installation
------------

After installing lcvtoolbox, the CLI is available as both ``cv-toolbox`` and ``toolbox`` commands:

.. code-block:: bash

   # Check installation
   cv-toolbox --version
   
   # Or use the shorter alias
   toolbox --version

Basic Commands
--------------

Help
~~~~

Get help on available commands:

.. code-block:: bash

   cv-toolbox --help
   
   # Get help for specific command
   cv-toolbox demo --help

Version
~~~~~~~

Display version information:

.. code-block:: bash

   cv-toolbox version

Demo
~~~~

Run a demonstration of spatial primitives:

.. code-block:: bash

   cv-toolbox demo

This shows examples of:
- Point operations
- Point collections
- Factory methods for creating geometric shapes

Creating Custom Commands
------------------------

You can extend the CLI with custom commands:

.. code-block:: python

   # my_commands.py
   import typer
   from lcvtoolbox.cli.main import app

   @app.command()
   def process_images(
       input_dir: str = typer.Argument(..., help="Input directory"),
       output_dir: str = typer.Argument(..., help="Output directory"),
       quality: int = typer.Option(85, "--quality", "-q", help="JPEG quality"),
   ):
       """Process images in a directory."""
       from pathlib import Path
       from lcvtoolbox.vision.encoding import encode_image_to_string
       from PIL import Image
       
       input_path = Path(input_dir)
       output_path = Path(output_dir)
       output_path.mkdir(exist_ok=True)
       
       for img_file in input_path.glob("*.jpg"):
           img = Image.open(img_file)
           encoded = encode_image_to_string(img, quality=quality)
           # Process encoded image...
           typer.echo(f"Processed {img_file.name}")

Using Rich for Output
---------------------

The CLI uses Rich for beautiful terminal output:

.. code-block:: python

   from rich.console import Console
   from rich.table import Table
   from rich.progress import track

   console = Console()

   @app.command()
   def analyze_dataset(path: str):
       """Analyze a dataset with progress tracking."""
       files = list(Path(path).glob("**/*.jpg"))
       
       table = Table(title="Dataset Analysis")
       table.add_column("Metric", style="cyan")
       table.add_column("Value", style="magenta")
       
       total_size = 0
       for file in track(files, description="Analyzing..."):
           total_size += file.stat().st_size
       
       table.add_row("Total Files", str(len(files)))
       table.add_row("Total Size", f"{total_size / 1024 / 1024:.2f} MB")
       
       console.print(table)

Command Options
---------------

Common patterns for command options:

.. code-block:: python

   @app.command()
   def convert(
       # Required arguments
       input_file: Path = typer.Argument(..., help="Input file path"),
       
       # Optional with default
       format: str = typer.Option("JPEG", "--format", "-f", help="Output format"),
       
       # Boolean flag
       verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
       
       # Multiple values
       labels: list[str] = typer.Option([], "--label", "-l", help="Labels to process"),
       
       # Enum choices
       quality: str = typer.Option(
           "balanced",
           "--quality",
           "-q",
           help="Quality preset",
           case_sensitive=False,
           callback=lambda x: x.lower()
       ),
   ):
       """Convert images with various options."""
       if verbose:
           typer.echo(f"Converting {input_file}")

Configuration Files
-------------------

Loading configuration from files:

.. code-block:: python

   import json
   from pathlib import Path

   @app.command()
   def process_with_config(
       config: Path = typer.Option(
           "config.json",
           "--config",
           "-c",
           help="Configuration file"
       ),
   ):
       """Process using configuration file."""
       if not config.exists():
           typer.echo(f"Config file not found: {config}", err=True)
           raise typer.Exit(1)
       
       with open(config) as f:
           settings = json.load(f)
       
       # Use settings...
       typer.echo(f"Loaded config from {config}")

Error Handling
--------------

Proper error handling in CLI commands:

.. code-block:: python

   @app.command()
   def risky_operation(path: str):
       """Command with error handling."""
       try:
           # Risky operation
           result = process_path(path)
       except FileNotFoundError:
           typer.echo(f"Error: File not found: {path}", err=True)
           raise typer.Exit(1)
       except PermissionError:
           typer.echo(f"Error: Permission denied: {path}", err=True)
           raise typer.Exit(2)
       except Exception as e:
           typer.echo(f"Unexpected error: {e}", err=True)
           raise typer.Exit(3)
       
       typer.echo(f"Success: {result}")

Interactive Mode
----------------

Create interactive commands:

.. code-block:: python

   @app.command()
   def interactive_setup():
       """Interactive setup wizard."""
       # Ask for confirmation
       if not typer.confirm("Do you want to continue?"):
           raise typer.Abort()
       
       # Text input
       name = typer.prompt("What's your project name?")
       
       # Password input
       token = typer.prompt("Enter your API token", hide_input=True)
       
       # Choice selection
       format = typer.prompt(
           "Choose format",
           type=typer.Choice(["JPEG", "PNG", "WebP"]),
           default="JPEG"
       )
       
       typer.echo(f"Setting up project: {name}")

Progress Bars
-------------

Show progress for long operations:

.. code-block:: python

   from rich.progress import Progress, SpinnerColumn, TextColumn

   @app.command()
   def batch_process(directory: str):
       """Process files with progress bar."""
       files = list(Path(directory).glob("*.jpg"))
       
       with Progress(
           SpinnerColumn(),
           TextColumn("[progress.description]{task.description}"),
           transient=True,
       ) as progress:
           task = progress.add_task("Processing...", total=len(files))
           
           for file in files:
               # Process file
               process_file(file)
               progress.advance(task)

Best Practices
--------------

1. **Use Type Hints**: Always use type hints for better IDE support and validation
2. **Provide Help Text**: Add help text to all arguments and options
3. **Handle Errors Gracefully**: Use proper exit codes and error messages
4. **Use Rich for Output**: Leverage Rich for tables, progress bars, and styled output
5. **Validate Input**: Check file existence, permissions, and formats before processing
6. **Support Configuration Files**: Allow users to save and reuse complex configurations
7. **Make Commands Composable**: Design commands that can work together in pipelines

Example: Complete CLI Application
---------------------------------

Here's a complete example combining multiple concepts:

.. code-block:: python

   # advanced_cli.py
   import typer
   from pathlib import Path
   from rich.console import Console
   from rich.table import Table
   from lcvtoolbox.vision.encoding import encode_image_to_string, CompressionPreset
   from PIL import Image

   app = typer.Typer(help="Advanced image processing CLI")
   console = Console()

   @app.command()
   def batch_encode(
       input_dir: Path = typer.Argument(..., help="Input directory"),
       output_dir: Path = typer.Argument(..., help="Output directory"),
       preset: str = typer.Option(
           "balanced",
           "--preset", "-p",
           help="Compression preset",
           case_sensitive=False
       ),
       dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be done"),
   ):
       """Batch encode images with presets."""
       # Validate preset
       try:
           compression_preset = CompressionPreset[preset.upper()]
       except KeyError:
           typer.echo(f"Invalid preset: {preset}", err=True)
           raise typer.Exit(1)
       
       # Create output directory
       if not dry_run:
           output_dir.mkdir(parents=True, exist_ok=True)
       
       # Process images
       images = list(input_dir.glob("*.jpg")) + list(input_dir.glob("*.png"))
       
       if not images:
           typer.echo("No images found!", err=True)
           raise typer.Exit(1)
       
       # Show summary table
       table = Table(title="Batch Encoding Summary")
       table.add_column("File", style="cyan")
       table.add_column("Size", style="magenta")
       table.add_column("Status", style="green")
       
       for img_path in images:
           if dry_run:
               table.add_row(img_path.name, f"{img_path.stat().st_size / 1024:.1f} KB", "Would process")
           else:
               try:
                   img = Image.open(img_path)
                   encoded = encode_image_to_string(img, preset=compression_preset)
                   output_path = output_dir / f"{img_path.stem}_encoded.txt"
                   output_path.write_text(encoded)
                   table.add_row(img_path.name, f"{img_path.stat().st_size / 1024:.1f} KB", "✓ Processed")
               except Exception as e:
                   table.add_row(img_path.name, "Error", f"✗ {str(e)}")
       
       console.print(table)

   if __name__ == "__main__":
       app()
