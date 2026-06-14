from __future__ import annotations

import asyncio
from pathlib import Path

import uvicorn
import typer
from rich.console import Console
from rich.table import Table

from alletra_onboard.adapters.browser.cloudinit_wizard import CloudinitWizardAdapter
from alletra_onboard.adapters.browser.debug_browser import launch_debug_browser
from alletra_onboard.adapters.browser.dscc_setup import DsccSetupAdapter
from alletra_onboard.adapters.persistence.sqlite import SqliteRunStore
from alletra_onboard.application.configuring import read_env, set_env_values
from alletra_onboard.application.health import greenlake_check
from alletra_onboard.application.intake import load_work_items_csv
from alletra_onboard.domain.models import BrowserResultStatus
from alletra_onboard.application.preflight_service import PreflightService
from alletra_onboard.application.provisioning import (
    DONE,
    FAILED,
    SKIPPED,
    WARNING,
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
    warned = [r for r in results if any(p.status == WARNING for p in r.phases)]
    if warned:
        console.print(
            f"[yellow]{len(results)} array(s) completed with warnings — device registered + "
            f"ASSIGNED_TO_SERVICE (the array can connect via cloudinit); see warnings above.[/yellow]"
        )
        return
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
    current = read_env(env_path)

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

    set_env_values(
        env_path,
        {
            "GL_CLIENT_ID": client_id,
            "GL_CLIENT_SECRET": client_secret,
            "GL_TOKEN_URL": token_url,
            "GL_BASE_URL": base_url,
            "GL_MEMBER_WORKSPACE_ID": workspace_id,
        },
    )
    console.print(f"[green]Saved {env_path.resolve()}[/green] (gitignored). Secret stored locally; not printed.")


@app.command("check")
def check() -> None:
    """Read-only health check: GreenLake auth + which Data Services regions are provisioned.

    Use this to confirm an install (e.g. on the jump box) can reach GreenLake and that the
    workspace has a provisioned Data Services instance to assign devices to. No writes.
    """
    settings = load_settings()
    console.print(f"[bold]GreenLake health check[/bold]  base={settings.gl_base_url}")
    report = asyncio.run(greenlake_check(settings))

    if report.missing_credentials:
        console.print(f"[red]Missing GreenLake credentials:[/red] {', '.join(report.missing_credentials)}")
        console.print("Run [bold]onboard configure[/bold] first.")
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
        console.print("[green]Data Services is provisioned — the assign step can run.[/green]")
    else:
        console.print(
            "[yellow]No PROVISIONED Data Services found. Add it in the workspace "
            "(Manage Workspace -> Services) before the assign step.[/yellow]"
        )


@app.command("cloudinit")
def cloudinit(
    file: str = typer.Option(..., "--file", help="CSV file with array work items."),
    serial: str = typer.Option(..., "--serial", help="Array serial number."),
    attach: str = typer.Option(
        None,
        "--attach",
        metavar="CDP_URL",
        help="Attach to an already-open browser (e.g. http://localhost:9222) and drive its current "
        "cloudinit tab, instead of launching a new browser. For testing on an already-connected "
        "array: open the wizard, click Modify yourself to reach page 1, then run with --attach.",
    ),
    auto_submit: bool = typer.Option(
        False, "--auto-submit", help="Also click Submit. Default: stop at Review so the operator submits."
    ),
) -> None:
    """Component B — fill the on-array Cloud Connectivity Wizard.

    Default: launches its own browser, navigates to the cloudinit URL, fills every screen and
    STOPS at Review (does NOT click Submit) so you review + submit yourself; the browser stays
    open and it reports the result you trigger. The automation never clicks Modify or Launch
    DSCC. Use --attach to drive a browser you already have open; --auto-submit for unattended.
    """
    settings = load_settings()
    matches = [item for item in load_work_items_csv(Path(file)) if item.serial_number == serial]
    if not matches:
        console.print("[red]No matching work item in the CSV.[/red]")
        raise typer.Exit(code=2)

    item = matches[0]
    console.print(f"[bold]Cloudinit wizard[/bold] for {serial}  ->  {item.cloudinit_url}")
    if auto_submit:
        console.print("[yellow]--auto-submit: will click Submit and apply the config automatically.[/yellow]")
    else:
        console.print(
            "[dim]Fills every screen and STOPS at Review. Review the values in the browser and click "
            "Submit yourself (or close the browser to cancel). The browser stays open while it waits.[/dim]"
        )
    if attach:
        console.print(f"[dim]Attaching to {attach} and driving its open cloudinit tab (no new browser).[/dim]")
    adapter = CloudinitWizardAdapter(
        headless=settings.browser_headless, cdp_url=attach, artifact_dir=settings.artifact_dir
    )
    result = asyncio.run(adapter.run(item, run_id=serial, auto_submit=auto_submit))

    ok = result in (BrowserResultStatus.SUCCEEDED, BrowserResultStatus.ALREADY_DONE)
    style = "green" if ok else ("yellow" if result == BrowserResultStatus.WAITING_FOR_OPERATOR else "red")
    console.print(f"Result: [{style}]{result.value}[/{style}]")
    if result == BrowserResultStatus.WAITING_FOR_OPERATOR:
        console.print("[yellow]Browser unavailable — run: .\\.venv\\Scripts\\python.exe -m playwright install chromium[/yellow]")
    if not ok:
        raise typer.Exit(code=1)


@app.command("dscc")
def dscc(
    file: str = typer.Option(..., "--file", help="CSV file with array work items."),
    serial: str = typer.Option(..., "--serial", help="Array serial number."),
    attach: str = typer.Option(
        ...,
        "--attach",
        metavar="CDP_URL",
        help="Attach to a Chrome you already logged into DSCC with (e.g. http://localhost:9222). "
        "DSCC needs your GreenLake SSO session, so this adapter never logs in — open the "
        "Set Up System wizard for the array (on Welcome), then run this.",
    ),
) -> None:
    """Component C — fill the DSCC "Set Up System" wizard up to the System credential.

    Attaches to your logged-in Chrome, drives the wizard inside the setup iframe
    (Welcome -> Network Domain -> Time -> Attributes -> System name/country), and STOPS on the
    System screen so you add the credential (secret), then Continue -> review -> Submit yourself.
    Never enters the secret, never Submits, never touches the blueprint.
    """
    settings = load_settings()
    matches = [item for item in load_work_items_csv(Path(file)) if item.serial_number == serial]
    if not matches:
        console.print("[red]No matching work item in the CSV.[/red]")
        raise typer.Exit(code=2)

    item = matches[0]
    console.print(f"[bold]DSCC Set Up System[/bold] for {serial}  ->  console-{item.dscc_region_code}.data.cloud.hpe.com")
    console.print(f"[dim]Attaching to {attach}; fills the wizard and STOPS on the System screen at Credentials.[/dim]")

    adapter = DsccSetupAdapter(cdp_url=attach, artifact_dir=settings.artifact_dir)
    result = asyncio.run(adapter.run(item, run_id=serial))

    waiting = result == BrowserResultStatus.WAITING_FOR_OPERATOR
    style = "green" if waiting else "red"
    console.print(f"Result: [{style}]{result.value}[/{style}]")
    if waiting:
        console.print(
            "[green]Filled through System name + country.[/green] In the browser: add the System "
            "[bold]Credentials[/bold] secret, then Continue -> review the values -> Submit yourself."
        )
    else:
        console.print("[yellow]Did not reach the System screen — check the artifact screenshot.[/yellow]")
        raise typer.Exit(code=1)


@app.command("browser")
def browser(
    port: int = typer.Option(9222, "--port", help="CDP remote-debugging port."),
    profile: str = typer.Option(None, "--profile", help="User-data dir (persists the SSO login). Default: a temp dir."),
    url: str = typer.Option(None, "--url", help="Optional URL to open (e.g. the DSCC console or cloudinit URL)."),
    proxy: str = typer.Option(None, "--proxy", help="Proxy for the browser. Default: BROWSER_PROXY or the HTTPS_PROXY env."),
    no_proxy: bool = typer.Option(False, "--no-proxy", help="Force a direct connection (ignore HTTPS_PROXY)."),
) -> None:
    """Launch a CDP-enabled Chrome for the cloudinit / DSCC wizards to attach to.

    Starts Chrome with remote debugging on a persistent profile (so your GreenLake login
    survives across steps) and prints the --attach URL to pass to `onboard cloudinit`/`onboard dscc`.
    Behind a lab proxy it auto-applies HTTPS_PROXY so DSCC SSO can complete (use --no-proxy to skip).
    """
    settings = load_settings()
    try:
        info = launch_debug_browser(
            port=port,
            profile_dir=profile,
            url=url,
            proxy=proxy or settings.browser_proxy,
            proxy_bypass=settings.browser_proxy_bypass,
            auto_proxy=not no_proxy,
        )
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]Launched[/green] {info['executable']}")
    console.print(f"  profile : {info['profile_dir']}")
    if info["proxy"]:
        console.print(f"  proxy   : {info['proxy']}")
    console.print(f"  attach  : [bold]{info['cdp_url']}[/bold]")
    console.print(
        "[dim]Log into DSCC (and/or open the cloudinit URL) in this window, then run:\n"
        f"  onboard dscc      --file config\\arrays.csv --serial <SERIAL> --attach {info['cdp_url']}\n"
        f"  onboard cloudinit --file config\\arrays.csv --serial <SERIAL> --attach {info['cdp_url']}[/dim]"
    )


@app.command("sync-clock")
def sync_clock_cmd() -> None:
    """Correct the system clock from an HTTPS time source (fixes DSCC 'iat is in the future').

    Works where NTP/UDP is blocked, since it rides the HTTPS proxy. Needs Administrator.
    """
    from alletra_onboard.adapters.system.clock import sync_clock

    try:
        result = asyncio.run(sync_clock())
    except PermissionError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    except Exception as exc:  # noqa: BLE001
        console.print(f"[red]Clock sync failed:[/red] {type(exc).__name__}: {str(exc)[:200]}")
        raise typer.Exit(code=1) from exc

    if result.changed:
        console.print(f"[green]Clock corrected[/green] (was off by {result.skew_seconds_before:+.0f}s).")
        console.print(f"  now: {result.local_utc_after} UTC (source {result.source})")
    else:
        console.print(f"[green]Clock already in sync[/green] ({result.skew_seconds_before:+.1f}s vs {result.source}).")


_STATUS_STYLE = {DONE: "green", SKIPPED: "cyan", WOULD_DO: "yellow", WARNING: "yellow", FAILED: "red"}


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
