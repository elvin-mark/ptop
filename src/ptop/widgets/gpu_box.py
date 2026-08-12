"""GPU Monitoring Widget."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from ptop.metrics.gpu import GPUMetrics
from ptop.theme import Theme
from ptop.widgets.mem_box import fmt_bytes
from ptop.widgets.sparkline import BrailleSparkline


class GPUBox(Vertical):
    """Widget displaying GPU utilization, VRAM, and temperatures."""

    def __init__(self, theme: Theme, **kwargs):
        super().__init__(**kwargs)
        self.border_title = " GPU "
        self.theme = theme
        self.metrics: GPUMetrics | None = None
        self.info_label = Static(id="gpu_info")
        self.sparkline = BrailleSparkline(color=theme.gpu_color, id="gpu_sparkline")

    def compose(self) -> ComposeResult:
        yield self.info_label
        yield self.sparkline

    def update_metrics(self, metrics: GPUMetrics, theme: Theme) -> None:
        self.metrics = metrics
        self.theme = theme
        self.sparkline.chart_color = theme.gpu_color

        t = self.theme
        if not metrics.available or not metrics.gpus:
            self.sparkline.update_data([], max_val=100.0)
            msg = f"[bold {t.gpu_color}]GPU[/] [{t.text_muted}]Integrated Graphics / Host Accelerator (Shared System Memory)[/]"
            self.info_label.update(Text.from_markup(msg))
            return

        gpu = metrics.gpus[0]
        self.sparkline.update_data(gpu.history, max_val=100.0)

        bar_len = 16
        filled = round((gpu.vram_percent / 100.0) * bar_len)
        vram_bar = "█" * filled + "░" * (bar_len - filled)

        temp_str = f" | {gpu.temperature_c:.0f}°C" if gpu.temperature_c else ""
        power_str = f" | {gpu.power_watts:.1f}W" if gpu.power_watts else ""

        lines = [
            f"[bold {t.gpu_color}]GPU[/] [{t.primary}]{gpu.name[:24]}[/] [{t.text}]{gpu.usage_percent:5.1f}%[/]{temp_str}{power_str}",
            f"     [{t.secondary}]VRAM[/] [{t.text}]{gpu.vram_percent:5.1f}%[/] [{t.gpu_color}][{vram_bar}][/] [{t.text}]{fmt_bytes(gpu.vram_used_bytes)} / {fmt_bytes(gpu.vram_total_bytes)}[/]",
        ]

        self.info_label.update(Text.from_markup("\n".join(lines)))
