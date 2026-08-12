"""Process Search / Filter Input Modal Screen."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Static

from ptop.theme import Theme


class FilterModal(ModalScreen[str | None]):
    """Modal input dialog for process search filter."""

    def __init__(self, current_filter: str, theme: Theme):
        super().__init__()
        self.current_filter = current_filter
        self.theme = theme

    def compose(self) -> ComposeResult:
        t = self.theme
        msg = f"[bold {t.primary}]🔍 FILTER PROCESSES[/]\n[{t.text_muted}]Search PID, Name, User, or Command line (Esc to clear/cancel):[/]"

        with Vertical(id="filter_dialog"):
            yield Static(Text.from_markup(msg), id="filter_msg")
            yield Input(
                value=self.current_filter,
                placeholder="Type search query...",
                id="filter_input",
            )
            with Horizontal():
                yield Button("Apply (Enter)", variant="primary", id="apply_btn")
                yield Button("Clear", variant="warning", id="clear_btn")
                yield Button("Cancel", variant="default", id="cancel_btn")

    def on_mount(self) -> None:
        inp = self.query_one("#filter_input", Input)
        inp.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value.strip())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id
        if bid == "apply_btn":
            inp = self.query_one("#filter_input", Input)
            self.dismiss(inp.value.strip())
        elif bid == "clear_btn":
            self.dismiss("")
        else:
            self.dismiss(None)

    def key_escape(self) -> None:
        self.dismiss(None)
