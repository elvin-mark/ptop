"""Process metrics collector, tree builder, filtering, sorting, and signaling."""

import os
import time
from dataclasses import dataclass, field

import psutil


@dataclass
class ProcessItem:
    pid: int
    ppid: int
    name: str
    user: str
    cpu_percent: float
    mem_percent: float
    mem_rss_bytes: int
    status: str
    threads: int
    cmdline: str
    read_bytes_sec: float = 0.0
    write_bytes_sec: float = 0.0
    is_container: bool = False
    children: list["ProcessItem"] = field(default_factory=list)
    depth: int = 0


@dataclass
class ProcessTree:
    items: list[ProcessItem]
    total_processes: int
    running_count: int
    sleeping_count: int
    stopped_count: int


class ProcessCollector:
    def __init__(self):
        self.last_proc_io: dict[int, tuple[int, int, float]] = {}  # pid -> (read_bytes, write_bytes, timestamp)

    def _is_container_pid(self, pid: int) -> bool:
        if not os.path.exists(f"/proc/{pid}/cgroup"):
            return False
        try:
            with open(f"/proc/{pid}/cgroup") as f:
                content = f.read()
                return any(k in content for k in ["docker", "kubepods", "containerd", "podman"])
        except Exception:
            return False

    def collect(
        self,
        sort_by: str = "cpu",
        reverse: bool = True,
        filter_query: str = "",
        tree_mode: bool = False,
    ) -> ProcessTree:
        now = time.time()
        procs_raw: list[ProcessItem] = []
        running_cnt = 0
        sleeping_cnt = 0
        stopped_cnt = 0

        # Efficient batch sampling
        attrs = [
            "pid",
            "ppid",
            "name",
            "username",
            "cpu_percent",
            "memory_percent",
            "memory_info",
            "status",
            "num_threads",
            "cmdline",
        ]

        for proc in psutil.process_iter(attrs=attrs):
            try:
                pinfo = proc.info
                pid = pinfo["pid"]
                if pid <= 0:
                    continue

                status = pinfo["status"] or "unknown"
                stopped_statuses = {
                    getattr(psutil, "STATUS_STOPPED", "stopped"),
                    getattr(psutil, "STATUS_TRACING_STOP", "tracing_stop"),
                    getattr(psutil, "STATUS_TRACED_STOP", "traced_stop"),
                }
                if status == psutil.STATUS_RUNNING:
                    running_cnt += 1
                elif status == psutil.STATUS_SLEEPING:
                    sleeping_cnt += 1
                elif status in stopped_statuses:
                    stopped_cnt += 1

                cpu_pct = pinfo["cpu_percent"] or 0.0
                mem_pct = pinfo["memory_percent"] or 0.0
                mem_rss = pinfo["memory_info"].rss if pinfo["memory_info"] else 0
                threads = pinfo["num_threads"] or 1
                user = pinfo["username"] or "root"
                name = pinfo["name"] or f"pid_{pid}"
                cmdline = " ".join(pinfo["cmdline"]) if pinfo["cmdline"] else name
                ppid = pinfo["ppid"] or 0

                # Disk IO rate per process
                read_rate, write_rate = 0.0, 0.0
                try:
                    io = proc.io_counters()
                    if pid in self.last_proc_io:
                        prev_r, prev_w, prev_t = self.last_proc_io[pid]
                        dt = now - prev_t
                        if dt > 0:
                            read_rate = max(0.0, (io.read_bytes - prev_r) / dt)
                            write_rate = max(0.0, (io.write_bytes - prev_w) / dt)
                    self.last_proc_io[pid] = (io.read_bytes, io.write_bytes, now)
                except Exception:
                    pass

                is_container = self._is_container_pid(pid)

                item = ProcessItem(
                    pid=pid,
                    ppid=ppid,
                    name=name,
                    user=user,
                    cpu_percent=cpu_pct,
                    mem_percent=mem_pct,
                    mem_rss_bytes=mem_rss,
                    status=status,
                    threads=threads,
                    cmdline=cmdline,
                    read_bytes_sec=read_rate,
                    write_bytes_sec=write_rate,
                    is_container=is_container,
                )
                procs_raw.append(item)

            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Filter query
        if filter_query:
            q = filter_query.lower()
            procs_raw = [
                p
                for p in procs_raw
                if q in p.name.lower() or q in p.cmdline.lower() or q in p.user.lower() or q in str(p.pid)
            ]

        # Sorting key
        def get_sort_key(p: ProcessItem):
            if sort_by == "cpu":
                return p.cpu_percent
            elif sort_by == "mem":
                return p.mem_percent
            elif sort_by == "pid":
                return p.pid
            elif sort_by == "name":
                return p.name.lower()
            elif sort_by == "user":
                return p.user.lower()
            elif sort_by == "disk":
                return p.read_bytes_sec + p.write_bytes_sec
            return p.cpu_percent

        if tree_mode and not filter_query:
            # Build tree view
            pid_map: dict[int, ProcessItem] = {p.pid: p for p in procs_raw}
            roots: list[ProcessItem] = []

            for p in procs_raw:
                if p.ppid in pid_map and p.ppid != p.pid:
                    pid_map[p.ppid].children.append(p)
                else:
                    roots.append(p)

            # Sort roots and recursively flatten tree
            roots.sort(key=get_sort_key, reverse=reverse)
            flattened: list[ProcessItem] = []

            def flatten(node: ProcessItem, depth: int = 0):
                node.depth = depth
                flattened.append(node)
                node.children.sort(key=get_sort_key, reverse=reverse)
                for child in node.children:
                    flatten(child, depth + 1)

            for root in roots:
                flatten(root, depth=0)

            final_list = flattened
        else:
            procs_raw.sort(key=get_sort_key, reverse=reverse)
            final_list = procs_raw

        return ProcessTree(
            items=final_list,
            total_processes=len(procs_raw),
            running_count=running_cnt,
            sleeping_count=sleeping_cnt,
            stopped_count=stopped_cnt,
        )


