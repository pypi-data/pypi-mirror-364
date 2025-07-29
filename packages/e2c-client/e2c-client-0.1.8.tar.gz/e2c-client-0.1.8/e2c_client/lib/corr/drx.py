import math
import struct

# try:
#     from CCL.AmbManager import AmbManager
#     import ControlExceptions
# except ModuleNotFoundError:
#     print("Failed to import CCL.AmbManager or ControlExceptions")

from rich.table import Table
from rich.console import Console

## Definitions
# DRXs CAN bus definitions in HILSE (OSF room)
CAN_ABM = "DMC"

# DRXs CAN bus definitions
CAN_CHANNEL_DRX0 = 2
CAN_NODE_DRX0 = 0x100
CAN_CHANNEL_DRX1 = 2
CAN_NODE_DRX1 = 0x101
CAN_CHANNEL_DRX2 = 2
CAN_NODE_DRX2 = 0x102
CAN_CHANNEL_DRX3 = 2
CAN_NODE_DRX3 = 0x103

# Monitor point definitions
RCA_GET_SIGNAL_AVG_D = 0x03102
RCA_GET_SIGNAL_AVG_C = 0x03202
RCA_GET_SIGNAL_AVG_B = 0x03302
RCA_GET_PARITY_COUNTER_D = 0x1502
RCA_GET_PARITY_COUNTER_C = 0x2502
RCA_GET_PARITY_COUNTER_B = 0x3502
RCA_GET_MFD_RAW = 0x0250A


def str2int(value):
    if "X" in value.upper():
        return int(value, 16)
    else:
        return int(value)


