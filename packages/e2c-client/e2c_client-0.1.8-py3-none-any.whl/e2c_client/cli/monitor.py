import typer
from typing import Optional

from e2c_client import E2CClient

monitor_app = typer.Typer(short_help="E2C monitoring related commands")


@monitor_app.callback()
def monitor_app_callback():
    """
    Perform monitoring requests for E2C-controlled devices.

    Usage:

    \b
    e2c-client monitor --help
    e2c-client monitor request --host <host> --channel <channel> --node <node> --rca <RCA>

    Example:
    Get attenuators on IFP0 of DA63. Returns: A:12 dB, B:12.5 dB, C:9 dB, D:8.5 dB

    $ e2c-client monitor request --host da63-e2c --channel 0 --node 0x29 --rca 0x0101
    Error: 0
    Data:
    0x60, 0x64, 0x48, 0x44

    """


@monitor_app.command("request", short_help="Perform AMB monitor request")
def request(
    host: Optional[str] = typer.Option(None, help="E2C hostname or IP address"),
    port: Optional[int] = typer.Option(2000, help="E2C socket server port"),
    channel: Optional[str] = typer.Option(None, help="LRU channel number"),
    node: Optional[str] = typer.Option(None, help="LRU node address"),
    rca: Optional[str] = typer.Option(None, help="Monitor request RCA"),
):
    try:
        client = E2CClient(host, port)
        error, data = client.send_request(
            resource_id=0,  # ignored, kept in the API for backwards compatibility
            bus_id=E2CClient.converter(channel),
            node_id=E2CClient.converter(node),
            can_addr=E2CClient.converter(rca),
            mode=0,
            data=b"",
        )
        print(f"Error: {error}")
        print("Data: ")
        print(", ".join(hex(b) for b in data))
    except Exception as e:
        print(f"Error: {str(e)}")


@monitor_app.command(
    "temperature", short_help="Perform AMB monitor request for AMBSI temperature"
)
def temperature(
    host: Optional[str] = typer.Option(None, help="E2C hostname or IP address"),
    port: Optional[int] = typer.Option(2000, help="E2C socket server port"),
    channel: Optional[str] = typer.Option(None, help="LRU channel number"),
    node: Optional[str] = typer.Option(None, help="LRU node address"),
):
    try:
        client = E2CClient(host, port)
        temp = client.get_temperature_c(
            E2CClient.converter(channel), E2CClient.converter(node)
        )
        print(f"Temperature: {temp} [C]")
    except Exception as e:
        print(f"Error: {str(e)}")


@monitor_app.command("nodes", short_help="List all CAN nodes reported by E2C host")
def nodes(
    host: Optional[str] = typer.Option(None, help="E2C hostname or IP address"),
    port: Optional[int] = typer.Option(2000, help="E2C socket server port"),
):
    try:
        client = E2CClient(host, port)
        client.get_all_nodes()
    except Exception as e:
        print(f"Error: {str(e)}")
