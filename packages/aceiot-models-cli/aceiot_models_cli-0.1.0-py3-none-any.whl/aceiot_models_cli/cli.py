"""Main CLI entry point for aceiot-models-cli."""

import click
from aceiot_models import (
    ClientCreate,
)
from click import Context

from .api_client import APIClient
from .config import load_config
from .formatters import format_json, format_table, print_error, print_success


def require_api_client(ctx: Context) -> APIClient:
    """Ensure API client is available, exit if not."""
    if "client" not in ctx.obj:
        print_error("API key is required. Set ACEIOT_API_KEY or use --api-key")
        ctx.exit(1)
    return ctx.obj["client"]


# Create main CLI group
@click.group()
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=False),
    default=None,
    help="Path to configuration file",
)
@click.option(
    "--api-url",
    envvar="ACEIOT_API_URL",
    default="https://flightdeck.aceiot.cloud/api",
    help="API base URL",
)
@click.option(
    "--api-key",
    envvar="ACEIOT_API_KEY",
    help="API key for authentication",
)
@click.option(
    "--output",
    "-o",
    type=click.Choice(["json", "table"]),
    default="table",
    help="Output format",
)
@click.pass_context
def cli(
    ctx: Context,
    config: str | None,
    api_url: str,
    api_key: str | None,
    output: str,
) -> None:
    """ACE IoT Models CLI - Interact with the ACE IoT API."""
    # Load configuration
    cfg = load_config(config)

    # Override with command line options
    if api_url:
        cfg.api_url = api_url
    if api_key:
        cfg.api_key = api_key

    # Store config in context for subcommands
    ctx.obj = {
        "config": cfg,
        "output": output,
    }

    # Only create API client if we have an API key
    # Some commands (like init, test-serializers) don't need it
    if cfg.api_key:
        ctx.obj["client"] = APIClient(cfg.api_url, cfg.api_key)


# Client commands group
@cli.group()
@click.pass_context
def clients(ctx: Context) -> None:
    """Manage clients."""
    pass


@clients.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=10, help="Results per page")
@click.pass_context
def list_clients(ctx: Context, page: int, per_page: int) -> None:
    """List all clients."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_clients(page=page, per_page=per_page)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as table
            headers = ["ID", "Name", "Nice Name", "Business Contact", "Tech Contact"]
            rows = []
            for item in result.get("items", []):
                rows.append(
                    [
                        item.get("id", ""),
                        item.get("name", ""),
                        item.get("nice_name", ""),
                        item.get("bus_contact", ""),
                        item.get("tech_contact", ""),
                    ]
                )
            click.echo(format_table(headers, rows))
            click.echo(
                f"\nPage {result.get('page')} of {result.get('pages')} (Total: {result.get('total')})"
            )
    except Exception as e:
        print_error(f"Failed to list clients: {e}")
        ctx.exit(1)


@clients.command("get")
@click.argument("client_name")
@click.pass_context
def get_client(ctx: Context, client_name: str) -> None:
    """Get a specific client by name."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_client(client_name)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as key-value pairs
            click.echo(f"Client: {result.get('name')}")
            click.echo(f"Nice Name: {result.get('nice_name')}")
            click.echo(f"ID: {result.get('id')}")
            click.echo(f"Business Contact: {result.get('bus_contact')}")
            click.echo(f"Tech Contact: {result.get('tech_contact')}")
            click.echo(f"Address: {result.get('address')}")
    except Exception as e:
        print_error(f"Failed to get client: {e}")
        ctx.exit(1)


@clients.command("create")
@click.option("--name", required=True, help="Client name")
@click.option("--nice-name", help="Nice name for display")
@click.option("--bus-contact", help="Business contact")
@click.option("--tech-contact", help="Technical contact")
@click.option("--address", help="Client address")
@click.pass_context
def create_client(
    ctx: Context,
    name: str,
    nice_name: str | None,
    bus_contact: str | None,
    tech_contact: str | None,
    address: str | None,
) -> None:
    """Create a new client."""
    client = require_api_client(ctx)

    try:
        # Create client model
        client_data = ClientCreate(
            name=name,
            nice_name=nice_name or name,
            bus_contact=bus_contact,
            tech_contact=tech_contact,
            address=address,
        )

        result = client.create_client(client_data)
        print_success(f"Client '{name}' created successfully")

        if ctx.obj["output"] == "json":
            click.echo(format_json(result))
    except Exception as e:
        print_error(f"Failed to create client: {e}")
        ctx.exit(1)


