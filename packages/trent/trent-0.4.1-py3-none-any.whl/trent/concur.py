import concurrent.futures as conc
import psutil


import multiprocessing


def cpu_count() -> int:
    try:
        import psutil
        res = psutil.cpu_count()
        assert res
        return res
    except (ImportError, NotImplementedError):
        pass

    try:
        import multiprocessing
        return multiprocessing.cpu_count()
    except (ImportError, NotImplementedError):
        pass
    return 8


CPU_COUNT = cpu_count()
TRENT_THREADPOOL = conc.ThreadPoolExecutor(CPU_COUNT * 2, 'trent')