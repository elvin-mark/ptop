from ptop.metrics.cpu import CPUCollector
from ptop.metrics.disk import DiskCollector
from ptop.metrics.gpu import GPUCollector
from ptop.metrics.memory import MemoryCollector
from ptop.metrics.net import NetCollector
from ptop.metrics.process import ProcessCollector


def test_cpu_collector():
    coll = CPUCollector(history_len=10)
    metrics = coll.collect()
    assert metrics.logical_cores >= 1
    assert 0.0 <= metrics.total_usage <= 100.0
    assert len(metrics.history) == 1


def test_memory_collector():
    coll = MemoryCollector(history_len=10)
    metrics = coll.collect()
    assert metrics.ram_total_bytes > 0
    assert 0.0 <= metrics.ram_percent <= 100.0


def test_disk_collector():
    coll = DiskCollector(history_len=10)
    metrics = coll.collect()
    assert isinstance(metrics.partitions, list)


def test_net_collector():
    coll = NetCollector(history_len=10)
    metrics = coll.collect()
    assert metrics.total_rx_bytes >= 0


def test_gpu_collector():
    coll = GPUCollector(history_len=10)
    metrics = coll.collect()
    assert isinstance(metrics.available, bool)


def test_process_collector():
    coll = ProcessCollector()
    tree = coll.collect(sort_by="cpu", reverse=True)
    assert tree.total_processes > 0
    assert len(tree.items) > 0


def test_process_collector_tree_and_folding():
    coll = ProcessCollector()
    tree = coll.collect(sort_by="cpu", reverse=True, tree_mode=True)
    assert tree.total_processes > 0
    assert len(tree.items) > 0

    # Find a process that has children
    parent_with_children = next((p for p in tree.items if p.child_count > 0), None)
    if parent_with_children:
        # Test collapsing that PID
        folded_tree = coll.collect(
            sort_by="cpu",
            reverse=True,
            tree_mode=True,
            collapsed_pids={parent_with_children.pid},
        )
        assert len(folded_tree.items) < len(tree.items)
        folded_item = next((p for p in folded_tree.items if p.pid == parent_with_children.pid), None)
        assert folded_item is not None
        assert folded_item.is_collapsed is True