# Sites commands group
@cli.group()
@click.pass_context
def sites(ctx: Context) -> None:
    """Manage sites."""
    pass


@sites.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=10, help="Results per page")
@click.option("--client-name", help="Filter by client name")
@click.option("--collect-enabled", is_flag=True, help="Only show sites with collect enabled points")
@click.option("--show-archived", is_flag=True, help="Include archived sites")
@click.pass_context
def list_sites(
    ctx: Context,
    page: int,
    per_page: int,
    client_name: str | None,
    collect_enabled: bool,
    show_archived: bool,
) -> None:
    """List all sites."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_sites(
            page=page,
            per_page=per_page,
            client_name=client_name,
            collect_enabled=collect_enabled,
            show_archived=show_archived,
        )

        # Check if result is None
        if result is None:
            print_error("API returned no data. Check your API key and connection.")
            ctx.exit(1)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as table
            headers = ["ID", "Name", "Client", "Nice Name", "Address", "Archived"]
            rows = []
            items = result.get("items", [])

            if not items:
                click.echo("No sites found.")
                return

            for item in items:
                address = item.get("address", "")
                # Handle None address gracefully
                if address is not None:
                    address = str(address)[:50]  # Truncate long addresses
                else:
                    address = ""

                rows.append(
                    [
                        item.get("id", ""),
                        item.get("name", ""),
                        item.get("client", ""),
                        item.get("nice_name", ""),
                        address,
                        "Yes" if item.get("archived") else "No",
                    ]
                )

            click.echo(format_table(headers, rows))

            # Add pagination info with safe defaults
            page_info = result.get("page", 1)
            pages_info = result.get("pages", 1)
            total_info = result.get("total", len(rows))
            click.echo(f"\nPage {page_info} of {pages_info} (Total: {total_info})")

    except Exception as e:
        print_error(f"Failed to list sites: {e}")
        ctx.exit(1)


@sites.command("get")
@click.argument("site_name")
@click.pass_context
def get_site(ctx: Context, site_name: str) -> None:
    """Get a specific site by name."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_site(site_name)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as key-value pairs
            click.echo(f"Site: {result.get('name')}")
            click.echo(f"Nice Name: {result.get('nice_name')}")
            click.echo(f"ID: {result.get('id')}")
            click.echo(f"Client: {result.get('client')}")
            click.echo(f"Address: {result.get('address')}")
            click.echo(f"Latitude: {result.get('latitude')}")
            click.echo(f"Longitude: {result.get('longitude')}")
            if result.get("timezone"):
                click.echo(f"Timezone: {result.get('timezone')}")
            click.echo(f"Archived: {'Yes' if result.get('archived') else 'No'}")
    except Exception as e:
        print_error(f"Failed to get site: {e}")
        ctx.exit(1)


# Gateways commands group
@cli.group()
@click.pass_context
def gateways(ctx: Context) -> None:
    """Manage gateways."""
    pass


@gateways.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=10, help="Results per page")
@click.option("--show-archived", is_flag=True, help="Include archived gateways")
@click.pass_context
def list_gateways(ctx: Context, page: int, per_page: int, show_archived: bool) -> None:
    """List all gateways."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_gateways(page=page, per_page=per_page, show_archived=show_archived)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as table
            headers = ["Name", "Site", "Client", "VPN IP", "Archived", "Updated"]
            rows = []
            for item in result.get("items", []):
                rows.append(
                    [
                        item.get("name", ""),
                        item.get("site", ""),
                        item.get("client", ""),
                        item.get("vpn_ip", ""),
                        "Yes" if item.get("archived") else "No",
                        item.get("updated", "")[:19],  # Truncate timestamp
                    ]
                )
            click.echo(format_table(headers, rows))
            click.echo(
                f"\nPage {result.get('page')} of {result.get('pages')} (Total: {result.get('total')})"
            )
    except Exception as e:
        print_error(f"Failed to list gateways: {e}")
        ctx.exit(1)


# Points commands group
@cli.group()
@click.pass_context
def points(ctx: Context) -> None:
    """Manage points."""
    pass


@points.command("list")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=10, help="Results per page")
@click.option("--site", help="Filter by site name")
@click.pass_context
def list_points(ctx: Context, page: int, per_page: int, site: str | None) -> None:
    """List all points."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        if site:
            result = client.get_site_points(site, page=page, per_page=per_page)
        else:
            result = client.get_points(page=page, per_page=per_page)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as table
            headers = ["ID", "Name", "Site", "Type", "Collect", "Interval", "Updated"]
            rows = []
            for item in result.get("items", []):
                rows.append(
                    [
                        item.get("id", ""),
                        item.get("name", "")[:40],  # Truncate long names
                        item.get("site", ""),
                        item.get("point_type", ""),
                        "Yes" if item.get("collect_enabled") else "No",
                        str(item.get("collect_interval", "")),
                        item.get("updated", "")[:10],  # Just date
                    ]
                )
            click.echo(format_table(headers, rows))
            click.echo(
                f"\nPage {result.get('page')} of {result.get('pages')} (Total: {result.get('total')})"
            )
    except Exception as e:
        print_error(f"Failed to list points: {e}")
        ctx.exit(1)


