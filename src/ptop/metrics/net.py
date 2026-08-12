"""Network interfaces and traffic metrics collector."""

import time
from collections import deque
from dataclasses import dataclass, field

import psutil


@dataclass
class NetInterfaceStats:
    name: str
    rx_bytes_sec: float
    tx_bytes_sec: float
    total_rx_bytes: int
    total_tx_bytes: int
    is_up: bool


@dataclass
class NetMetrics:
    total_rx_bytes_sec: float = 0.0
    total_tx_bytes_sec: float = 0.0
    total_rx_bytes: int = 0
    total_tx_bytes: int = 0
    interfaces: list[NetInterfaceStats] = field(default_factory=list)
    rx_history: list[float] = field(default_factory=list)
    tx_history: list[float] = field(default_factory=list)


class NetCollector:
    def __init__(self, history_len: int = 60):
        self.history_len = history_len
        self.rx_history: deque = deque(maxlen=history_len)
        self.tx_history: deque = deque(maxlen=history_len)
        self.last_net_io: dict[str, psutil._common.snetio] | None = None
        self.last_time: float | None = None

    def collect(self) -> NetMetrics:
        now = time.time()
        interfaces: list[NetInterfaceStats] = []
        total_rx_sec = 0.0
        total_tx_sec = 0.0
        total_rx_bytes = 0
        total_tx_bytes = 0

        try:
            net_io = psutil.net_io_counters(pernic=True)
            stats = psutil.net_if_stats()

            dt = (now - self.last_time) if self.last_time else 0.0

            for iface_name, io in net_io.items():
                if iface_name.startswith(("lo", "docker", "veth", "br-")):
                    continue  # Filter loopback and virtual bridges by default for cleaner UI

                is_up = stats[iface_name].isup if iface_name in stats else True
                total_rx_bytes += io.bytes_recv
                total_tx_bytes += io.bytes_sent

                rx_sec = 0.0
                tx_sec = 0.0

                if self.last_net_io and iface_name in self.last_net_io and dt > 0:
                    prev_io = self.last_net_io[iface_name]
                    rx_sec = max(0.0, (io.bytes_recv - prev_io.bytes_recv) / dt)
                    tx_sec = max(0.0, (io.bytes_sent - prev_io.bytes_sent) / dt)

                total_rx_sec += rx_sec
                total_tx_sec += tx_sec

                interfaces.append(
                    NetInterfaceStats(
                        name=iface_name,
                        rx_bytes_sec=rx_sec,
                        tx_bytes_sec=tx_sec,
                        total_rx_bytes=io.bytes_recv,
                        total_tx_bytes=io.bytes_sent,
                        is_up=is_up,
                    )
                )

            self.last_net_io = net_io
            self.last_time = now
        except Exception:
            pass

        self.rx_history.append(total_rx_sec)
        self.tx_history.append(total_tx_sec)

        return NetMetrics(
            total_rx_bytes_sec=total_rx_sec,
            total_tx_bytes_sec=total_tx_sec,
            total_rx_bytes=total_rx_bytes,
            total_tx_bytes=total_tx_bytes,
            interfaces=interfaces,
            rx_history=list(self.rx_history),
            tx_history=list(self.tx_history),
        )
