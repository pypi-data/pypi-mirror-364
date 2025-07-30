
import os
import sys


IS_WINDOWS = sys.platform == 'win32'


def get_cpu_count() -> int:

    if IS_WINDOWS:
        import psutil
        cpu = psutil.cpu_count(logical=False)
    else:
        import subprocess

        try:
            cmd = "lscpu -b -p=Core,Socket | grep -v '^#' | sort -u | wc -l"
            ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = ps.communicate()[0]
            cpu = int(output)
        except Exception:
            import multiprocessing
            cpu = multiprocessing.cpu_count() // 2

        try:
            cpu = min(cpu, os.sched_getaffinity(0))
        except Exception:
            pass

    return cpu
