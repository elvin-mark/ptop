"""Combined async background metrics collector."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from ptop.metrics.cpu import CPUCollector, CPUMetrics
from ptop.metrics.disk import DiskCollector, DiskMetrics
from ptop.metrics.gpu import GPUCollector, GPUMetrics
from ptop.metrics.memory import MemoryCollector, MemoryMetrics
from ptop.metrics.net import NetCollector, NetMetrics
from ptop.metrics.process import ProcessCollector, ProcessTree


@dataclass
class SystemSnapshot:
    cpu: CPUMetrics
    memory: MemoryMetrics
    disk: DiskMetrics
    net: NetMetrics
    gpu: GPUMetrics
    procs: ProcessTree
    timestamp: float


class MetricsCollector:
    def __init__(self, history_len: int = 60):
        self.cpu_coll = CPUCollector(history_len)
        self.mem_coll = MemoryCollector(history_len)
        self.disk_coll = DiskCollector(history_len)
        self.net_coll = NetCollector(history_len)
        self.gpu_coll = GPUCollector(history_len)
        self.proc_coll = ProcessCollector()
        self.executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="ptop_collector")

    async def collect_all(
        self,
        sort_by: str = "cpu",
        reverse: bool = True,
        filter_query: str = "",
        tree_mode: bool = False,
    ) -> SystemSnapshot:
        loop = asyncio.get_running_loop()

        # Gather non-blocking metrics in threadpool executor
        cpu_fut = loop.run_in_executor(self.executor, self.cpu_coll.collect)
        mem_fut = loop.run_in_executor(self.executor, self.mem_coll.collect)
        disk_fut = loop.run_in_executor(self.executor, self.disk_coll.collect)
        net_fut = loop.run_in_executor(self.executor, self.net_coll.collect)
        gpu_fut = loop.run_in_executor(self.executor, self.gpu_coll.collect)
        proc_fut = loop.run_in_executor(
            self.executor,
            self.proc_coll.collect,
            sort_by,
            reverse,
            filter_query,
            tree_mode,
        )

        cpu, memory, disk, net, gpu, procs = await asyncio.gather(
            cpu_fut, mem_fut, disk_fut, net_fut, gpu_fut, proc_fut
        )

        import time

        return SystemSnapshot(
            cpu=cpu,
            memory=memory,
            disk=disk,
            net=net,
            gpu=gpu,
            procs=procs,
            timestamp=time.time(),
        )

    def close(self):
        self.executor.shutdown(wait=False)
