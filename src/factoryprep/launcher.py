"""Shared console entry point, including Windows Explorer file drops."""
from __future__ import annotations

import ctypes
import os
import sys
from pathlib import Path

from .cli import app


def _owns_console() -> bool:
    """Explorer creates a console; shells already have other attached processes."""
    if sys.platform != "win32" or not getattr(sys, "frozen", False):
        return False
    processes = (ctypes.c_ulong * 16)()
    count = ctypes.windll.kernel32.GetConsoleProcessList(processes, len(processes))
    if count == 1:
        return True
    # A one-file build has a waiting bootloader parent attached to the same console.
    return (count == 2 and os.getppid() in processes[:count] and _parent_is_bootloader())


def _parent_is_bootloader() -> bool:
    from ctypes import wintypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    kernel.OpenProcess.restype = wintypes.HANDLE
    kernel.QueryFullProcessImageNameW.argtypes = [
        wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD),
    ]
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    handle = kernel.OpenProcess(0x1000, False, os.getppid())
    if not handle:
        return False
    try:
        name = ctypes.create_unicode_buffer(32768)
        size = wintypes.DWORD(len(name))
        return bool(kernel.QueryFullProcessImageNameW(handle, 0, name, ctypes.byref(size))
                    and Path(name.value) == Path(sys.executable))
    finally:
        kernel.CloseHandle(handle)


def main() -> None:
    args = sys.argv[1:]
    # Explorer supplies bare file paths. Commands/options retain normal Typer parsing.
    if args and (Path(args[0]).is_file() or Path(args[0]).suffix.lower() in {
        ".xlsx", ".xlsm", ".csv", ".tsv", ".xls",
    }):
        args = ["drop", *args]
    pause = _owns_console()
    try:
        app(args=args or ["--help"], prog_name="factoryprep")
    finally:
        if pause:
            try:
                input("\nPress Enter to close...")
            except (EOFError, OSError):
                pass
