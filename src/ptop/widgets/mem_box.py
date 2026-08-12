"""Memory & Swap Monitoring Widget."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from ptop.metrics.memory import MemoryMetrics
from ptop.theme import Theme
from ptop.widgets.sparkline import BrailleSparkline


def fmt_bytes(b: float) -> str:
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if abs(b) < 1024.0:
            return f"{b:5.1f} {unit}"
        b /= 1024.0
    return f"{b:5.1f} PiB"


class MemBox(Vertical):
    """Widget displaying RAM and Swap utilization."""

    def __init__(self, theme: Theme, **kwargs):
        super().__init__(**kwargs)
        self.can_focus = True
        self.border_title = " MEMORY & SWAP "
        self.theme = theme
        self.metrics: MemoryMetrics | None = None
        self.info_label = Static(id="mem_info")
        self.sparkline = BrailleSparkline(color=theme.mem_color, id="mem_sparkline")

    def on_click(self) -> None:
        self.focus()

    def compose(self) -> ComposeResult:
        yield self.info_label
        yield self.sparkline

    def update_metrics(self, metrics: MemoryMetrics, theme: Theme) -> None:
        self.metrics = metrics
        self.theme = theme
        self.sparkline.chart_color = theme.mem_color
        self.sparkline.update_data(metrics.history, max_val=100.0)

        t = self.theme
        bar_len = 16
        ram_filled = round((metrics.ram_percent / 100.0) * bar_len)
        ram_bar = "█" * ram_filled + "░" * (bar_len - ram_filled)
        ram_color = t.error if metrics.ram_percent > 90 else (t.warning if metrics.ram_percent > 75 else t.mem_color)

        swap_filled = round((metrics.swap_percent / 100.0) * bar_len) if metrics.swap_total_bytes > 0 else 0
        swap_bar = "█" * swap_filled + "░" * (bar_len - swap_filled)
        swap_color = t.warning if metrics.swap_percent > 50 else t.secondary

        lines = [
            f"[bold {t.secondary}]RAM[/] [{t.text}]{metrics.ram_percent:5.1f}%[/] [{ram_color}][{ram_bar}][/] [{t.text}]{fmt_bytes(metrics.ram_used_bytes)} / {fmt_bytes(metrics.ram_total_bytes)}[/]",
            f"     [{t.text_muted}]Avail: {fmt_bytes(metrics.ram_available_bytes)} | Cached: {fmt_bytes(metrics.ram_cached_bytes)}[/]",
            f"[bold {t.secondary}]SWP[/] [{t.text}]{metrics.swap_percent:5.1f}%[/] [{swap_color}][{swap_bar}][/] [{t.text}]{fmt_bytes(metrics.swap_used_bytes)} / {fmt_bytes(metrics.swap_total_bytes)}[/]",
        ]

        self.info_label.update(Text.from_markup("\n".join(lines)))
