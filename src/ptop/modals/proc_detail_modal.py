"""Detailed Process Inspector Modal Screen."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ptop.metrics.process import ProcessItem, get_process_details
from ptop.theme import Theme


class ProcDetailModal(ModalScreen):
    """Modal displaying deep inspect details for a process."""

    def __init__(self, process: ProcessItem, theme: Theme):
        super().__init__()
        self.process = process
        self.theme = theme

    def compose(self) -> ComposeResult:
        t = self.theme
        p = self.process
        details = get_process_details(p.pid)

        lines = [f"[bold {t.primary}]🔍 PROCESS DETAILS - PID {p.pid}[/]\n"]
        for k, v in details.items():
            lines.append(f"[bold {t.secondary}]{k}:[/] [{t.text}]{v}[/]")

        with Vertical(id="proc_detail_dialog"):
            with VerticalScroll():
                yield Static(Text.from_markup("\n".join(lines)), id="proc_detail_content")
            yield Button("Close (Esc)", variant="primary", id="close_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

    def key_escape(self) -> None:
        self.dismiss()
