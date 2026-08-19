"""Custom Application Footer Shortcut Widget."""

from rich.text import Text
from textual.widgets import Static

from ptop.theme import Theme


class FooterBar(Static):
    """Application bottom shortcut legend bar."""

    def __init__(self, theme: Theme, filter_query: str = "", sort_by: str = "cpu", tree_mode: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.theme = theme
        self.filter_query = filter_query
        self.sort_by = sort_by
        self.tree_mode = tree_mode

    def update_state(self, theme: Theme, filter_query: str, sort_by: str, tree_mode: bool) -> None:
        self.theme = theme
        self.filter_query = filter_query
        self.sort_by = sort_by
        self.tree_mode = tree_mode
        self.refresh()

    def render(self) -> Text:
        t = self.theme

        filter_str = f" [{t.warning}]Filter: '{self.filter_query}'[/]" if self.filter_query else ""
        tree_str = f" [{t.secondary}][TREE: Space/F Fold][/]" if self.tree_mode else ""
        sort_str = f" [{t.primary}]Sort:{self.sort_by.upper()}[/]"

        shortcuts = [
            f"[reverse {t.primary}] B [/] Theme",
            f"[reverse {t.primary}] L [/] Layout",
            f"[reverse {t.primary}] Z [/] Zoom",
            f"[reverse {t.primary}] E [/] Export",
            f"[reverse {t.primary}] N [/] Sockets",
            f"[reverse {t.primary}] V [/] Services",
            f"[reverse {t.primary}] H [/] Sensors",
            f"[reverse {t.primary}] S [/] Sort",
            f"[reverse {t.primary}] / [/] Filter",
            f"[reverse {t.primary}] T [/] Tree",
            f"[reverse {t.primary}] K [/] Kill",
            f"[reverse {t.primary}] I [/] Inspect",
            f"[reverse {t.error}] Q [/] Quit",
        ]

        content = " ".join(shortcuts) + f" |{sort_str}{tree_str}{filter_str}"
        return Text.from_markup(content)
