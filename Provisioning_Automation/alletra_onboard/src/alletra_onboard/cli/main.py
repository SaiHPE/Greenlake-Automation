from __future__ import annotations

import asyncio
from pathlib import Path

import uvicorn
import typer
from rich.console import Console
from rich.table import Table

from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.application.intake import load_work_items_csv
from alletra_onboard.application.preflight_service import PreflightService
from alletra_onboard.application.provisioning import (
    DONE,
    FAILED,
    SKIPPED,
    WOULD_DO,
    ProvisionResult,
    build_provisioning_service,
    missing_credentials,
)
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


@app.command("provision")
def provision(
    file: str = typer.Option(..., "--file", help="CSV file with array work items."),
    serial: str | None = typer.Option(None, "--serial", help="Only provision the matching serial number."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview every call; perform no writes."),
) -> None:
    """Component A — GreenLake REST: discover, add subscription, register device, assign, verify."""
    settings = load_settings()
    missing = missing_credentials(settings)
    if missing:
        console.print(f"[red]Missing GreenLake credentials:[/red] {', '.join(missing)}")
        console.print("Run [bold]onboard configure[/bold] (or set them in .env), then retry.")
        raise typer.Exit(code=2)

    items = load_work_items_csv(Path(file))
    if serial:
        items = [item for item in items if item.serial_number == serial]
    if not items:
        console.print("[red]No matching work items found in the CSV.[/red]")
        raise typer.Exit(code=2)

    mode = "DRY-RUN (no writes)" if dry_run else "LIVE"
    console.print(f"[bold]GreenLake provisioning — {mode}[/bold]  base={settings.gl_base_url}")

    results: list[ProvisionResult] = []
    for item in items:
        console.rule(f"{item.serial_number}  ({item.part_number})")

        def progress(phase, message):
            console.print(f"  [dim]{phase.value:<22}[/dim] {message}")

        service = build_provisioning_service(settings, progress=progress)
        result = asyncio.run(service.provision(item, dry_run=dry_run))
        results.append(result)
        _print_result_table(result)

    console.print()
    if dry_run:
        blocked = [r for r in results if r.error]
        if blocked:
            console.print(
                f"[yellow]Dry-run complete (no changes made), but {len(blocked)} array(s) hit a "
                f"blocking issue above — resolve before the live run.[/yellow]"
            )
        else:
            console.print("[green]Dry-run complete — no changes made; the live run would proceed.[/green]")
        return
    failures = [r for r in results if not r.succeeded]
    if failures:
        console.print(f"[red]{len(failures)} of {len(results)} array(s) did not complete.[/red]")
        raise typer.Exit(code=1)
    console.print(f"[green]All {len(results)} array(s) provisioned and verified.[/green]")


@app.command("configure")
def configure(
    client_id: str | None = typer.Option(None, "--client-id"),
    client_secret: str | None = typer.Option(None, "--client-secret"),
    token_url: str | None = typer.Option(None, "--token-url"),
    base_url: str | None = typer.Option(None, "--base-url"),
    workspace_id: str | None = typer.Option(None, "--workspace-id"),
    env_file: str = typer.Option(".env", "--env-file", help="Path to the .env to write (gitignored)."),
    show: bool = typer.Option(False, "--show", help="Print current values (secret masked) and exit."),
) -> None:
    """Store GreenLake API credentials in a local .env — the interface to add them."""
    env_path = Path(env_file)
    current = _read_env(env_path)

    if show:
        for key in ("GL_CLIENT_ID", "GL_TOKEN_URL", "GL_BASE_URL", "GL_MEMBER_WORKSPACE_ID"):
            console.print(f"{key}={current.get(key) or '(unset)'}")
        console.print(f"GL_CLIENT_SECRET={'**** (set)' if current.get('GL_CLIENT_SECRET') else '(unset)'}")
        return

    client_id = client_id or typer.prompt("GreenLake Client ID", default=current.get("GL_CLIENT_ID", ""))
    client_secret = client_secret or typer.prompt(
        "GreenLake Client Secret", hide_input=True, show_default=False, default=current.get("GL_CLIENT_SECRET", "")
    )
    token_url = token_url or typer.prompt("Token URL", default=current.get("GL_TOKEN_URL", ""))
    base_url = base_url or typer.prompt(
        "API base URL", default=current.get("GL_BASE_URL", "https://global.api.greenlake.hpe.com")
    )
    workspace_id = workspace_id or typer.prompt(
        "Member workspace ID", default=current.get("GL_MEMBER_WORKSPACE_ID", "")
    )

    current.update(
        {
            "GL_CLIENT_ID": client_id,
            "GL_CLIENT_SECRET": client_secret,
            "GL_TOKEN_URL": token_url,
            "GL_BASE_URL": base_url,
            "GL_MEMBER_WORKSPACE_ID": workspace_id,
        }
    )
    _write_env(env_path, current)
    console.print(f"[green]Saved {env_path.resolve()}[/green] (gitignored). Secret stored locally; not printed.")


@app.command("check")
def check() -> None:
    """Read-only health check: GreenLake auth + which Data Services regions are provisioned.

    Use this to confirm an install (e.g. on the jump box) can reach GreenLake and that the
    workspace has a provisioned Data Services instance to assign devices to. No writes.
    """
    settings = load_settings()
    missing = missing_credentials(settings)
    if missing:
        console.print(f"[red]Missing GreenLake credentials:[/red] {', '.join(missing)}")
        console.print("Run [bold]onboard configure[/bold] first.")
        raise typer.Exit(code=2)

    async def run():
        service = build_provisioning_service(settings)
        items = await service.service_catalog.per_region_service_managers()
        ds_ids = {
            sm.get("id")
            for region in items
            for sm in region.get("serviceManagers", [])
            if "data service" in str(sm.get("name", "")).lower()
        }
        response = await service.http.request(
            "GET", "/service-catalog/v1/service-manager-provisions", bucket="service_catalog_read"
        )
        return ds_ids, response.json().get("items", [])

    console.print(f"[bold]GreenLake health check[/bold]  base={settings.gl_base_url}")
    try:
        ds_ids, provisions = asyncio.run(run())
    except Exception as exc:  # noqa: BLE001 - operator-facing health check reports, not crashes.
        console.print(f"[red]FAILED:[/red] {type(exc).__name__}: {str(exc)[:200]}")
        console.print("[dim]On the jump box this is often egress/proxy — set HTTPS_PROXY and retry.[/dim]")
        raise typer.Exit(code=1)

    console.print("[green]OK[/green] — token fetched and GreenLake is reachable.")
    table = Table(title="Provisioned services in this workspace")
    table.add_column("Region")
    table.add_column("Status")
    table.add_column("Service manager id")
    table.add_column("Data Services?")
    for provision in provisions:
        sm_id = (provision.get("serviceManager") or {}).get("id") or ""
        is_ds = "YES" if sm_id in ds_ids else ""
        table.add_row(str(provision.get("region")), str(provision.get("provisionStatus")), sm_id, is_ds)
    console.print(table)
    ready = any(
        (p.get("serviceManager") or {}).get("id") in ds_ids and p.get("provisionStatus") == "PROVISIONED"
        for p in provisions
    )
    if ready:
        console.print("[green]Data Services is provisioned — the assign step can run.[/green]")
    else:
        console.print(
            "[yellow]No PROVISIONED Data Services found. Add it in the workspace "
            "(Manage Workspace -> Services) before the assign step.[/yellow]"
        )


_STATUS_STYLE = {DONE: "green", SKIPPED: "cyan", WOULD_DO: "yellow", FAILED: "red"}


def _print_result_table(result: ProvisionResult) -> None:
    table = Table(show_header=True, header_style="bold")
    table.add_column("Phase")
    table.add_column("Status")
    table.add_column("Detail")
    for phase in result.phases:
        style = _STATUS_STYLE.get(phase.status, "white")
        table.add_row(phase.phase.value, f"[{style}]{phase.status}[/{style}]", phase.detail)
    console.print(table)
    ids = [
        f"device={result.device_id}" if result.device_id else "",
        f"subscription={result.subscription_id}" if result.subscription_id else "",
        f"app={result.service_manager_id}" if result.service_manager_id else "",
    ]
    ids = [value for value in ids if value]
    if ids:
        console.print(f"  [dim]{'  '.join(ids)}[/dim]")
    if result.error:
        console.print(f"  [red]error: {result.error}[/red]")


def _read_env(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            data[key.strip()] = value.strip()
    return data


def _write_env(path: Path, data: dict[str, str]) -> None:
    lines = [f"{key}={value}" for key, value in data.items() if value != ""]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@app.command("preflight")
def preflight(
    file: str = typer.Option(..., "--file", help="CSV file with array work items."),
    live_greenlake: bool = typer.Option(
        False,
        "--live-greenlake",
        help="Run live read-only GreenLake checks after local validation.",
    ),
) -> None:
    settings = load_settings()
    service = PreflightService(settings)
    items = load_work_items_csv(Path(file))
    for item in items:
        report = asyncio.run(service.run(item, live_greenlake=live_greenlake))
        table = Table(title=f"Preflight {item.serial_number} ({report.overall_status.value})")
        table.add_column("Check")
        table.add_column("Status")
        table.add_column("Message")
        table.add_column("Remediation")
        for check in report.checks:
            table.add_row(check.name, check.status.value, check.message, check.remediation or "")
        console.print(table)
