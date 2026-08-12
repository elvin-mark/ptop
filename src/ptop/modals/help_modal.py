"""Help Modal Dialog Screen."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static

from ptop.theme import Theme


class HelpModal(ModalScreen):
    """Modal displaying keybindings and command reference."""

    def __init__(self, theme: Theme):
        super().__init__()
        self.theme = theme

    def compose(self) -> ComposeResult:
        t = self.theme
        help_text = (
            f"[bold {t.primary}]⚡ PTOP KEYBOARD REFERENCE & HELP[/]\n\n"
            f"[bold {t.secondary}]Navigation & Views[/]\n"
            f"  [bold {t.accent}]Up / Down / j / k[/] : Navigate process table list\n"
            f"  [bold {t.accent}]PageUp / PageDown[/]  : Scroll process table by page\n"
            f"  [bold {t.accent}]B[/]                 : Cycle color themes (Catppuccin, TokyoNight, Nord, Dracula, Cyberpunk)\n"
            f"  [bold {t.accent}]L[/]                 : Toggle layout presets (Full, Compact, GPU Focus, Process Focus)\n"
            f"  [bold {t.accent}]Z[/]                 : Toggle Panel Zoom / Fullscreen mode\n"
            f"  [bold {t.accent}]E[/]                 : Export System Performance Snapshot Report (Markdown/JSON)\n"
            f"  [bold {t.accent}]N[/]                 : Open Network Connections & Sockets Inspector\n"
            f"  [bold {t.accent}]A[/]                 : Toggle Health Alerts drawer\n\n"
            f"[bold {t.secondary}]Process Operations[/]\n"
            f"  [bold {t.accent}]/[/]                 : Filter / Search processes by PID, Name, User, or Command\n"
            f"  [bold {t.accent}]Esc[/]               : Clear active process filter\n"
            f"  [bold {t.accent}]S[/]                 : Cycle process sort column (CPU%, MEM%, PID, Name, Disk I/O, User)\n"
            f"  [bold {t.accent}]R[/]                 : Reverse process sort direction\n"
            f"  [bold {t.accent}]T[/]                 : Toggle Process Tree hierarchy view\n"
            f"  [bold {t.accent}]I / Enter[/]         : Inspect detailed process information (Files, Connections, Threads)\n"
            f"  [bold {t.accent}]K[/]                 : Send signal to selected process (SIGKILL 9, SIGTERM 15, etc.)\n\n"
            f"[bold {t.secondary}]General[/]\n"
            f"  [bold {t.accent}]?[/]                 : Show this help modal\n"
            f"  [bold {t.error}]Q / Ctrl+C[/]        : Quit ptop\n"
        )

        with Vertical(id="help_dialog"):
            yield Static(Text.from_markup(help_text), id="help_content")
            yield Button("Close (Esc)", variant="primary", id="close_btn")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss()

    def key_escape(self) -> None:
        self.dismiss()
