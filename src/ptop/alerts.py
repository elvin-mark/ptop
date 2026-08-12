"""Alert system for monitoring thresholds and health events."""

import time
from dataclasses import dataclass

from ptop.config import Config
from ptop.metrics.collector import SystemSnapshot


@dataclass
class Alert:
    timestamp: float
    time_str: str
    severity: str  # "INFO", "WARNING", "CRITICAL"
    category: str  # "CPU", "MEM", "DISK", "TEMP"
    message: str


class AlertManager:
    def __init__(self, max_alerts: int = 50):
        self.max_alerts = max_alerts
        self.alerts: list[Alert] = []
        self.last_triggered: dict = {}  # category -> timestamp of last alert to avoid spamming

    def check(self, snapshot: SystemSnapshot, config: Config) -> list[Alert]:
        now = time.time()
        time_str = time.strftime("%H:%M:%S", time.localtime(now))
        cooldown = 10.0  # seconds between duplicate alerts

        # 1. CPU Usage
        if snapshot.cpu.total_usage >= config.alert_cpu_percent:
            if now - self.last_triggered.get("CPU", 0) > cooldown:
                self.last_triggered["CPU"] = now
                self.alerts.insert(
                    0,
                    Alert(
                        timestamp=now,
                        time_str=time_str,
                        severity="WARNING" if snapshot.cpu.total_usage < 95 else "CRITICAL",
                        category="CPU",
                        message=f"High CPU utilization: {snapshot.cpu.total_usage:.1f}%",
                    ),
                )

        # 2. CPU Temperature
        if (
            snapshot.cpu.temperature_c and snapshot.cpu.temperature_c >= config.alert_temp_celsius
        ) and now - self.last_triggered.get("TEMP", 0) > cooldown:
            self.last_triggered["TEMP"] = now
            self.alerts.insert(
                0,
                Alert(
                    timestamp=now,
                    time_str=time_str,
                    severity="CRITICAL",
                    category="TEMP",
                    message=f"High CPU temperature: {snapshot.cpu.temperature_c:.1f}°C",
                ),
            )

        # 3. RAM Memory Pressure
        if snapshot.memory.ram_percent >= config.alert_mem_percent:
            if now - self.last_triggered.get("MEM", 0) > cooldown:
                self.last_triggered["MEM"] = now
                self.alerts.insert(
                    0,
                    Alert(
                        timestamp=now,
                        time_str=time_str,
                        severity="WARNING" if snapshot.memory.ram_percent < 95 else "CRITICAL",
                        category="MEM",
                        message=f"High RAM usage: {snapshot.memory.ram_percent:.1f}% ({snapshot.memory.ram_used_bytes / (1024**3):.1f} GB)",
                    ),
                )

        # 4. Disk Partition Space
        for part in snapshot.disk.partitions:
            if part.percent >= config.alert_disk_percent:
                key = f"DISK_{part.mountpoint}"
                if now - self.last_triggered.get(key, 0) > cooldown:
                    self.last_triggered[key] = now
                    self.alerts.insert(
                        0,
                        Alert(
                            timestamp=now,
                            time_str=time_str,
                            severity="WARNING" if part.percent < 95 else "CRITICAL",
                            category="DISK",
                            message=f"Low disk space on {part.mountpoint}: {part.percent:.1f}% used",
                        ),
                    )

        # Trim list
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[: self.max_alerts]

        return self.alerts

    def clear(self) -> None:
        self.alerts.clear()
