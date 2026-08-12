"""Network Monitoring Widget."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from ptop.metrics.net import NetMetrics
from ptop.theme import Theme
from ptop.widgets.mem_box import fmt_bytes
from ptop.widgets.sparkline import BrailleSparkline


class NetBox(Vertical):
    """Widget displaying Network traffic speeds and interface statistics."""

    def __init__(self, theme: Theme, **kwargs):
        super().__init__(**kwargs)
        self.border_title = " NETWORK "
        self.theme = theme
        self.metrics: NetMetrics | None = None
        self.info_label = Static(id="net_info")
        self.rx_sparkline = BrailleSparkline(color=theme.net_rx_color, id="net_rx_sparkline")
        self.tx_sparkline = BrailleSparkline(color=theme.net_tx_color, id="net_tx_sparkline")

    def compose(self) -> ComposeResult:
        yield self.info_label
        yield self.rx_sparkline
        yield self.tx_sparkline

    def update_metrics(self, metrics: NetMetrics, theme: Theme) -> None:
        self.metrics = metrics
        self.theme = theme
        self.rx_sparkline.chart_color = theme.net_rx_color
        self.tx_sparkline.chart_color = theme.net_tx_color

        max_rate = max(1.0, max(metrics.rx_history + metrics.tx_history, default=1.0))
        self.rx_sparkline.update_data(metrics.rx_history, max_val=max_rate)
        self.tx_sparkline.update_data(metrics.tx_history, max_val=max_rate)

        t = self.theme
        lines = [
            f"[bold {t.net_rx_color}]NET RX (Down):[/] [{t.text}]{fmt_bytes(metrics.total_rx_bytes_sec)}/s[/] [dim]({fmt_bytes(metrics.total_rx_bytes)} total)[/]",
            f"[bold {t.net_tx_color}]NET TX (Up)  :[/] [{t.text}]{fmt_bytes(metrics.total_tx_bytes_sec)}/s[/] [dim]({fmt_bytes(metrics.total_tx_bytes)} total)[/]",
        ]

        for iface in metrics.interfaces[:3]:
            status = "UP" if iface.is_up else "DOWN"
            status_color = t.mem_color if iface.is_up else t.error
            lines.append(
                f" [{t.primary}]{iface.name:<8}[/] [{status_color}]{status}[/] [{t.text}]▼ {fmt_bytes(iface.rx_bytes_sec)}/s ▲ {fmt_bytes(iface.tx_bytes_sec)}/s[/]"
            )

        self.info_label.update(Text.from_markup("\n".join(lines)))
