import struct
import sys
import math

from rich.table import Table
from rich.console import Console
from rich.text import Text

## Definitions
# LFTRR/LORR CAN bus definitions in HILSE (OSF room)
CAN_CHANNEL = 1
CAN_NODE = 0x22
CAN_ABM = "DMC"

# Monitor point definitions
RCA_STATUS = 0x00001
RCA_RX_OPT_PWR = 0x00007
RCA_TE_LENGTH = 0x00011
RCA_TE_OFFSET_COUNTER = 0x00012

# Status monitor point bit definitions
# Byte 1
FLAG_DCM_LOCKED = 0b1
FLAG_12V_OUT_OF_RANGE = 0b10
FLAG_15V_OUT_OF_RANGE = 0b100
FLAG_RX_OPT_PWR_ERROR = 0b1000
FLAG_2GHZ_UNLOCKED = 0b10000  # clear with CLEAR_FLAGS
FLAG_125MHZ_UNLOCKED = 0b100000  # clear with CLEAR_FLAGS
# Byte 2
FLAG_TE_SHORT = 0b1  # clear with CLEAR_FLAGS
FLAG_TE_LONG = 0b10  # clear with CLEAR_FLAGS

# Control points definitions
RCA_RESYNC_TE = 0x00081
RCA_CLEAR_FLAGS = 0x00082

# Nominal ranges
RANGE_RX_OPT_PWR_MIN = -15
RANGE_RX_OPT_PWR_MAX = +5
RANGE_TE_LENGTH_EQ = 5999999
RANGE_TE_OFFSET_EQ = 2


class Lftrr:
    def __init__(self, abm=None, node=None, channel=None) -> None:
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

        if node is None:
            self.node = CAN_NODE
        else:
            self.node = node

        if channel is None:
            self.channel = CAN_CHANNEL
        else:
            self.channel = channel

    def __del__(self):
        try:
            del self.mgr
        except:
            pass

    def status(self):
        """General healthcheck of the LFTRR, limited to relevant variables for HILSE"""

        table = Table(title="HILSE LFTRR STATUS")
        table.add_column("Parameter", justify="right")
        table.add_column("Value", justify="right")

        # Received optical power
        try:
            monitor = self.mgr.monitor(self.channel, self.node, RCA_RX_OPT_PWR)
        except self.ControlExceptions.CAMBErrorEx:
            raise Exception(
                f"Node {hex(self.node)}/ch{self.channel} not found on {self.abm} bus"
            )

        power_raw = struct.unpack(">H", monitor[0])
        power_mw = power_raw[0] * 20 / 4095
        power_dbm = 10 * math.log10(power_mw)

        good_power = True
        if power_dbm < RANGE_RX_OPT_PWR_MIN:
            good_power = False
        if power_dbm > RANGE_RX_OPT_PWR_MAX:
            good_power = False

        table.add_row(
            "Rx optical power",
            f"[green]{power_dbm:.2f}[/green] \[dBm]"
            if good_power
            else f"[red]{power_dbm:.2f}[/red] \[dBm]",
        )

        # TE length
        monitor = self.mgr.monitor(self.channel, self.node, RCA_TE_LENGTH)
        te_length = struct.unpack(">I", b"\0" + monitor[0])[0]

        table.add_row(
            "TE length",
            f"[green]{te_length}[/green]"
            if te_length == RANGE_TE_LENGTH_EQ
            else f"[red]{te_length}[/red]",
        )

        # TE offset
        monitor = self.mgr.monitor(self.channel, self.node, RCA_TE_OFFSET_COUNTER)
        te_offset = struct.unpack(">I", b"\0" + monitor[0])[0]

        table.add_row(
            "TE offset",
            f"[green]{te_offset}[/green]"
            if te_offset == RANGE_TE_OFFSET_EQ
            else f"[red]{te_offset}[/red]",
        )

        # STATUS bits
        monitor = self.mgr.monitor(self.channel, CAN_NODE, RCA_STATUS)
        status = struct.unpack("2B", monitor[0])

        flag_dcm_locked = 1 * bool(status[0] & FLAG_DCM_LOCKED)
        flag_12v_out_of_range = 1 * bool(status[0] & FLAG_12V_OUT_OF_RANGE)
        flag_15v_out_of_range = 1 * bool(status[0] & FLAG_15V_OUT_OF_RANGE)
        flag_rx_opt_pwr_error = 1 * bool(status[0] & FLAG_RX_OPT_PWR_ERROR)
        flag_2ghz_unlocked = 1 * bool(status[0] & FLAG_2GHZ_UNLOCKED)
        flag_125mhz_unlocked = 1 * bool(status[0] & FLAG_125MHZ_UNLOCKED)
        flag_te_short = 1 * bool(status[1] & FLAG_TE_SHORT)
        flag_te_long = 1 * bool(status[1] & FLAG_TE_LONG)

        flags = []
        if not flag_dcm_locked:
            flags.append("DCM unlocked")
        if flag_12v_out_of_range:
            flags.append("12V out of range")
        if flag_15v_out_of_range:
            flags.append("15V out of range")
        if flag_rx_opt_pwr_error:
            flags.append("Rx optical signal not detected")
        if flag_2ghz_unlocked:
            flags.append("2 GHz unlocked")
        if flag_125mhz_unlocked:
            flags.append("125 MHz unlocked")
        if flag_te_short:
            flags.append("TE short detected")
        if flag_te_long:
            flags.append("TE long detected")

        table.add_row(
            "125 MHz",
            f"[green]Locked[/green]"
            if not flag_125mhz_unlocked
            else f"[red]Unlocked[/red]",
        )

        table.add_row("Error flags", "[red]" + "\n".join(flags) + "[/red]")
        console = Console()
        print()
        console.print(table)
        print()

        print(
            "Run 'alma-hilse timing resync' to sync to central reference and clear flags"
        )
        print()

    def resync_te(self):
        """Resync LFTRR to external reference from CLO"""

        self.clear_flags()
        try:
            self.mgr.command(
                self.channel, self.node, RCA_RESYNC_TE, struct.pack("1B", 0x01)
            )
        except self.ControlExceptions.CAMBErrorEx:
            raise Exception(
                f"Node {hex(self.node)}/ch{self.channel} not found on {self.abm} bus"
            )

        self.clear_flags()

        print("Resync command was sent")
        self.status()

    def clear_flags(self):
        """Clear latched warning and error flags"""

        try:
            self.mgr.command(
                self.channel, self.node, RCA_CLEAR_FLAGS, struct.pack("1B", 0x01)
            )
        except self.ControlExceptions.CAMBErrorEx:
            raise Exception(
                f"Node {hex(self.node)}/ch{self.channel} not found on {self.abm} bus"
            )

        print("Clear flags command was sent")
