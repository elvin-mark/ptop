"""Main Textual Application for ptop."""

import asyncio
from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container

from ptop.alerts import Alert, AlertManager
from ptop.config import Config
from ptop.metrics.collector import MetricsCollector, SystemSnapshot
from ptop.modals.filter_modal import FilterModal
from ptop.modals.help_modal import HelpModal
from ptop.modals.kill_modal import KillModal
from ptop.modals.proc_detail_modal import ProcDetailModal
from ptop.theme import THEMES, Theme, get_theme
from ptop.widgets.alerts_box import AlertsBox
from ptop.widgets.cpu_box import CPUBox
from ptop.widgets.disk_box import DiskBox
from ptop.widgets.footer import FooterBar
from ptop.widgets.gpu_box import GPUBox
from ptop.widgets.header import HeaderBar
from ptop.widgets.mem_box import MemBox
from ptop.widgets.net_box import NetBox
from ptop.widgets.proc_box import ProcessBox

CSS_PATH = Path(__file__).parent / "styles" / "default.tcss"


class PtopApp(App):
    """Next-generation Python System Monitor TUI."""

    CSS_PATH = CSS_PATH
    BINDINGS = [
        Binding("b", "cycle_theme", "Theme", show=False),
        Binding("l", "cycle_layout", "Layout", show=False),
        Binding("s", "cycle_sort", "Sort", show=False),
        Binding("r", "toggle_sort_order", "Reverse Sort", show=False),
        Binding("t", "toggle_tree", "Tree Mode", show=False),
        Binding("slash", "open_filter", "Search", show=False),
        Binding("escape", "clear_filter", "Clear Filter", show=False),
        Binding("k", "kill_process", "Kill", show=False),
        Binding("i", "inspect_process", "Inspect", show=False),
        Binding("enter", "inspect_process", "Inspect", show=False),
        Binding("a", "toggle_alerts", "Alerts", show=False),
        Binding("question", "show_help", "Help", show=False),
        Binding("up", "move_up", "Up", show=False),
        Binding("down", "move_down", "Down", show=False),
        Binding("j", "move_down", "Down", show=False),
        Binding("pageup", "page_up", "Page Up", show=False),
        Binding("pagedown", "page_down", "Page Down", show=False),
        Binding("q", "quit_app", "Quit", show=True),
    ]

    LAYOUTS = ["full", "compact", "gpu", "proc"]
    SORT_COLUMNS = ["cpu", "mem", "pid", "name", "disk", "user"]

    def __init__(self):
        super().__init__()
        self.config = Config.load()
        self.active_theme: Theme = get_theme(self.config.theme)
        self.collector = MetricsCollector()
        self.alert_mgr = AlertManager()

        self.filter_query: str = ""
        self.sort_by: str = self.config.proc_sort_by
        self.sort_reverse: bool = self.config.proc_sort_reverse
        self.tree_mode: bool = self.config.proc_tree_view
        self.show_alerts: bool = self.config.show_alerts
        self.current_layout: str = self.config.layout

        self.header_bar = HeaderBar(theme=self.active_theme, layout_name=self.current_layout, id="app_header")
        self.footer_bar = FooterBar(
            theme=self.active_theme,
            filter_query=self.filter_query,
            sort_by=self.sort_by,
            tree_mode=self.tree_mode,
            id="app_footer",
        )
        self.cpu_box = CPUBox(theme=self.active_theme, id="cpu_panel")
        self.mem_box = MemBox(theme=self.active_theme, id="mem_panel")
        self.disk_box = DiskBox(theme=self.active_theme, id="disk_panel")
        self.net_box = NetBox(theme=self.active_theme, id="net_panel")
        self.gpu_box = GPUBox(theme=self.active_theme, id="gpu_panel")
        self.proc_box = ProcessBox(theme=self.active_theme, id="proc_panel")
        self.alerts_box = AlertsBox(theme=self.active_theme, id="alerts_panel")

    def compose(self) -> ComposeResult:
        yield self.header_bar
        with Container(id="main_content"):
            yield self.cpu_box
            yield self.mem_box
            yield self.disk_box
            yield self.net_box
            yield self.gpu_box
            yield self.proc_box
            if self.show_alerts:
                yield self.alerts_box
        yield self.footer_bar

    async def on_mount(self) -> None:
        self.title = "ptop"
        self._apply_layout_class()
        # Schedule periodic background metrics refresh timer
        self.set_interval(self.config.refresh_rate_ms / 1000.0, self._update_metrics)

    def _apply_layout_class(self) -> None:
        try:
            main_content = self.query_one("#main_content")
            for layout_name in self.LAYOUTS:
                main_content.remove_class(f"layout-{layout_name}")
            main_content.add_class(f"layout-{self.current_layout}")
        except Exception:
            pass

    async def _update_metrics(self) -> None:
        snapshot: SystemSnapshot = await self.collector.collect_all(
            sort_by=self.sort_by,
            reverse=self.sort_reverse,
            filter_query=self.filter_query,
            tree_mode=self.tree_mode,
        )

        active_alerts: list[Alert] = self.alert_mgr.check(snapshot, self.config)

        self.cpu_box.update_metrics(snapshot.cpu, self.active_theme)
        self.mem_box.update_metrics(snapshot.memory, self.active_theme)
        self.disk_box.update_metrics(snapshot.disk, self.active_theme)
        self.net_box.update_metrics(snapshot.net, self.active_theme)
        self.gpu_box.update_metrics(snapshot.gpu, self.active_theme)
        self.proc_box.update_metrics(snapshot.procs, self.active_theme)
        if self.show_alerts:
            self.alerts_box.update_alerts(active_alerts, self.active_theme)

        self.header_bar.update_info(self.active_theme, self.current_layout)
        self.footer_bar.update_state(self.active_theme, self.filter_query, self.sort_by, self.tree_mode)

    # Keybinding actions
    def action_move_up(self) -> None:
        self.proc_box.move_cursor(-1)

    def action_move_down(self) -> None:
        self.proc_box.move_cursor(1)

    def action_page_up(self) -> None:
        self.proc_box.move_cursor(-10)

    def action_page_down(self) -> None:
        self.proc_box.move_cursor(10)

    def action_cycle_theme(self) -> None:
        theme_names = list(THEMES.keys())
        curr_idx = theme_names.index(self.active_theme.name) if self.active_theme.name in theme_names else 0
        next_theme_name = theme_names[(curr_idx + 1) % len(theme_names)]
        self.active_theme = get_theme(next_theme_name)
        self.config.theme = next_theme_name
        self.config.save()
        asyncio.create_task(self._update_metrics())

    def action_cycle_layout(self) -> None:
        curr_idx = self.LAYOUTS.index(self.current_layout) if self.current_layout in self.LAYOUTS else 0
        self.current_layout = self.LAYOUTS[(curr_idx + 1) % len(self.LAYOUTS)]
        self.config.layout = self.current_layout
        self.config.save()
        self._apply_layout_class()
        asyncio.create_task(self._update_metrics())

    def action_cycle_sort(self) -> None:
        curr_idx = self.SORT_COLUMNS.index(self.sort_by) if self.sort_by in self.SORT_COLUMNS else 0
        self.sort_by = self.SORT_COLUMNS[(curr_idx + 1) % len(self.SORT_COLUMNS)]
        self.config.proc_sort_by = self.sort_by
        self.config.save()
        asyncio.create_task(self._update_metrics())

    def action_toggle_sort_order(self) -> None:
        self.sort_reverse = not self.sort_reverse
        self.config.proc_sort_reverse = self.sort_reverse
        self.config.save()
        asyncio.create_task(self._update_metrics())

    def action_toggle_tree(self) -> None:
        self.tree_mode = not self.tree_mode
        self.config.proc_tree_view = self.tree_mode
        self.config.save()
        asyncio.create_task(self._update_metrics())

    def action_toggle_alerts(self) -> None:
        self.show_alerts = not self.show_alerts
        self.config.show_alerts = self.show_alerts
        self.config.save()
        asyncio.create_task(self._update_metrics())

    def action_open_filter(self) -> None:
        def on_filter_done(result: str | None) -> None:
            if result is not None:
                self.filter_query = result
                asyncio.create_task(self._update_metrics())

        self.push_screen(FilterModal(self.filter_query, self.active_theme), on_filter_done)

    def action_clear_filter(self) -> None:
        self.filter_query = ""
        asyncio.create_task(self._update_metrics())

    def action_kill_process(self) -> None:
        proc = self.proc_box.get_selected_process()
        if not proc:
            return

        def on_kill_done(result_msg: str | None) -> None:
            if result_msg:
                self.notify(result_msg, title="Process Signal")
                asyncio.create_task(self._update_metrics())

        self.push_screen(KillModal(proc, self.active_theme), on_kill_done)

    def action_inspect_process(self) -> None:
        proc = self.proc_box.get_selected_process()
        if not proc:
            return
        self.push_screen(ProcDetailModal(proc, self.active_theme))

    def action_show_help(self) -> None:
        self.push_screen(HelpModal(self.active_theme))

    def action_quit_app(self) -> None:
        self.collector.close()
        self.exit()