@points.command("timeseries")
@click.argument("point_name")
@click.option("--start", required=True, help="Start time (ISO format)")
@click.option("--end", required=True, help="End time (ISO format)")
@click.pass_context
def get_timeseries(ctx: Context, point_name: str, start: str, end: str) -> None:
    """Get timeseries data for a point."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_point_timeseries(point_name, start, end)

        if output_format == "json":
            click.echo(format_json(result))
        else:
            # Format as table
            samples = result.get("point_samples", [])
            if samples:
                headers = ["Time", "Value", "Point"]
                rows = []
                for sample in samples:
                    rows.append(
                        [
                            sample.get("time", ""),
                            sample.get("value", ""),
                            sample.get("name", ""),
                        ]
                    )
                click.echo(format_table(headers, rows))
                click.echo(f"\nTotal samples: {len(samples)}")
            else:
                click.echo("No data found for the specified time range")
    except Exception as e:
        print_error(f"Failed to get timeseries data: {e}")
        ctx.exit(1)


@points.command("discovered")
@click.argument("site_name")
@click.option("--page", default=1, help="Page number")
@click.option("--per-page", default=100, help="Results per page")
@click.pass_context
def list_discovered_points(ctx: Context, site_name: str, page: int, per_page: int) -> None:
    """List discovered BACnet points for a site."""
    from aceiot_models import Point

    from .utils import convert_api_response_to_points

    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        result = client.get_discovered_points(site_name, page=page, per_page=per_page)

        # Convert to Point objects for better handling
        result = convert_api_response_to_points(result)

        if output_format == "json":
            # Convert Point objects back to dicts for JSON output
            json_result = result.copy()
            if "items" in json_result:
                json_result["items"] = [
                    point.model_dump() if isinstance(point, Point) else point
                    for point in json_result["items"]
                ]
            click.echo(format_json(json_result))
        else:
            # Format as table
            headers = ["Name", "Type", "Device", "Object Type", "Object Name", "Present Value"]
            rows = []

            for point in result.get("items", []):
                if isinstance(point, Point) and point.bacnet_data:
                    bacnet = point.bacnet_data
                    device_name = bacnet.device_name or "Unknown"
                    device_id = bacnet.device_id or ""
                    rows.append(
                        [
                            point.name or "",
                            point.point_type or "",
                            f"{device_name} ({device_id})",
                            bacnet.object_type or "",
                            bacnet.object_name or "",
                            bacnet.present_value or "",
                        ]
                    )
                elif isinstance(point, Point):
                    rows.append(
                        [
                            point.name or "",
                            point.point_type or "",
                            "-",
                            "-",
                            "-",
                            "-",
                        ]
                    )
                else:
                    # Fallback for raw dict (if Point creation failed)
                    if point.get("bacnet_data"):
                        bacnet = point["bacnet_data"]
                        rows.append(
                            [
                                point.get("name", ""),
                                point.get("point_type", ""),
                                f"{bacnet.get('device_name', 'Unknown')} ({bacnet.get('device_id', '')})",
                                bacnet.get("object_type", ""),
                                bacnet.get("object_name", ""),
                                bacnet.get("present_value", ""),
                            ]
                        )
                    else:
                        rows.append(
                            [
                                point.get("name", ""),
                                point.get("point_type", ""),
                                "-",
                                "-",
                                "-",
                                "-",
                            ]
                        )

            if rows:
                click.echo(format_table(headers, rows))

                # Add pagination info
                total_pages = result.get("pages", 1)
                total_items = result.get("total", len(rows))
                click.echo(
                    f"\nPage {result.get('page', 1)} of {total_pages} (Total points: {total_items})"
                )
            else:
                click.echo("No discovered points found")
    except Exception as e:
        print_error(f"Failed to get discovered points: {e}")
        ctx.exit(1)


@points.command("batch-timeseries")
@click.option(
    "--points-file",
    "-f",
    type=click.File("r"),
    required=True,
    help="File containing point names (one per line)",
)
@click.option("--start", "-s", required=True, help="Start time (ISO format)")
@click.option("--end", "-e", required=True, help="End time (ISO format)")
@click.option("--batch-size", default=100, help="Points per batch")
@click.pass_context
def batch_timeseries(ctx: Context, points_file, start: str, end: str, batch_size: int) -> None:
    """Get timeseries data for multiple points with automatic batching."""
    client = require_api_client(ctx)
    output_format = ctx.obj["output"]

    try:
        # Read point names from file
        point_names = [line.strip() for line in points_file if line.strip()]

        if not point_names:
            click.echo("No point names found in file")
            return

        click.echo(f"Processing {len(point_names)} points in batches of {batch_size}...")

        # Get data with batching
        result = client.get_points_timeseries_batch(point_names, start, end, batch_size=batch_size)

        samples = result.get("point_samples", [])

        if output_format == "json":
            click.echo(format_json(result))
        else:
            if samples:
                # Group by point name for summary
                points_data = {}
                for sample in samples:
                    point_name = sample.get("name", "Unknown")
                    if point_name not in points_data:
                        points_data[point_name] = []
                    points_data[point_name].append(sample)

                # Display summary
                headers = ["Point Name", "Sample Count", "First Time", "Last Time"]
                rows = []

                for point_name, point_samples in points_data.items():
                    sorted_samples = sorted(point_samples, key=lambda x: x.get("time", ""))
                    rows.append(
                        [
                            point_name,
                            len(point_samples),
                            sorted_samples[0].get("time", "") if sorted_samples else "-",
                            sorted_samples[-1].get("time", "") if sorted_samples else "-",
                        ]
                    )

                click.echo(format_table(headers, rows))
                click.echo(f"\nTotal samples: {len(samples)} from {len(points_data)} points")
            else:
                click.echo("No data found for the specified time range")
    except Exception as e:
        print_error(f"Failed to get batch timeseries data: {e}")
        ctx.exit(1)


# Init command
@cli.command("init")
@click.option("--api-key", help="API key for authentication")
@click.option("--api-url", help="API base URL")
def init(api_key: str | None, api_url: str | None) -> None:
    """Initialize configuration file."""
    from .config import init_config

    try:
        init_config(api_key=api_key, api_url=api_url)
        print_success("Configuration initialized successfully")
    except Exception as e:
        print_error(f"Failed to initialize configuration: {e}")
        raise click.Abort()


# Test serializers command
@cli.command("test-serializers")
def test_serializers() -> None:
    """Test all serializers in the aceiot-models package."""
    from .test_serializers import run_all_serializer_tests

    click.echo("Running serializer tests...")
    try:
        results = run_all_serializer_tests()

        # Display results
        total_tests = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total_tests - passed

        click.echo(f"\n{'=' * 60}")
        click.echo("SERIALIZER TEST RESULTS")
        click.echo(f"{'=' * 60}")

        for result in results:
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            click.echo(f"{status} | {result['test_name']}")
            if not result["passed"]:
                click.echo(f"       Error: {result['error']}")

        click.echo(f"{'=' * 60}")
        click.echo(f"Total: {total_tests} | Passed: {passed} | Failed: {failed}")

        if failed > 0:
            import sys

            sys.exit(1)
        else:
            print_success("All serializer tests passed!")
    except Exception as e:
        print_error(f"Failed to run serializer tests: {e}")
        import sys

        sys.exit(1)


# REPL command
@cli.command("repl")
@click.pass_context
def repl_mode(ctx: Context) -> None:
    """Start interactive REPL mode."""
    from .repl import AceIoTRepl

    repl = AceIoTRepl(ctx)
    repl.start()


# Entry point
def main() -> None:
    """Main entry point for the CLI."""
    cli(obj={})


if __name__ == "__main__":
    main()
