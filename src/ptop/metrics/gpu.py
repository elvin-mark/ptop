"""GPU metrics collector supporting NVIDIA (pynvml / nvidia-smi) and fallback hardware stats."""

import shutil
import subprocess
from collections import deque
from dataclasses import dataclass, field


@dataclass
class GPUSpec:
    name: str = "N/A"
    driver_version: str = "N/A"
    usage_percent: float = 0.0
    vram_used_bytes: int = 0
    vram_total_bytes: int = 0
    vram_percent: float = 0.0
    temperature_c: float | None = None
    power_watts: float | None = None
    history: list[float] = field(default_factory=list)


@dataclass
class GPUMetrics:
    available: bool = False
    gpus: list[GPUSpec] = field(default_factory=list)


class GPUCollector:
    def __init__(self, history_len: int = 60):
        self.history_len = history_len
        self.histories: dict = {}
        self.nvml_initialized = False
        self._init_nvml()

    def _init_nvml(self) -> None:
        try:
            import pynvml

            pynvml.nvmlInit()
            self.nvml_initialized = True
        except Exception:
            self.nvml_initialized = False

    def collect(self) -> GPUMetrics:
        if self.nvml_initialized:
            try:
                import pynvml

                count = pynvml.nvmlDeviceGetCount()
                gpus: list[GPUSpec] = []
                for i in range(count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle)
                    if isinstance(name, bytes):
                        name = name.decode("utf-8")

                    try:
                        util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                    except Exception:
                        util = 0.0

                    try:
                        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        vram_used = mem.used
                        vram_total = mem.total
                        vram_percent = (mem.used / mem.total * 100.0) if mem.total else 0.0
                    except Exception:
                        vram_used, vram_total, vram_percent = 0, 0, 0.0

                    try:
                        temp = float(pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU))
                    except Exception:
                        temp = None

                    try:
                        power = float(pynvml.nvmlDeviceGetPowerUsage(handle)) / 1000.0
                    except Exception:
                        power = None

                    if i not in self.histories:
                        self.histories[i] = deque(maxlen=self.history_len)
                    self.histories[i].append(util)

                    gpus.append(
                        GPUSpec(
                            name=name,
                            driver_version="",
                            usage_percent=float(util),
                            vram_used_bytes=vram_used,
                            vram_total_bytes=vram_total,
                            vram_percent=vram_percent,
                            temperature_c=temp,
                            power_watts=power,
                            history=list(self.histories[i]),
                        )
                    )
                return GPUMetrics(available=len(gpus) > 0, gpus=gpus)
            except Exception:
                pass

        # Fallback to nvidia-smi if available
        if shutil.which("nvidia-smi"):
            try:
                cmd = [
                    "nvidia-smi",
                    "--query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw",
                    "--format=csv,noheader,nounits",
                ]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=1.5)
                if res.returncode == 0 and res.stdout.strip():
                    gpus = []
                    lines = res.stdout.strip().splitlines()
                    for idx, line in enumerate(lines):
                        parts = [p.strip() for p in line.split(",")]
                        if len(parts) >= 5:
                            name = parts[0]
                            util = float(parts[1]) if parts[1].replace(".", "").isdigit() else 0.0
                            v_used = int(parts[2]) * 1024 * 1024 if parts[2].isdigit() else 0
                            v_tot = int(parts[3]) * 1024 * 1024 if parts[3].isdigit() else 0
                            v_pct = (v_used / v_tot * 100.0) if v_tot > 0 else 0.0
                            temp = float(parts[4]) if parts[4].replace(".", "").isdigit() else None
                            power = float(parts[5]) if len(parts) > 5 and parts[5].replace(".", "").isdigit() else None

                            if idx not in self.histories:
                                self.histories[idx] = deque(maxlen=self.history_len)
                            self.histories[idx].append(util)

                            gpus.append(
                                GPUSpec(
                                    name=name,
                                    usage_percent=util,
                                    vram_used_bytes=v_used,
                                    vram_total_bytes=v_tot,
                                    vram_percent=v_pct,
                                    temperature_c=temp,
                                    power_watts=power,
                                    history=list(self.histories[idx]),
                                )
                            )
                    if gpus:
                        return GPUMetrics(available=True, gpus=gpus)
            except Exception:
                pass

        return GPUMetrics(available=False, gpus=[])
