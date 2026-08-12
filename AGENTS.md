# AGENTS.md

## Overview

`ptop` is a terminal system monitor built with **Python 3.11+**, **Textual**, **Rich**, and **psutil**, packaged and managed with **uv**.

It provides real-time system metrics (CPU, RAM, Swap, Disk I/O, Network, GPU, and Processes) with Unicode Braille sparklines, multiple layout presets, interactive process management (tree view, search filter, signal sender, inspector), theme switching, and health alerting.

---

## Directory Structure

```
ptop/
├── pyproject.toml              # Project dependencies, Hatchling build system, Ruff config
├── README.md                   # User documentation
├── AGENTS.md                   # AI Agent guidance & architectural conventions
├── .vscode/
│   └── settings.json           # VSCode environment configuration
├── src/
│   └── ptop/
│       ├── __init__.py
│       ├── cli.py              # CLI entry point (argparse)
│       ├── app.py              # Main Textual App (PtopApp)
│       ├── config.py           # Configuration manager & persistence (~/.config/ptop/config.json)
│       ├── theme.py            # Theme definitions (Catppuccin, TokyoNight, Nord, Dracula, Cyberpunk)
│       ├── alerts.py           # Health evaluation & alert thresholds
│       ├── metrics/            # Hardware & system metric collectors
│       │   ├── __init__.py
│       │   ├── cpu.py          # CPU usage, per-core stats, freq, load avg, temp
│       │   ├── memory.py       # RAM & Swap statistics
│       │   ├── disk.py          # Partitions space & Read/Write I/O throughput
│       │   ├── net.py           # Network interface speeds (RX/TX) & totals
│       │   ├── gpu.py           # NVIDIA NVML & fallback GPU metrics
│       │   ├── process.py       # Process sampling, tree hierarchy, signals, inspection
│       │   └── collector.py     # Async ThreadPoolExecutor metrics orchestrator
│       ├── widgets/            # Custom Textual TUI components
│       │   ├── __init__.py
│       │   ├── sparkline.py     # Unicode Braille sparkline widget
│       │   ├── cpu_box.py       # CPU monitoring panel
│       │   ├── mem_box.py       # Memory & Swap panel
│       │   ├── disk_box.py      # Disk partition & I/O panel
│       │   ├── net_box.py       # Network traffic panel
│       │   ├── gpu_box.py       # GPU status panel
│       │   ├── proc_box.py      # Interactive process table & tree panel
│       │   ├── alerts_box.py    # Health alerts panel
│       │   ├── header.py        # Top application header bar
│       │   └── footer.py        # Bottom application shortcut legend
│       ├── modals/             # Modal dialog screens
│       │   ├── __init__.py
│       │   ├── help_modal.py    # Keyboard shortcut cheat sheet
│       │   ├── kill_modal.py    # Process signal dialog (SIGKILL, SIGTERM, etc.)
│       │   ├── proc_detail_modal.py # Process deep inspector modal
│       │   └── filter_modal.py  # Process search filter modal
│       └── styles/
│           └── default.tcss    # Textual CSS styling & layout rules
└── tests/
    ├── __init__.py
    ├── test_alerts.py
    ├── test_app.py
    ├── test_config.py
    ├── test_metrics.py
    └── test_sparkline.py
```

---

## Development Workflow & Tooling

### Package Manager
This repository uses `uv` for dependency management and running tools.

### Running the App
```bash
uv run ptop
```

### Running Tests
```bash
uv run pytest
```

### Code Formatting & Linting
Formatting and linting are strictly enforced with `ruff`:
```bash
# Format codebase
uv run ruff format .

# Check & auto-fix linting rules
uv run ruff check --fix .
```

---

## Key Architectural Rules for Agents

1. **Avoid Collision with Textual App Attributes**:
   - Textual's `App` class defines a built-in reactive property `theme` expecting a string.
   - Do NOT store the custom `Theme` object in `self.theme` on `PtopApp`. Use `self.active_theme` instead.

2. **Panel Widget Composition**:
   - Panel widgets (`CPUBox`, `MemBox`, `DiskBox`, `NetBox`, `GPUBox`) MUST inherit from `Vertical` (or `Container`) and yield separate sub-widgets (`info_label: Static` and `sparkline: BrailleSparkline`).
   - Do NOT override `render()` on parent containers that yield child widgets, as child widgets will overlap canvas text.

3. **TCSS Styling Rules**:
   - `border-title` is NOT a valid TCSS CSS property. Set `self.border_title = "..."` on Python widget instances inside `__init__`.
   - `border-title-color`, `border-title-align`, and `border-title-style` are valid TCSS properties.

4. **Async Non-blocking Metrics Gathering**:
   - All `psutil` and system metrics collection must be executed in thread pool workers via `MetricsCollector.collect_all()` so the main Textual event loop is never blocked.