def send_process_signal(pid: int, sig_num: int) -> tuple[bool, str]:
    """Sends a Unix signal (e.g. 9 for SIGKILL, 15 for SIGTERM) to a process."""
    try:
        os.kill(pid, sig_num)
        return True, f"Sent signal {sig_num} to PID {pid}"
    except Exception as e:
        return False, f"Failed to send signal to PID {pid}: {e}"


def get_process_details(pid: int) -> dict[str, str]:
    """Gets detailed inspect data for a process modal."""
    info: dict[str, str] = {}
    try:
        p = psutil.Process(pid)
        info["PID"] = str(p.pid)
        info["Name"] = p.name()
        info["Status"] = p.status()
        info["User"] = p.username()
        info["Created"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(p.create_time()))
        info["CPU %"] = f"{p.cpu_percent():.1f}%"
        info["Memory %"] = f"{p.memory_percent():.1f}%"
        info["RSS Bytes"] = f"{p.memory_info().rss / (1024 * 1024):.1f} MB"
        info["Threads"] = str(p.num_threads())
        info["CWD"] = p.cwd() if hasattr(p, "cwd") else "N/A"
        info["Cmdline"] = " ".join(p.cmdline())

        try:
            files = [f.path for f in p.open_files()[:10]]
            info["Open Files"] = "\n".join(files) if files else "None"
        except Exception:
            info["Open Files"] = "Permission Denied"

        try:
            conns = [f"{c.laddr} -> {c.raddr} ({c.status})" for c in p.net_connections()[:10]]
            info["Network Connections"] = "\n".join(conns) if conns else "None"
        except Exception:
            info["Network Connections"] = "Permission Denied"

    except psutil.NoSuchProcess:
        info["Error"] = f"Process {pid} no longer exists."
    except Exception as e:
        info["Error"] = f"Error inspecting process {pid}: {e}"

    return info
