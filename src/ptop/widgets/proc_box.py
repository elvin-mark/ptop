"""Interactive Process Table and Tree Widget."""

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from ptop.metrics.process import ProcessItem, ProcessTree
from ptop.theme import Theme
from ptop.widgets.mem_box import fmt_bytes


class ProcessBox(Vertical):
    """Widget rendering process table/tree with interactive selection and tree folding."""

    def __init__(self, theme: Theme, **kwargs):
        super().__init__(**kwargs)
        self.can_focus = True
        self.border_title = " PROCESSES "
        self.theme = theme
        self.tree_data: ProcessTree | None = None
        self.selected_index: int = 0
        self.items: list[ProcessItem] = []
        self.table_label = Static(id="proc_table")

    def on_click(self) -> None:
        self.focus()

    def compose(self) -> ComposeResult:
        yield self.table_label

    def update_metrics(self, tree_data: ProcessTree, theme: Theme) -> None:
        self.tree_data = tree_data
        self.theme = theme
        self.items = tree_data.items

        if self.items:
            self.selected_index = max(0, min(self.selected_index, len(self.items) - 1))
        else:
            self.selected_index = 0

        t = self.theme
        lines = []

        lines.append(
            f"[bold {t.primary}]PROCESSES[/] [{t.text}]Total: {tree_data.total_processes}[/] | [{t.mem_color}]Running: {tree_data.running_count}[/] | [{t.text_muted}]Sleeping: {tree_data.sleeping_count}[/] | [{t.warning}]Stopped: {tree_data.stopped_count}[/]"
        )

        header = f"[{t.border_title}]{'PID':>7} {'USER':<9} {'CPU%':>6} {'MEM%':>6} {'RSS':>9} {'TH':>4} {'DISK I/O':>11} {'NAME / COMMAND':<32}[/]"
        lines.append(header)
        lines.append(f"[{t.text_muted}]" + "─" * 92 + "[/]")

        max_rows = max(5, self.content_size.height - 4) if self.content_size.height > 4 else 15
        start_idx = max(0, min(self.selected_index - max_rows // 2, max(0, len(self.items) - max_rows)))
        visible_items = self.items[start_idx : start_idx + max_rows]

        for idx, proc in enumerate(visible_items):
            actual_idx = start_idx + idx
            is_selected = actual_idx == self.selected_index

            indent = ("  " * (proc.depth - 1) + "├─") if proc.depth > 0 else ""

            if proc.child_count > 0:
                if proc.is_collapsed:
                    branch_icon = f"[{t.secondary}]▶[dim]+{proc.child_count}[/] [/]"
                    plain_branch = f"▶+{proc.child_count} "
                else:
                    branch_icon = f"[{t.primary}]▼[/] "
                    plain_branch = "▼ "
            else:
                branch_icon = "" if proc.depth == 0 else " "
                plain_branch = "" if proc.depth == 0 else " "

            tree_prefix = f"[{t.text_muted}]{indent}[/]{branch_icon}" if indent else branch_icon
            plain_prefix = indent + plain_branch

            max_cmd_len = 32
            raw_cmd = proc.cmdline
            avail_len = max(10, max_cmd_len - len(plain_prefix))
            if len(raw_cmd) > avail_len:
                raw_cmd = raw_cmd[: max(0, avail_len - 3)] + "..."

            cmd_display = f"{tree_prefix}{raw_cmd}"

            container_badge = f" [{t.secondary}][DOCKER][/]" if proc.is_container else ""

            disk_io_val = proc.read_bytes_sec + proc.write_bytes_sec
            disk_io_str = f"{fmt_bytes(disk_io_val)}/s" if disk_io_val > 0 else "0 B/s"

            cpu_color = t.error if proc.cpu_percent > 80 else (t.warning if proc.cpu_percent > 40 else t.text)
            mem_color = t.error if proc.mem_percent > 20 else (t.warning if proc.mem_percent > 10 else t.text)

            row_str = (
                f"{proc.pid:>7} {proc.user[:9]:<9} [{cpu_color}]{proc.cpu_percent:>6.1f}[/] [{mem_color}]{proc.mem_percent:>6.1f}[/] "
                f"{fmt_bytes(proc.mem_rss_bytes):>9} {proc.threads:>4} {disk_io_str:>11} {cmd_display:<32}{container_badge}"
            )

            if is_selected:
                lines.append(f"[bold reverse {t.primary}]▶ {row_str}[/]")
            else:
                lines.append(f"  {row_str}")

        self.table_label.update(Text.from_markup("\n".join(lines)))

    def get_selected_process(self) -> ProcessItem | None:
        if self.items and 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None

    def move_cursor(self, delta: int) -> None:
        if self.items:
            self.selected_index = max(0, min(self.selected_index + delta, len(self.items) - 1))
            if self.tree_data:
                self.update_metrics(self.tree_data, self.theme)
