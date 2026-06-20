"""CLI entry point — just enough to launch the web app (the product is the UI / packaged .exe).

The onboarding itself (GreenLake registration, Cloud Connectivity, DSCC Set Up System) is driven
entirely from the web app; the old per-component CLI commands were removed. ``check`` stays for a
read-only connectivity verification (used by setup_jumpbox.ps1).
"""

from __future__ import annotations

import asyncio

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from alletra_onboard.application.health import greenlake_check
from alletra_onboard.config import load_settings

app = typer.Typer(help="HPE Alletra MP B10000 onboarding — launches the operator web app.")
console = Console()


@app.command("ui")
def ui() -> None:
    """Start the onboarding web app and open it in the default browser (operator entry point)."""
    import threading
    import webbrowser

    settings = load_settings()
    address = f"http://{settings.api_host}:{settings.api_port}"
    console.print(f"[bold]Alletra Onboard[/bold] — serving the web app at [green]{address}[/green] (Ctrl+C to stop)")
    threading.Timer(1.5, lambda: webbrowser.open(address)).start()
    uvicorn.run("alletra_onboard.api.app:app", host=settings.api_host, port=settings.api_port, reload=False)


@app.command("api")
def api() -> None:
    """Start the API server without opening a browser."""
    settings = load_settings()
    uvicorn.run("alletra_onboard.api.app:app", host=settings.api_host, port=settings.api_port, reload=False)


@app.command("check")
def check() -> None:
    """Read-only health check: GreenLake auth + which Data Services regions are provisioned.

    Confirms an install (e.g. on the jump box) can reach GreenLake and that the workspace has a
    provisioned Data Services instance to assign devices to. No writes.
    """
    settings = load_settings()
    console.print(f"[bold]GreenLake health check[/bold]  base={settings.gl_base_url}")
    report = asyncio.run(greenlake_check(settings))

    if report.missing_credentials:
        console.print(f"[red]Missing GreenLake credentials:[/red] {', '.join(report.missing_credentials)}")
        console.print("Enter them in the web app's Initialisation sheet (or .env) first.")
        raise typer.Exit(code=2)
    if not report.ok:
        console.print(f"[red]FAILED:[/red] {report.error}")
        console.print("[dim]On the jump box this is often egress/proxy — set HTTPS_PROXY and retry.[/dim]")
        raise typer.Exit(code=1)

    console.print("[green]OK[/green] — token fetched and GreenLake is reachable.")
    table = Table(title="Provisioned services in this workspace")
    table.add_column("Region")
    table.add_column("Status")
    table.add_column("Service manager id")
    table.add_column("Data Services?")
    for provision in report.provisions:
        table.add_row(
            provision.region,
            provision.status,
            provision.service_manager_id,
            "YES" if provision.is_data_services else "",
        )
    console.print(table)
    if report.ready:
        console.print("[green]Data Services is provisioned — onboard from the web app.[/green]")
    else:
        console.print(
            "[yellow]No PROVISIONED Data Services found. Add it in the workspace "
            "(Manage Workspace -> Services) before onboarding.[/yellow]"
        )
