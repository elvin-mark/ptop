"""CPU metrics collector."""

import platform
from collections import deque
from dataclasses import dataclass, field

import psutil


@dataclass
class CPUMetrics:
    model: str = ""
    physical_cores: int = 0
    logical_cores: int = 0
    total_usage: float = 0.0
    per_core_usage: list[float] = field(default_factory=list)
    freq_current_ghz: float = 0.0
    freq_min_ghz: float = 0.0
    freq_max_ghz: float = 0.0
    load_avg: tuple[float, float, float] = (0.0, 0.0, 0.0)
    temperature_c: float | None = None
    history: list[float] = field(default_factory=list)


class CPUCollector:
    def __init__(self, history_len: int = 60):
        self.history_len = history_len
        self.history: deque = deque(maxlen=history_len)
        self.physical_cores = psutil.cpu_count(logical=False) or 1
        self.logical_cores = psutil.cpu_count(logical=True) or 1
        self.model = self._get_cpu_model()
        # Prime psutil cpu counters so first collect() call has valid non-zero delta
        try:
            psutil.cpu_percent(interval=None, percpu=True)
        except Exception:
            pass

    def _get_cpu_model(self) -> str:
        try:
            if platform.system() == "Linux":
                with open("/proc/cpuinfo") as f:
                    for line in f:
                        if "model name" in line:
                            return line.split(":")[1].strip()
            elif platform.system() == "Darwin":
                import subprocess

                res = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
        except Exception:
            pass
        return f"{platform.processor() or 'CPU'} ({self.logical_cores} threads)"

    def collect(self) -> CPUMetrics:
        total_usage = psutil.cpu_percent(interval=None)
        per_core = psutil.cpu_percent(interval=None, percpu=True)

        freq_curr, freq_min, freq_max = 0.0, 0.0, 0.0
        try:
            freq_info = psutil.cpu_freq()
            if freq_info:
                freq_curr = freq_info.current / 1000.0 if freq_info.current else 0.0
                freq_min = freq_info.min / 1000.0 if freq_info.min else 0.0
                freq_max = freq_info.max / 1000.0 if freq_info.max else 0.0
        except Exception:
            pass

        load_1, load_5, load_15 = 0.0, 0.0, 0.0
        try:
            if hasattr(psutil, "getloadavg"):
                load_1, load_5, load_15 = psutil.getloadavg()
        except Exception:
            pass

        temp_c: float | None = None
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for key in ["coretemp", "k10temp", "cpu_thermal", "acpitz", "zenpower"]:
                        if key in temps and temps[key]:
                            temp_c = temps[key][0].current
                            break
                    if temp_c is None:
                        for entry_list in temps.values():
                            if entry_list:
                                temp_c = entry_list[0].current
                                break
        except Exception:
            pass

        self.history.append(total_usage)

        return CPUMetrics(
            model=self.model,
            physical_cores=self.physical_cores,
            logical_cores=self.logical_cores,
            total_usage=total_usage,
            per_core_usage=per_core,
            freq_current_ghz=freq_curr,
            freq_min_ghz=freq_min,
            freq_max_ghz=freq_max,
            load_avg=(load_1, load_5, load_15),
            temperature_c=temp_c,
            history=list(self.history),
        )
