"""Hardware Sensors & Battery Dashboard Modal Screen."""

import psutil
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ptop.theme import Theme


class SensorsModal(ModalScreen):
    """Modal displaying ACPI thermal sensors, fan speeds, and battery state."""

    def __init__(self, theme: Theme):
        super().__init__()
        self.theme = theme

    def compose(self) -> ComposeResult:
        t = self.theme
        lines = [f"[bold {t.primary}]🌡️ HARDWARE SENSORS & BATTERY DASHBOARD[/]\n"]

        # 1. Thermal Sensors
        lines.append(f"[bold {t.secondary}]🔥 Thermal Zones & Temperatures[/]")
        try:
            temps = psutil.sensors_temperatures()
            if temps:
                for sensor_name, entries in temps.items():
                    lines.append(f"  [{t.primary}]{sensor_name}[/]")
                    for e in entries:
                        label = e.label or "sensor"
                        high_str = f" (high: {e.high}°C)" if e.high else ""
                        crit_str = f" (crit: {e.critical}°C)" if e.critical else ""
                        temp_color = (
                            t.error
                            if (e.critical and e.current >= e.critical)
                            else (t.warning if (e.high and e.current >= e.high) else t.text)
                        )
                        lines.append(f"    • {label:<20}: [{temp_color}]{e.current:.1f}°C[/]{high_str}{crit_str}")
            else:
                lines.append(f"  [{t.text_muted}]No ACPI thermal sensors reported.[/]")
        except Exception as e:
            lines.append(f"  [{t.error}]Error reading thermal sensors: {e}[/]")

        lines.append("")

        # 2. Fan Speeds
        lines.append(f"[bold {t.secondary}]🌀 Cooling Fans[/]")
        try:
            fans = psutil.sensors_fans()
            if fans:
                for fan_name, entries in fans.items():
                    lines.append(f"  [{t.primary}]{fan_name}[/]")
                    for e in entries:
                        label = e.label or "fan"
                        lines.append(f"    • {label:<20}: [{t.disk_color}]{e.current} RPM[/]")
            else:
                lines.append(f"  [{t.text_muted}]No hardware cooling fan sensors reported.[/]")
        except Exception as e:
            lines.append(f"  [{t.error}]Error reading fan sensors: {e}[/]")

        lines.append("")

        # 3. Battery State
        lines.append(f"[bold {t.secondary}]🔋 Battery & Power Supply[/]")
        try:
            bat = psutil.sensors_battery()
            if bat:
                plugged = "AC Plugged In" if bat.power_plugged else "Discharging (Battery)"
                plugged_color = t.mem_color if bat.power_plugged else t.warning
                time_rem = "Calculating..."
                if bat.secsleft > 0:
                    mins = int(bat.secsleft // 60)
                    hrs = mins // 60
                    time_rem = f"{hrs}h {mins % 60}m"
                elif bat.secsleft == psutil.POWER_TIME_UNLIMITED:
                    time_rem = "Full / AC Powered"

                pct_color = t.mem_color if bat.percent > 50 else (t.warning if bat.percent > 20 else t.error)
                lines.append(f"  • Charge Level   : [{pct_color}]{bat.percent:.1f}%[/]")
                lines.append(f"  • Power Status   : [{plugged_color}]{plugged}[/]")
                lines.append(f"  • Time Remaining : [{t.text}]{time_rem}[/]")
            else:
                lines.append(f"  [{t.text_muted}]No battery detected (Desktop / AC system).[/]")
        except Exception as e:
            lines.append(f"  [{t.error}]Error reading battery state: {e}[/]")

        with Vertical(id="proc_detail_dialog"):
            with VerticalScroll():
                yield Static(Text.from_markup("\n".join(lines)), id="sensors_content")
            yield Button("Close (Esc)", variant="primary", id="close_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

    def key_escape(self) -> None:
        self.dismiss()
