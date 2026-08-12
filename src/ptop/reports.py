"""System performance report exporter for ptop."""

import json
import time
from pathlib import Path

from ptop.metrics.collector import SystemSnapshot
from ptop.widgets.mem_box import fmt_bytes

REPORTS_DIR = Path.home() / ".config" / "ptop" / "reports"


def export_snapshot_report(snapshot: SystemSnapshot, fmt: str = "markdown") -> Path:
    """Exports a performance snapshot to ~/.config/ptop/reports/."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestr = time.strftime("%Y-%m-%d_%H%M%S")

    if fmt == "json":
        filepath = REPORTS_DIR / f"snapshot_{timestr}.json"
        data = {
            "timestamp": snapshot.timestamp,
            "cpu": {
                "model": snapshot.cpu.model,
                "usage_percent": snapshot.cpu.total_usage,
                "cores": snapshot.cpu.logical_cores,
                "load_avg": list(snapshot.cpu.load_avg),
                "temp_c": snapshot.cpu.temperature_c,
            },
            "memory": {
                "ram_percent": snapshot.memory.ram_percent,
                "ram_used_bytes": snapshot.memory.ram_used_bytes,
                "ram_total_bytes": snapshot.memory.ram_total_bytes,
                "swap_percent": snapshot.memory.swap_percent,
            },
            "top_processes": [
                {
                    "pid": p.pid,
                    "name": p.name,
                    "user": p.user,
                    "cpu_percent": p.cpu_percent,
                    "mem_percent": p.mem_percent,
                    "cmdline": p.cmdline,
                }
                for p in snapshot.procs.items[:10]
            ],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return filepath

    # Default Markdown format
    filepath = REPORTS_DIR / f"snapshot_{timestr}.md"
    lines = [
        "# ⚡ PTOP System Performance Report",
        f"**Generated**: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(snapshot.timestamp))}",
        "",
        "## 💻 CPU Overview",
        f"- **Model**: {snapshot.cpu.model}",
        f"- **Total Utilization**: {snapshot.cpu.total_usage:.1f}%",
        f"- **Threads/Cores**: {snapshot.cpu.logical_cores}",
        f"- **Load Average**: {snapshot.cpu.load_avg[0]:.2f}, {snapshot.cpu.load_avg[1]:.2f}, {snapshot.cpu.load_avg[2]:.2f}",
        f"- **Frequency**: {snapshot.cpu.freq_current_ghz:.2f} GHz",
        f"- **Temperature**: {f'{snapshot.cpu.temperature_c:.1f}°C' if snapshot.cpu.temperature_c else 'N/A'}",
        "",
        "## 🧠 Memory & Swap",
        f"- **RAM Usage**: {snapshot.memory.ram_percent:.1f}% ({fmt_bytes(snapshot.memory.ram_used_bytes)} / {fmt_bytes(snapshot.memory.ram_total_bytes)})",
        f"- **RAM Available**: {fmt_bytes(snapshot.memory.ram_available_bytes)}",
        f"- **Swap Usage**: {snapshot.memory.swap_percent:.1f}% ({fmt_bytes(snapshot.memory.swap_used_bytes)} / {fmt_bytes(snapshot.memory.swap_total_bytes)})",
        "",
        "## 💾 Disk Partitions",
    ]

    for part in snapshot.disk.partitions:
        lines.append(
            f"- **{part.mountpoint}**: {part.percent:.1f}% used ({fmt_bytes(part.used_bytes)} / {fmt_bytes(part.total_bytes)})"
        )

    lines.extend(
        [
            "",
            "## 🌐 Network Speed",
            f"- **Download (RX)**: {fmt_bytes(snapshot.net.total_rx_bytes_sec)}/s (Total: {fmt_bytes(snapshot.net.total_rx_bytes)})",
            f"- **Upload (TX)**: {fmt_bytes(snapshot.net.total_tx_bytes_sec)}/s (Total: {fmt_bytes(snapshot.net.total_tx_bytes)})",
            "",
            "## ⚡ Top 10 Resource Processes",
            "| PID | USER | CPU% | MEM% | RSS | COMMAND |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )

    for p in snapshot.procs.items[:10]:
        lines.append(
            f"| {p.pid} | {p.user} | {p.cpu_percent:.1f}% | {p.mem_percent:.1f}% | {fmt_bytes(p.mem_rss_bytes)} | `{p.cmdline[:40]}` |"
        )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath
