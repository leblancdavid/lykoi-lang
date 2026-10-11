"""Dependency-free current resident memory, never peak RSS or a zero fallback."""
import ctypes
from ctypes import wintypes
import os
from pathlib import Path
import sys


def measure(pid=None):
    pid = os.getpid() if pid is None else pid
    if type(pid) is not int or pid <= 0:
        raise ValueError('INVALID_PID')
    result = dict(requested_pid=pid, measured_pid=None, observer_pid=os.getpid(),
                  resident_bytes=None, available=False, method=None, reason=None)
    try:
        if sys.platform == 'win32':
            class Counters(ctypes.Structure):
                _fields_ = [('cb', wintypes.DWORD), ('PageFaultCount', wintypes.DWORD)] + [
                    (name, ctypes.c_size_t) for name in ('PeakWorkingSetSize', 'WorkingSetSize',
                    'QuotaPeakPagedPoolUsage', 'QuotaPagedPoolUsage', 'QuotaPeakNonPagedPoolUsage',
                    'QuotaNonPagedPoolUsage', 'PagefileUsage', 'PeakPagefileUsage')]
            kernel = ctypes.WinDLL('kernel32', use_last_error=True)
            psapi = ctypes.WinDLL('psapi', use_last_error=True)
            kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            kernel.OpenProcess.restype = wintypes.HANDLE
            kernel.GetProcessId.argtypes = [wintypes.HANDLE]
            kernel.GetProcessId.restype = wintypes.DWORD
            kernel.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel.CloseHandle.restype = wintypes.BOOL
            psapi.GetProcessMemoryInfo.argtypes = [wintypes.HANDLE, ctypes.POINTER(Counters), wintypes.DWORD]
            psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
            handle = kernel.OpenProcess(0x0400 | 0x0010, False, pid)
            if not handle:
                raise ctypes.WinError(ctypes.get_last_error())
            try:
                actual_pid = kernel.GetProcessId(handle)
                counters = Counters()
                counters.cb = ctypes.sizeof(counters)
                if not psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                    raise ctypes.WinError(ctypes.get_last_error())
                resident = int(counters.WorkingSetSize)
            finally:
                kernel.CloseHandle(handle)
            method = 'Windows GetProcessMemoryInfo.WorkingSetSize'
        elif sys.platform.startswith('linux'):
            status = (Path('/proc')/str(pid)/'status').read_text()
            fields = dict(line.split(':', 1) for line in status.splitlines() if ':' in line)
            actual_pid = int(fields['Pid'])
            amount, unit = fields['VmRSS'].split()
            assert unit == 'kB'
            resident = int(amount)*1024
            method = 'Linux /proc/PID/status VmRSS'
        else:
            result['reason'] = 'UNSUPPORTED_PLATFORM:' + sys.platform
            return result
        assert actual_pid == pid, 'PROCESS_ATTRIBUTION'
        assert resident > 0, 'NONPOSITIVE_RESIDENT_MEASUREMENT'
        result.update(measured_pid=actual_pid, resident_bytes=resident, available=True, method=method)
    except (OSError, KeyError, ValueError, AssertionError) as exc:
        result['reason'] = type(exc).__name__ + ':' + str(exc)
    return result


def validate(value, pid, ceiling=None):
    assert value['requested_pid'] == pid, 'REQUESTED_PROCESS_MISMATCH'
    if not value['available']:
        assert value['resident_bytes'] is None and value['measured_pid'] is None and value['reason'], 'FABRICATED_MEASUREMENT'
        if ceiling is not None:
            raise RuntimeError('RSS_UNAVAILABLE:' + value['reason'])
        return None
    assert value['measured_pid'] == pid, 'MEASURED_PROCESS_MISMATCH'
    assert type(value['resident_bytes']) is int and value['resident_bytes'] > 0, 'INVALID_RESIDENT_BYTES'
    if ceiling is not None:
        assert value['resident_bytes'] <= ceiling, 'RSS_LIMIT'
    return value['resident_bytes']


def rss(pid):
    return validate(measure(pid), pid)
