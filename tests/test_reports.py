from ptop.metrics.collector import SystemSnapshot
from ptop.metrics.cpu import CPUMetrics
from ptop.metrics.disk import DiskMetrics
from ptop.metrics.gpu import GPUMetrics
from ptop.metrics.memory import MemoryMetrics
from ptop.metrics.net import NetMetrics
from ptop.metrics.process import ProcessTree
from ptop.reports import export_snapshot_report


def test_export_snapshot_report(tmp_path):
    snap = SystemSnapshot(
        cpu=CPUMetrics(total_usage=50.0, logical_cores=8, model="Test CPU"),
        memory=MemoryMetrics(ram_percent=60.0, ram_used_bytes=8 * 1024**3, ram_total_bytes=16 * 1024**3),
        disk=DiskMetrics(),
        net=NetMetrics(),
        gpu=GPUMetrics(),
        procs=ProcessTree(items=[], total_processes=0, running_count=0, sleeping_count=0, stopped_count=0),
        timestamp=1000.0,
    )

    path_md = export_snapshot_report(snap, fmt="markdown")
    assert path_md.exists()
    assert path_md.suffix == ".md"

    path_json = export_snapshot_report(snap, fmt="json")
    assert path_json.exists()
    assert path_json.suffix == ".json"
