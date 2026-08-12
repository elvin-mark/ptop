"""Network Socket Connections Inspector Modal Screen with Live Search."""

import psutil
from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from ptop.theme import Theme


class SocketEntry:
    def __init__(self, proto: str, laddr: str, raddr: str, status: str, pid: str, proc_name: str):
        self.proto = proto
        self.laddr = laddr
        self.raddr = raddr
        self.status = status
        self.pid = pid
        self.proc_name = proc_name


class NetSocketsModal(ModalScreen):
    """Modal displaying active TCP/UDP network connections with live search & scrolling."""

    def __init__(self, theme: Theme):
        super().__init__()
        self.theme = theme
        self.entries: list[SocketEntry] = []
        self._load_connections()

    def _load_connections(self) -> None:
        try:
            conns = psutil.net_connections(kind="inet")
            for c in conns:
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

                self.entries.append(SocketEntry(proto, laddr, raddr, status, pid_str, proc_name))
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        t = self.theme
        header_cols = f"[{t.border_title}]{'PROTO':<6} {'LOCAL ADDRESS':<24} {'REMOTE ADDRESS':<24} {'STATUS':<12} {'PID':>6} {'PROCESS':<16}[/]"

        with Vertical(id="proc_detail_dialog"):
            yield Static(
                Text.from_markup(f"[bold {t.primary}]🌐 ACTIVE NETWORK SOCKETS & CONNECTIONS ({len(self.entries)})[/]"),
                id="net_header",
            )
            yield Input(
                placeholder="🔍 Search port, IP, process, or status (e.g. 8080, LISTEN, python)...",
                id="net_search_input",
            )
            yield Static(Text.from_markup(header_cols + "\n" + f"[{t.text_muted}]" + "─" * 90 + "[/]"))
            with VerticalScroll(id="net_scroll_area"):
                yield Static(Text.from_markup(self._build_rendered_content("")), id="net_content")
            yield Button("Close (Esc)", variant="primary", id="close_btn")

    def on_mount(self) -> None:
        try:
            inp = self.query_one("#net_search_input", Input)
            inp.focus()
        except Exception:
            pass

    def _build_rendered_content(self, query: str) -> str:
        t = self.theme
        q = query.lower().strip()
        lines = []

        matching = [
            e
            for e in self.entries
            if not q
            or q in e.laddr.lower()
            or q in e.raddr.lower()
            or q in e.proc_name.lower()
            or q in e.status.lower()
            or q in e.proto.lower()
            or q in e.pid.lower()
        ]

        for e in matching:
            status_color = (
                t.mem_color if e.status == "ESTABLISHED" else (t.warning if e.status == "LISTEN" else t.text_muted)
            )
            lines.append(
                f"[{t.secondary}]{e.proto:<6}[/] [{t.text}]{e.laddr:<24}[/] [{t.text}]{e.raddr:<24}[/] [{status_color}]{e.status:<12}[/] {e.pid:>6} [{t.primary}]{e.proc_name:<16}[/]"
            )

        if not lines:
            if q:
                lines.append(f"[{t.text_muted}]No matching network sockets for '{query}'.[/]")
            else:
                lines.append(f"[{t.text_muted}]No active inet connections found or permission denied.[validation]")

        return "\n".join(lines)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "net_search_input":
            try:
                content_static = self.query_one("#net_content", Static)
                content_static.update(Text.from_markup(self._build_rendered_content(event.value)))
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

    def key_escape(self) -> None:
        self.dismiss()
