"""Custom Application Header Widget."""

import platform
import time

import psutil
from rich.text import Text
from textual.widgets import Static

from ptop.theme import Theme


def get_uptime_str() -> str:
    try:
        boot_time = psutil.boot_time()
        uptime_secs = int(time.time() - boot_time)
        days, rem = divmod(uptime_secs, 86400)
        hours, rem = divmod(rem, 3600)
        mins, secs = divmod(rem, 60)
        if days > 0:
            return f"{days}d {hours}h {mins}m"
        return f"{hours}h {mins}m {secs}s"
    except Exception:
        return "N/A"


class HeaderBar(Static):
    """Application top header bar."""

    def __init__(self, theme: Theme, layout_name: str = "Full", **kwargs):
        super().__init__(**kwargs)
        self.theme = theme
        self.layout_name = layout_name
        self.hostname = platform.node() or "localhost"
        self.sys_info = f"{platform.system()} {platform.release()}"

    def update_info(self, theme: Theme, layout_name: str) -> None:
        self.theme = theme
        self.layout_name = layout_name
        self.refresh()

    def render(self) -> Text:
        t = self.theme
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        uptime = get_uptime_str()

        content = (
            f"[bold {t.primary}]⚡ PTOP v0.1.0[/] [{t.accent}]|[/] "
            f"[{t.text}]Host: [bold]{self.hostname}[/][/] [{t.text_muted}]({self.sys_info})[/] [{t.accent}]|[/] "
            f"[{t.text}]Up: [bold]{uptime}[/][/] [{t.accent}]|[/] "
            f"[{t.text}]Layout: [bold {t.secondary}]{self.layout_name.upper()}[/][/] [{t.accent}]|[/] "
            f"[{t.text}]Theme: [bold {t.primary}]{t.label}[/][/] [{t.accent}]|[/] "
            f"[{t.border_title}]{now_str}[/]"
        )
        return Text.from_markup(content)
