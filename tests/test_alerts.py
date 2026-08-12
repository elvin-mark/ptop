from ptop.alerts import AlertManager
from ptop.config import Config
from ptop.metrics.collector import SystemSnapshot
from ptop.metrics.cpu import CPUMetrics
from ptop.metrics.disk import DiskMetrics
from ptop.metrics.gpu import GPUMetrics
from ptop.metrics.memory import MemoryMetrics
from ptop.metrics.net import NetMetrics
from ptop.metrics.process import ProcessTree


def test_alert_manager_trigger():
    alert_mgr = AlertManager()
    cfg = Config(alert_cpu_percent=80.0)

    snap = SystemSnapshot(
        cpu=CPUMetrics(total_usage=95.0),
        memory=MemoryMetrics(ram_percent=50.0),
        disk=DiskMetrics(),
        net=NetMetrics(),
        gpu=GPUMetrics(),
        procs=ProcessTree(
            items=[],
            total_processes=0,
            running_count=0,
            sleeping_count=0,
            stopped_count=0,
        ),
        timestamp=1000.0,
    )

    alerts = alert_mgr.check(snap, cfg)
    assert len(alerts) == 1
    assert alerts[0].category == "CPU"
    assert alerts[0].severity == "CRITICAL"
