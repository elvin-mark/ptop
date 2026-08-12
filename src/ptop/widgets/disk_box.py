"""Disk Space & I/O Monitoring Widget."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from ptop.metrics.disk import DiskMetrics
from ptop.theme import Theme
from ptop.widgets.mem_box import fmt_bytes
from ptop.widgets.sparkline import BrailleSparkline


class DiskBox(Vertical):
    """Widget displaying Disk partitions and Read/Write IO speeds."""

    def __init__(self, theme: Theme, **kwargs):
        super().__init__(**kwargs)
        self.can_focus = True
        self.border_title = " DISK "
        self.theme = theme
        self.metrics: DiskMetrics | None = None
        self.info_label = Static(id="disk_info")
        self.read_sparkline = BrailleSparkline(color=theme.disk_color, id="disk_read_sparkline")
        self.write_sparkline = BrailleSparkline(color=theme.warning, id="disk_write_sparkline")

    def compose(self) -> ComposeResult:
        yield self.info_label
        yield self.read_sparkline
        yield self.write_sparkline

    def update_metrics(self, metrics: DiskMetrics, theme: Theme) -> None:
        self.metrics = metrics
        self.theme = theme
        self.read_sparkline.chart_color = theme.disk_color
        self.write_sparkline.chart_color = theme.warning

        max_io = max(1.0, max(metrics.read_history + metrics.write_history, default=1.0))
        self.read_sparkline.update_data(metrics.read_history, max_val=max_io)
        self.write_sparkline.update_data(metrics.write_history, max_val=max_io)

        t = self.theme
        lines = [
            f"[bold {t.disk_color}]DISK I/O[/] [{t.text}]Read: {fmt_bytes(metrics.read_bytes_sec)}/s[/] | [{t.text}]Write: {fmt_bytes(metrics.write_bytes_sec)}/s[/]",
        ]

        for p in metrics.partitions[:4]:
            bar_len = 10
            filled = round((p.percent / 100.0) * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            color = t.error if p.percent > 90 else (t.warning if p.percent > 75 else t.disk_color)
            lines.append(
                f" [{t.primary}]{p.mountpoint[:12]:<12}[/] [{color}][{bar}][/] [{t.text}]{p.percent:5.1f}%[/] [{t.text_muted}]({fmt_bytes(p.used_bytes)} / {fmt_bytes(p.total_bytes)})[/]"
            )

        self.info_label.update(Text.from_markup("\n".join(lines)))
