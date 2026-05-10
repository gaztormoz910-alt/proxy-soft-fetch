import os
import ctypes

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]

    def __init__(self):
        self.dwLength = ctypes.sizeof(self)
        super(MEMORYSTATUSEX, self).__init__()

def get_hardware_limits():
    cores = os.cpu_count() or 4
    ram_gb = 4
    try:
        if os.name == 'nt':
            stat = MEMORYSTATUSEX()
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
            ram_gb = stat.ullTotalPhys / (1024 ** 3)
    except:
        pass
    
    # Calculate recommended max threads
    # Base: 100 per core, plus 50 per GB of RAM
    max_threads = int((cores * 150) + (ram_gb * 100))
    # Cap it at 5000 to avoid Windows socket exhaustion (WSAENOBUFS)
    max_threads = min(max_threads, 5000)
    # Floor it at 500
    max_threads = max(max_threads, 500)
    
    return {
        'cores': cores,
        'ram_gb': round(ram_gb, 1),
        'max_threads': max_threads
    }

print(get_hardware_limits())
