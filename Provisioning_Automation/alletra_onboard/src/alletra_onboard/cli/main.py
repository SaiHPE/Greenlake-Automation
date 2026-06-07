from __future__ import annotations

from pathlib import Path

import uvicorn
import typer
from rich.console import Console
from rich.table import Table

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.application.intake import load_work_items_csv
from alletra_onboard.application.preflight_service import PreflightService
from alletra_onboard.application.run_service import RunService
from alletra_onboard.config import load_settings

app = typer.Typer(help="Alletra MP B10000 onboarding automation.")
console = Console()


def _store() -> SqliteRunStore:
    settings = load_settings()
    store = SqliteRunStore(settings.state_database_path)
    store.initialize()
    return store


@app.command("api")
def api() -> None:
    settings = load_settings()
    uvicorn.run("alletra_onboard.api.app:app", host=settings.api_host, port=settings.api_port, reload=False)


@app.command("run")
def create_run(serial: str = typer.Option(..., "--array", help="Array serial number.")) -> None:
    service = RunService(_store())
    run = service.create_run(serial)
    console.print(f"Created run [bold]{run.run_id}[/bold] for {serial}")


@app.command("status")
def status() -> None:
    runs = _store().list_runs()
    table = Table(title="Alletra Onboard Runs")
    table.add_column("Run ID")
    table.add_column("Serial")
    table.add_column("Status")
    table.add_column("Phase")
    for run in runs:
        table.add_row(run.run_id, run.serial_number, run.status.value, run.current_phase.value)
    console.print(table)


@app.command("preflight")
def preflight(file: str = typer.Option(..., "--file", help="CSV file with array work items.")) -> None:
    settings = load_settings()
    service = PreflightService(settings)
    items = load_work_items_csv(Path(file))
    for item in items:
        report = service.run_local(item)
        table = Table(title=f"Preflight {item.serial_number} ({report.overall_status.value})")
        table.add_column("Check")
        table.add_column("Status")
        table.add_column("Message")
        for check in report.checks:
            table.add_row(check.name, check.status.value, check.message)
        console.print(table)