class Drx:
    def __init__(self, abm=None, nodes=None, channels=None) -> None:
        if abm is None:
            self.abm = CAN_ABM
        else:
            self.abm = abm

        try:
            # This import is done locally to avoid blocking response in case AmbManager is not available
            from CCL.AmbManager import AmbManager
            import ControlExceptions
        except ModuleNotFoundError as e:
            raise Exception("Failed to import CCL.AmbManager or ControlExceptions")
        except:
            raise
        else:
            try:
                self.mgr = AmbManager(self.abm)
                self.ControlExceptions = ControlExceptions
            except Exception as e:
                raise Exception(f"Failed to instantiate {self.abm} AmbManager")

        if nodes is None:
            self.node0 = CAN_NODE_DRX0
            self.node1 = CAN_NODE_DRX1
            self.node2 = CAN_NODE_DRX2
            self.node3 = CAN_NODE_DRX3
        else:
            try:
                _nodes = nodes.split(",")
            except:
                raise Exception("Failed to expand nodes list")

            self.node0 = str2int(_nodes[0])
            self.node1 = str2int(_nodes[1])
            self.node2 = str2int(_nodes[2])
            self.node3 = str2int(_nodes[3])

        if channels is None:
            self.channel0 = CAN_CHANNEL_DRX0
            self.channel1 = CAN_CHANNEL_DRX1
            self.channel2 = CAN_CHANNEL_DRX2
            self.channel3 = CAN_CHANNEL_DRX3
        else:
            try:
                _channels = channels.split(",")
            except:
                raise Exception("Failed to expand channels list")

            self.channel0 = int(_channels[0])
            self.channel1 = int(_channels[1])
            self.channel2 = int(_channels[2])
            self.channel3 = int(_channels[3])

    def __del__(self):
        try:
            del self.mgr
        except:
            pass

    def get_drx_status(self):
        """HILSE correlator DRXs 0 to 3 average bits power"""

        table = Table(title="HILSE CORR DRXs status", row_styles=["o", "", ""])
        table.add_column("DRX/bit", justify="right")
        table.add_column("Avg pwr \[nW]", justify="right")
        table.add_column("Avg pwr \[dBm]", justify="right")
        table.add_column("Parity counter \[]", justify="right")
        table.add_column("Raw mfd \[]", justify="right")

        # Received optical power and parity counter per bit
        for channel, node, rca_pwr, rca_parity, rca_mfd_raw, label in [
            (
                self.channel0,
                self.node0,
                RCA_GET_SIGNAL_AVG_D,
                RCA_GET_PARITY_COUNTER_D,
                RCA_GET_MFD_RAW,
                "DRX0 bit D",
            ),
            (
                self.channel0,
                self.node0,
                RCA_GET_SIGNAL_AVG_C,
                RCA_GET_PARITY_COUNTER_C,
                None,
                "DRX0 bit C",
            ),
            (
                self.channel0,
                self.node0,
                RCA_GET_SIGNAL_AVG_B,
                RCA_GET_PARITY_COUNTER_B,
                None,
                "DRX0 bit B",
            ),
            (
                self.channel1,
                self.node1,
                RCA_GET_SIGNAL_AVG_D,
                RCA_GET_PARITY_COUNTER_D,
                RCA_GET_MFD_RAW,
                "DRX1 bit D",
            ),
            (
                self.channel1,
                self.node1,
                RCA_GET_SIGNAL_AVG_C,
                RCA_GET_PARITY_COUNTER_C,
                None,
                "DRX1 bit C",
            ),
            (
                self.channel1,
                self.node1,
                RCA_GET_SIGNAL_AVG_B,
                RCA_GET_PARITY_COUNTER_B,
                None,
                "DRX1 bit B",
            ),
            (
                self.channel2,
                self.node2,
                RCA_GET_SIGNAL_AVG_D,
                RCA_GET_PARITY_COUNTER_D,
                RCA_GET_MFD_RAW,
                "DRX2 bit D",
            ),
            (
                self.channel2,
                self.node2,
                RCA_GET_SIGNAL_AVG_C,
                RCA_GET_PARITY_COUNTER_C,
                None,
                "DRX2 bit C",
            ),
            (
                self.channel2,
                self.node2,
                RCA_GET_SIGNAL_AVG_B,
                RCA_GET_PARITY_COUNTER_B,
                None,
                "DRX2 bit B",
            ),
            (
                self.channel3,
                self.node3,
                RCA_GET_SIGNAL_AVG_D,
                RCA_GET_PARITY_COUNTER_D,
                RCA_GET_MFD_RAW,
                "DRX3 bit D",
            ),
            (
                self.channel3,
                self.node3,
                RCA_GET_SIGNAL_AVG_C,
                RCA_GET_PARITY_COUNTER_C,
                None,
                "DRX3 bit C",
            ),
            (
                self.channel3,
                self.node3,
                RCA_GET_SIGNAL_AVG_B,
                RCA_GET_PARITY_COUNTER_B,
                None,
                "DRX3 bit B",
            ),
        ]:
            try:
                monitor = self.mgr.monitor(channel, node, rca_pwr)
            except self.ControlExceptions.CAMBErrorEx:
                raise Exception(f"Node {hex(node)}/ch{channel} not found on {self.abm}")

            # GET_SIGNAL_AVG: 3 Bytes: MSByte first, 24 bits twos complement. 1 nW/count
            power_nw = int.from_bytes(monitor[0], "big", signed=True)
            power_dbm = 10 * math.log10(power_nw / 1e6)

            good_power = True
            if power_dbm < -15:
                good_power = False
            if power_dbm > -3:
                good_power = False

            try:
                monitor = self.mgr.monitor(channel, node, rca_parity)
            except self.ControlExceptions.CAMBErrorEx:
                raise Exception(f"Node {hex(node)}/ch{channel} not found on {self.abm}")

            # GET_DFR_PARITY_COUNTER: 8 bytes
            parity_counter = struct.unpack(">Q", monitor[0])[0]

            if rca_mfd_raw is not None:
                try:
                    monitor = self.mgr.monitor(channel, node, rca_mfd_raw)
                except self.ControlExceptions.CAMBErrorEx:
                    raise Exception(
                        f"Node {hex(node)}/ch{channel} not found on {self.abm}"
                    )

                # GET_METAFRAME_DELAY_RAW: 3 bytes, number of 62.5MHz clocks counted
                mfd_raw = struct.unpack(">I", b"\0" + monitor[0])[0]
            else:
                mfd_raw = ""

            table.add_row(
                label,
                f"{power_nw}",
                f"[green]{power_dbm:.2f}[/green]"
                if good_power
                else f"[red]{power_dbm:.2f}[/red]",
                str(parity_counter),
                str(mfd_raw),
            )

        console = Console()
        print()
        console.print(table)
        print()
