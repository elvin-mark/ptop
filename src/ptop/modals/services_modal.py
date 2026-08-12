"""Systemd Services Inspector Modal Screen with Live Search."""

import shutil
import subprocess

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from ptop.theme import Theme


class ServiceEntry:
    def __init__(self, name: str, load: str, active: str, sub: str, description: str):
        self.name = name
        self.load = load
        self.active = active
        self.sub = sub
        self.description = description


class ServicesModal(ModalScreen):
    """Modal displaying Systemd service units with live search."""

    def __init__(self, theme: Theme):
        super().__init__()
        self.theme = theme
        self.services: list[ServiceEntry] = []
        self._load_services()

    def _load_services(self) -> None:
        if not shutil.which("systemctl"):
            return
        try:
            cmd = ["systemctl", "list-units", "--type=service", "--no-pager", "--plain", "--all"]
            res = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=3.0)
            if res.returncode == 0 and res.stdout:
                for line in res.stdout.splitlines():
                    parts = line.strip().split(None, 4)
                    if len(parts) >= 5 and parts[0].endswith(".service"):
                        self.services.append(
                            ServiceEntry(
                                name=parts[0],
                                load=parts[1],
                                active=parts[2],
                                sub=parts[3],
                                description=parts[4],
                            )
                        )
        except Exception:
            pass

    def compose(self) -> ComposeResult:
        t = self.theme
        header_cols = (
            f"[{t.border_title}]{'SERVICE UNIT':<30} {'LOAD':<8} {'ACTIVE':<10} {'SUB':<10} {'DESCRIPTION':<30}[/]"
        )

        with Vertical(id="proc_detail_dialog"):
            yield Static(
                Text.from_markup(f"[bold {t.primary}]⚙ SYSTEMD SERVICES & UNITS ({len(self.services)})[/]"),
                id="services_header",
            )
            yield Input(
                placeholder="🔍 Search service name, status, or description (e.g. nginx, failed, running)...",
                id="services_search_input",
            )
            yield Static(Text.from_markup(header_cols + "\n" + f"[{t.text_muted}]" + "─" * 90 + "[/]"))
            with VerticalScroll(id="net_scroll_area"):
                yield Static(Text.from_markup(self._build_rendered_content("")), id="services_content")
            yield Button("Close (Esc)", variant="primary", id="close_btn")

    def on_mount(self) -> None:
        try:
            inp = self.query_one("#services_search_input", Input)
            inp.focus()
        except Exception:
            pass

    def _build_rendered_content(self, query: str) -> str:
        t = self.theme
        q = query.lower().strip()
        lines = []

        matching = [
            s
            for s in self.services
            if not q or q in s.name.lower() or q in s.active.lower() or q in s.sub.lower() or q in s.description.lower()
        ]

        for s in matching:
            status_color = t.mem_color if s.active == "active" else (t.error if s.active == "failed" else t.text_muted)
            lines.append(
                f"[{t.primary}]{s.name:<30}[/] [{t.text_muted}]{s.load:<8}[/] [{status_color}]{s.active:<10}[/] [{t.secondary}]{s.sub:<10}[/] [{t.text}]{s.description[:30]:<30}[/]"
            )

        if not lines:
            if q:
                lines.append(f"[{t.text_muted}]No matching systemd services for '{query}'.[/]")
            else:
                lines.append(f"[{t.text_muted}]No systemd service units found or systemd is not present.[/]")

        return "\n".join(lines)

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "services_search_input":
            try:
                content_static = self.query_one("#services_content", Static)
                content_static.update(Text.from_markup(self._build_rendered_content(event.value)))
            except Exception:
                pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

    def key_escape(self) -> None:
        self.dismiss()
