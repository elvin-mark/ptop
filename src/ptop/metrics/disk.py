"""Disk space and I/O metrics collector."""

import time
from collections import deque
from dataclasses import dataclass, field

import psutil


@dataclass
class PartitionInfo:
    device: str
    mountpoint: str
    fstype: str
    total_bytes: int
    used_bytes: int
    free_bytes: int
    percent: float


@dataclass
class DiskMetrics:
    partitions: list[PartitionInfo] = field(default_factory=list)
    read_bytes_sec: float = 0.0
    write_bytes_sec: float = 0.0
    read_count_sec: float = 0.0
    write_count_sec: float = 0.0
    read_history: list[float] = field(default_factory=list)
    write_history: list[float] = field(default_factory=list)


IGNORED_FSTYPES = {
    "",
    "squashfs",
    "iso9660",
    "proc",
    "sysfs",
    "devtmpfs",
    "devpts",
    "cgroup",
    "cgroup2",
    "pstore",
    "bpf",
    "configfs",
    "debugfs",
    "hugetlbfs",
    "mqueue",
    "tracefs",
    "securityfs",
    "autofs",
    "fusectl",
    "ramfs",
}


class DiskCollector:
    def __init__(self, history_len: int = 60):
        self.history_len = history_len
        self.read_history: deque = deque(maxlen=history_len)
        self.write_history: deque = deque(maxlen=history_len)
        self.last_io: tuple | None = None
        self.last_time: float | None = None

    def collect(self) -> DiskMetrics:
        partitions_info: list[PartitionInfo] = []
        seen_mounts = set()

        try:
            parts = psutil.disk_partitions(all=False)
            if not any(p.mountpoint == "/" for p in parts):
                parts = psutil.disk_partitions(all=True)

            for part in parts:
                if part.fstype in IGNORED_FSTYPES or part.mountpoint in seen_mounts:
                    continue
                if part.mountpoint.startswith(("/proc", "/sys", "/dev", "/run")):
                    continue

                try:
                    usage = psutil.disk_usage(part.mountpoint)
                    if usage.total == 0:
                        continue
                    seen_mounts.add(part.mountpoint)
                    partitions_info.append(
                        PartitionInfo(
                            device=part.device,
                            mountpoint=part.mountpoint,
                            fstype=part.fstype,
                            total_bytes=usage.total,
                            used_bytes=usage.used,
                            free_bytes=usage.free,
                            percent=usage.percent,
                        )
                    )
                except (PermissionError, FileNotFoundError, OSError):
                    continue
        except Exception:
            pass

        # Sort partitions so '/' is first, then by total space descending
        partitions_info.sort(key=lambda p: (0 if p.mountpoint == "/" else 1, -p.total_bytes))

        # Disk I/O rates
        now = time.time()
        read_rate = 0.0
        write_rate = 0.0
        read_ops_rate = 0.0
        write_ops_rate = 0.0

        try:
            io_counters = psutil.disk_io_counters()
            if io_counters and self.last_io and self.last_time:
                dt = now - self.last_time
                if dt > 0:
                    read_rate = max(0.0, (io_counters.read_bytes - self.last_io.read_bytes) / dt)
                    write_rate = max(0.0, (io_counters.write_bytes - self.last_io.write_bytes) / dt)
                    read_ops_rate = max(0.0, (io_counters.read_count - self.last_io.read_count) / dt)
                    write_ops_rate = max(0.0, (io_counters.write_count - self.last_io.write_count) / dt)

            if io_counters:
                self.last_io = io_counters
                self.last_time = now
        except Exception:
            pass

        self.read_history.append(read_rate)
        self.write_history.append(write_rate)

        return DiskMetrics(
            partitions=partitions_info,
            read_bytes_sec=read_rate,
            write_bytes_sec=write_rate,
            read_count_sec=read_ops_rate,
            write_count_sec=write_ops_rate,
            read_history=list(self.read_history),
            write_history=list(self.write_history),
        )
