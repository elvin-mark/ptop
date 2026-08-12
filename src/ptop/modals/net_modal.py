"""Network Socket Connections Inspector Modal Screen."""

import psutil
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ptop.theme import Theme


class NetSocketsModal(ModalScreen):
    """Modal displaying active TCP/UDP network connections."""

    def __init__(self, theme: Theme):
        super().__init__()
        self.theme = theme

    def compose(self) -> ComposeResult:
        t = self.theme
        lines = [f"[bold {t.primary}]🌐 ACTIVE NETWORK SOCKETS & CONNECTIONS[/]\n"]
        lines.append(
            f"[{t.border_title}]{'PROTO':<6} {'LOCAL ADDRESS':<24} {'REMOTE ADDRESS':<24} {'STATUS':<12} {'PID':>6} {'PROCESS':<16}[/]"
        )
        lines.append(f"[{t.text_muted}]" + "─" * 90 + "[/]")

        try:
            conns = psutil.net_connections(kind="inet")
            count = 0
            for c in conns:
                if count >= 25:
                    break
                laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "*"
                raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "*"
                proto = "TCP" if c.type == 1 else "UDP"
                status = c.status if c.status else "NONE"
                pid_str = str(c.pid) if c.pid else "-"

                proc_name = "N/A"
                if c.pid:
                    try:
                        proc_name = psutil.Process(c.pid).name()[:16]
                    except Exception:
                        proc_name = "unknown"

                status_color = (
                    t.mem_color if status == "ESTABLISHED" else (t.warning if status == "LISTEN" else t.text_muted)
                )

                lines.append(
                    f"[{t.secondary}]{proto:<6}[/] [{t.text}]{laddr:<24}[/] [{t.text}]{raddr:<24}[/] [{status_color}]{status:<12}[/] {pid_str:>6} [{t.primary}]{proc_name:<16}[/]"
                )
                count += 1

            if count == 0:
                lines.append(f"[{t.text_muted}]No active inet connections found or permission denied.[validation]")

        except Exception as e:
            lines.append(f"[{t.error}]Error fetching network connections: {e}[/]")

        with Vertical(id="proc_detail_dialog"):
            yield Static(Text.from_markup("\n".join(lines)), id="net_content")
            yield Button("Close (Esc)", variant="primary", id="close_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

    def key_escape(self) -> None:
        self.dismiss()
