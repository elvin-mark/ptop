"""Health Alerts Widget."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from ptop.alerts import Alert
from ptop.theme import Theme


class AlertsBox(Vertical):
    """Widget rendering system health notifications."""

    def __init__(self, theme: Theme, **kwargs):
        super().__init__(**kwargs)
        self.border_title = " ALERTS "
        self.theme = theme
        self.alerts: list[Alert] = []
        self.alerts_label = Static(id="alerts_label")

    def compose(self) -> ComposeResult:
        yield self.alerts_label

    def update_alerts(self, alerts: list[Alert], theme: Theme) -> None:
        self.alerts = alerts
        self.theme = theme

        t = self.theme
        lines = [f"[bold {t.warning}]SYSTEM HEALTH & ALERTS[/]"]

        if not alerts:
            lines.append(f" [{t.mem_color}]✓ System Operating Normally. No Active Alerts.[/]")
        else:
            for alert in alerts[:4]:
                color = t.error if alert.severity == "CRITICAL" else t.warning
                lines.append(
                    f" [{t.text_muted}]{alert.time_str}[/] [{color}][{alert.severity}][{alert.category}][/] [{t.text}]{alert.message}[/]"
                )

        self.alerts_label.update(Text.from_markup("\n".join(lines)))
