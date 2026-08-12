"""Process Kill / Signal Modal Dialog Screen."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ptop.metrics.process import ProcessItem, send_process_signal
from ptop.theme import Theme


class KillModal(ModalScreen[str | None]):
    """Modal dialog to choose signal for target process."""

    def __init__(self, process: ProcessItem, theme: Theme):
        super().__init__()
        self.process = process
        self.theme = theme

    def compose(self) -> ComposeResult:
        t = self.theme
        p = self.process

        msg = (
            f"[bold {t.error}]SEND SIGNAL TO PROCESS[/]\n\n"
            f"PID: [bold {t.primary}]{p.pid}[/]\n"
            f"Name: [bold {t.text}]{p.name}[/]\n"
            f"Command: [{t.text_muted}]{p.cmdline[:50]}[/]\n\n"
            f"Select signal to send:"
        )

        with Vertical(id="kill_dialog"):
            yield Static(Text.from_markup(msg), id="kill_msg")
            with Horizontal(classes="signal_buttons"):
                yield Button("SIGTERM (15)", variant="warning", id="sig_15")
                yield Button("SIGKILL (9)", variant="error", id="sig_9")
                yield Button("SIGSTOP (19)", variant="default", id="sig_19")
                yield Button("SIGCONT (18)", variant="default", id="sig_18")
            yield Button("Cancel (Esc)", variant="default", id="cancel_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        sig_map = {
            "sig_15": 15,
            "sig_9": 9,
            "sig_19": 19,
            "sig_18": 18,
        }
        if button_id in sig_map:
            sig_num = sig_map[button_id]
            _ok, result_msg = send_process_signal(self.process.pid, sig_num)
            self.dismiss(result_msg)
        else:
            self.dismiss(None)

    def key_escape(self) -> None:
        self.dismiss(None)
