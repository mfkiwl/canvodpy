"""
CLI for canvodpy configuration management.

Provides commands for:
- Initializing configuration files from templates
- Validating configuration
- Viewing current configuration
- Editing configuration files
"""

import shutil
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .models import ProcessingConfig, SidsConfig, SitesConfig


def find_monorepo_root() -> Path:
    """Find the monorepo root by looking for a .git directory.

    Returns
    -------
    Path
        Monorepo root directory.

    Raises
    ------
    RuntimeError
        If the monorepo root cannot be found.
    """
    current = Path.cwd().resolve()

    # Walk up directory tree looking for .git
    for parent in [current] + list(current.parents):
        if (parent / ".git").exists():
            return parent

    # Fallback: if this file is in
    # packages/canvod-utils/src/canvod/utils/config/cli.py then monorepo root is
    # 7 levels up.
    try:
        cli_file = Path(__file__).resolve()
        # cli.py -> config -> utils -> canvod -> src -> canvod-utils ->
        # packages -> root.
        monorepo_root = cli_file.parent.parent.parent.parent.parent.parent.parent
        if (monorepo_root / ".git").exists():
            return monorepo_root
    except Exception:
        pass

    raise RuntimeError("Cannot find monorepo root (no .git directory found)")


# Main app
main_app = typer.Typer(
    name="canvodpy",
    help="canvodpy CLI tools",
    no_args_is_help=True,
)

# Config subcommand
config_app = typer.Typer(
    name="config",
    help="Configuration management",
    no_args_is_help=True,
)

console = Console()

# Always use monorepo root config directory
try:
    MONOREPO_ROOT = find_monorepo_root()
    DEFAULT_CONFIG_DIR = MONOREPO_ROOT / "config"
except RuntimeError:
    # Fallback if we can't find monorepo root
    DEFAULT_CONFIG_DIR = Path.cwd() / "config"

CONFIG_DIR_OPTION = typer.Option(
    "--config-dir",
    "-c",
    help="Configuration directory",
)


@config_app.command()
def init(
    config_dir: Annotated[Path, CONFIG_DIR_OPTION] = DEFAULT_CONFIG_DIR,
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing files",
    ),
) -> None:
    """Initialize configuration files from templates.

    Creates:
      - config/processing.yaml
      - config/sites.yaml
      - config/sids.yaml

    Parameters
    ----------
    config_dir : Path
        Directory where configuration files are created.
    force : bool
        Overwrite existing files.

    Returns
    -------
    None
    """
    console.print("\n[bold]Initializing canvodpy configuration...[/bold]\n")

    # Create config directory
    config_dir.mkdir(parents=True, exist_ok=True)

    # Get template directory (from monorepo root)
    try:
        monorepo_root = find_monorepo_root()
        template_dir = monorepo_root / "config"
    except RuntimeError:
        # Fallback to path calculation if monorepo root not found
        template_dir = (
            Path(__file__).parent.parent.parent.parent.parent.parent.parent / "config"
        )

    if not template_dir.exists():
        console.print(
            f"[red]❌ Template directory not found: {template_dir}[/red]",
        )
        console.print("\nMake sure you're running from the repository root.")
        raise typer.Exit(1)

    files_created = []
    files_skipped = []

    # Copy templates
    templates = [
        ("processing.yaml.example", config_dir / "processing.yaml"),
        ("sites.yaml.example", config_dir / "sites.yaml"),
        ("sids.yaml.example", config_dir / "sids.yaml"),
    ]

    for template_name, dest_path in templates:
        template_path = template_dir / template_name

        if dest_path.exists() and not force:
            files_skipped.append(dest_path)
            continue

        if template_path.exists():
            shutil.copy(template_path, dest_path)
            files_created.append(dest_path)
        else:
            console.print(f"[yellow]⚠️  Template not found: {template_path}[/yellow]")

    # Show results
    if files_created:
        console.print("[green]✓ Created:[/green]")
        for f in files_created:
            console.print(f"  {f}")

    if files_skipped:
        console.print("\n[yellow]⊘ Skipped (already exist):[/yellow]")
        for f in files_skipped:
            console.print(f"  {f}")
        console.print("\n  Use --force to overwrite")

    # Next steps
    console.print("\n[bold]Next steps:[/bold]")
    console.print("  1. Edit config/processing.yaml:")
    console.print("     - Set nasa_earthdata_acc_mail (optional, for NASA CDDIS)")
    console.print("  2. Edit config/sites.yaml with your research sites")
    console.print("     - Set gnss_site_data_root for each site")
    console.print("  3. Run: canvodpy config validate\n")


