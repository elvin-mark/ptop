"""Configuration loader and management for ptop."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "ptop"
CONFIG_FILE = CONFIG_DIR / "config.json"


@dataclass
class Config:
    theme: str = "catppuccin"
    refresh_rate_ms: int = 1000
    temp_unit: str = "C"  # "C" or "F"
    layout: str = "full"  # "full", "compact", "gpu", "proc"
    show_cpu: bool = True
    show_mem: bool = True
    show_disk: bool = True
    show_net: bool = True
    show_gpu: bool = True
    show_proc: bool = True
    show_alerts: bool = True
    proc_sort_by: str = "cpu"  # "cpu", "mem", "pid", "name", "disk", "user"
    proc_sort_reverse: bool = True
    proc_tree_view: bool = False

    # Alert Thresholds
    alert_cpu_percent: float = 90.0
    alert_mem_percent: float = 85.0
    alert_temp_celsius: float = 85.0
    alert_disk_percent: float = 90.0

    @classmethod
    def load(cls) -> "Config":
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, encoding="utf-8") as f:
                    data = json.load(f)
                    return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
            except Exception:
                pass
        return cls()

    def save(self) -> None:
        try:
            CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(asdict(self), f, indent=2)
        except Exception:
            pass
