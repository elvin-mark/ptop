"""Memory and Swap metrics collector."""

from collections import deque
from dataclasses import dataclass, field

import psutil


@dataclass
class MemoryMetrics:
    ram_total_bytes: int = 0
    ram_used_bytes: int = 0
    ram_free_bytes: int = 0
    ram_available_bytes: int = 0
    ram_cached_bytes: int = 0
    ram_percent: float = 0.0
    swap_total_bytes: int = 0
    swap_used_bytes: int = 0
    swap_free_bytes: int = 0
    swap_percent: float = 0.0
    history: list[float] = field(default_factory=list)


class MemoryCollector:
    def __init__(self, history_len: int = 60):
        self.history_len = history_len
        self.history: deque = deque(maxlen=history_len)

    def collect(self) -> MemoryMetrics:
        vm = psutil.virtual_memory()
        sw = psutil.swap_memory()

        ram_cached = getattr(vm, "cached", 0) or getattr(vm, "buffers", 0)

        self.history.append(vm.percent)

        return MemoryMetrics(
            ram_total_bytes=vm.total,
            ram_used_bytes=vm.used,
            ram_free_bytes=vm.free,
            ram_available_bytes=vm.available,
            ram_cached_bytes=ram_cached,
            ram_percent=vm.percent,
            swap_total_bytes=sw.total,
            swap_used_bytes=sw.used,
            swap_free_bytes=sw.free,
            swap_percent=sw.percent,
            history=list(self.history),
        )