@config_app.command()
def validate(
    config_dir: Annotated[Path, CONFIG_DIR_OPTION] = DEFAULT_CONFIG_DIR,
) -> None:
    """Validate configuration files.

    Parameters
    ----------
    config_dir : Path
        Directory containing config files.

    Returns
    -------
    None
    """
    from .loader import load_config

    console.print("\n[bold]Validating configuration...[/bold]\n")

    try:
        config = load_config(config_dir)
        console.print("[green]✓ Configuration is valid![/green]\n")

        # Show summary
        console.print(f"  Sites: {len(config.sites.sites)}")
        for name in config.sites.sites.keys():
            console.print(f"    - {name}")

        console.print(f"\n  SID mode: {config.sids.mode}")
        console.print(f"  Agency: {config.processing.aux_data.agency}")

        # Show site data roots
        for name, site in config.sites.sites.items():
            console.print(f"  {name} data root: {site.gnss_site_data_root}")

        # Show credentials from config
        email = config.processing.credentials.nasa_earthdata_acc_mail
        if email:
            console.print(f"  NASA Earthdata email: {email}")
            console.print("  [green]✓ NASA CDDIS enabled[/green]")
        else:
            console.print("  [yellow]⊘ NASA CDDIS disabled (ESA only)[/yellow]")

        console.print()

    except Exception as e:
        console.print("[red]❌ Validation failed:[/red]\n")
        console.print(str(e))
        console.print()
        raise typer.Exit(1) from e


@config_app.command()
def show(
    config_dir: Annotated[Path, CONFIG_DIR_OPTION] = DEFAULT_CONFIG_DIR,
    section: str = typer.Option(
        None,
        "--section",
        "-s",
        help="Show specific section (processing, sites, sids)",
    ),
) -> None:
    """Display current configuration.

    Parameters
    ----------
    config_dir : Path
        Directory containing config files.
    section : str
        Optional section name (processing, sites, sids).

    Returns
    -------
    None
    """
    from .loader import load_config

    try:
        config = load_config(config_dir)
    except Exception as e:
        console.print(f"\n[red]❌ Error loading config:[/red] {e}\n")
        raise typer.Exit(1) from e

    console.print("\n[bold]Current Configuration[/bold]\n")

    if section == "processing" or section is None:
        _show_processing(config.processing)

    if section == "sites" or section is None:
        _show_sites(config.sites)

    if section == "sids" or section is None:
        _show_sids(config.sids)

    console.print()


@config_app.command()
def edit(
    file: str = typer.Argument(
        ...,
        help="Config file to edit (processing, sites, sids)",
    ),
    config_dir: Annotated[Path, CONFIG_DIR_OPTION] = DEFAULT_CONFIG_DIR,
) -> None:
    """Open a configuration file in the editor.

    Parameters
    ----------
    file : str
        Config file to edit (processing, sites, sids).
    config_dir : Path
        Directory containing config files.

    Returns
    -------
    None
    """
    import os

    file_map = {
        "processing": config_dir / "processing.yaml",
        "sites": config_dir / "sites.yaml",
        "sids": config_dir / "sids.yaml",
    }

    if file not in file_map:
        console.print(f"[red]Unknown config file:[/red] {file}")
        console.print(f"Choose from: {', '.join(file_map.keys())}")
        raise typer.Exit(1)

    file_path = file_map[file]

    if not file_path.exists():
        console.print(f"[red]File not found:[/red] {file_path}")
        console.print("\nRun: canvodpy config init")
        raise typer.Exit(1)

    # Open in editor
    editor = os.getenv("EDITOR", "nano")
    subprocess.run([editor, str(file_path)])


def _show_processing(config: ProcessingConfig) -> None:
    """Display processing config.

    Parameters
    ----------
    config : ProcessingConfig
        Processing configuration object.

    Returns
    -------
    None
    """
    console.print("[bold]Processing Configuration:[/bold]")
    table = Table(show_header=False)

    table.add_row(
        "NASA Earthdata Email",
        config.credentials.nasa_earthdata_acc_mail or "[yellow]Not set[/yellow]",
    )

    table.add_row("Agency", config.aux_data.agency)
    table.add_row("Product Type", config.aux_data.product_type)
    table.add_row("Max Threads", str(config.processing.n_max_threads))
    table.add_row(
        "Time Aggregation",
        f"{config.processing.time_aggregation_seconds}s",
    )
    glonass_mode = (
        "Aggregated" if config.processing.aggregate_glonass_fdma else "Individual"
    )
    table.add_row("GLONASS FDMA", glonass_mode)
    console.print(table)
    console.print()


def _show_sites(config: SitesConfig) -> None:
    """Display sites config.

    Parameters
    ----------
    config : SitesConfig
        Sites configuration object.

    Returns
    -------
    None
    """
    console.print("[bold]Research Sites:[/bold]")
    for name, site in config.sites.items():
        console.print(f"\n  [cyan]{name}[/cyan]:")
        console.print(f"    Data root: {site.gnss_site_data_root}")
        console.print(f"    Receivers: {len(site.receivers)}")
        for recv_name, recv in site.receivers.items():
            console.print(f"      - {recv_name} ({recv.type})")


def _show_sids(config: SidsConfig) -> None:
    """Display SIDs config.

    Parameters
    ----------
    config : SidsConfig
        SIDs configuration object.

    Returns
    -------
    None
    """
    console.print("[bold]Signal IDs:[/bold]")
    table = Table(show_header=False)
    table.add_row("Mode", config.mode)
    if config.mode == "preset":
        table.add_row("Preset", config.preset or "")
    elif config.mode == "custom":
        table.add_row("Custom SIDs", f"{len(config.custom_sids)} defined")
    console.print(table)
    console.print()


# Register config subcommand
main_app.add_typer(config_app, name="config")


def main() -> None:
    """Run the CLI entry point."""
    main_app()


if __name__ == "__main__":
    main()
