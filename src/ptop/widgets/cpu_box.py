"""CPU Monitoring Widget."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from ptop.metrics.cpu import CPUMetrics
from ptop.theme import Theme
from ptop.widgets.sparkline import BrailleSparkline


class CPUBox(Vertical):
    """Container widget for CPU stats and sparkline chart."""

    def __init__(self, theme: Theme, **kwargs):
        super().__init__(**kwargs)
        self.border_title = " CPU "
        self.theme = theme
        self.metrics: CPUMetrics | None = None
        self.info_label = Static(id="cpu_info")
        self.sparkline = BrailleSparkline(color=theme.cpu_color, id="cpu_sparkline")

    def compose(self) -> ComposeResult:
        yield self.info_label
        yield self.sparkline

    def update_metrics(self, metrics: CPUMetrics, theme: Theme) -> None:
        self.metrics = metrics
        self.theme = theme
        self.sparkline.chart_color = theme.cpu_color
        self.sparkline.update_data(metrics.history, max_val=100.0)

        t = self.theme
        temp_str = f" | {metrics.temperature_c:.1f}°C" if metrics.temperature_c else ""
        freq_str = f" | {metrics.freq_current_ghz:.2f} GHz" if metrics.freq_current_ghz > 0 else ""
        load_str = f"Load: {metrics.load_avg[0]:.2f} {metrics.load_avg[1]:.2f} {metrics.load_avg[2]:.2f}"

        lines = [
            f"[bold {t.primary}]CPU[/] [{t.text}]{metrics.total_usage:5.1f}%[/] [{t.text_muted}]({metrics.logical_cores} threads{freq_str}{temp_str})[/] [dim]{load_str}[/]"
        ]

        cores = metrics.per_core_usage
        if cores:
            core_strs = []
            for i, pct in enumerate(cores[:16]):
                bar_len = 6
                filled = round((pct / 100.0) * bar_len)
                bar = "█" * filled + "░" * (bar_len - filled)
                color = t.error if pct > 85 else (t.warning if pct > 60 else t.cpu_color)
                core_strs.append(f"C{i:02d}:[{color}]{bar}[/]{pct:3.0f}%")

            for row_start in range(0, len(core_strs), 4):
                lines.append("  ".join(core_strs[row_start : row_start + 4]))

        self.info_label.update(Text.from_markup("\n".join(lines)))
