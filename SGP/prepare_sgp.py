#!/usr/bin/env python3
"""Automate SGP Factory Insights attendance file preparation on Windows.

Requirements:
    - Windows with Microsoft Excel installed
    - Python 3.8 or newer (no third-party Python packages)

Usage:
    python prepare_sgp.py "Attendance 2 - 8 Nov 2026.xls"
    python prepare_sgp.py "Attendance 2 - 8 Nov 2026.xls" -o "SGP_ready.xlsx"

Processing:
    - Opens the first worksheet of the .xls attachment in Excel
    - Applies Excel DATE number format 'yyyymmdd' (keeps real date values)
    - Removes SCHEDULED START TIME and SCHEDULED END TIME when present
    - Saves a new .xlsx file in an outputs folder, using the original filename
    - Creates the outputs folder automatically without modifying the source
    - Preserves all other cell values, worksheet styles, and columns
"""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


EXCEL_SCRIPT = r'''
param(
    [Parameter(Mandatory = $true)][string]$InputPath,
    [Parameter(Mandatory = $true)][string]$OutputPath
)
$ErrorActionPreference = 'Stop'
$excel = $null
$workbook = $null
$sheet = $null
try {
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    $excel.DisplayAlerts = $false
    $excel.AskToUpdateLinks = $false

    $workbook = $excel.Workbooks.Open($InputPath, 0, $true)
    $sheet = $workbook.Worksheets.Item(1)

    # Find headers by name, rather than hard-coding Excel column letters.
    $lastCol = [int]$sheet.Cells.Item(1, $sheet.Columns.Count).End(-4159).Column
    $lastRow = [int]$sheet.Cells.Item($sheet.Rows.Count, 1).End(-4162).Row

    $dateIndex = 0
    $drop = @()
    $removedNames = @()
    for ($col = 1; $col -le $lastCol; $col++) {
        $rawName = [string]$sheet.Cells.Item(1, $col).Value2
        $name = ($rawName -replace '\s+', ' ').Trim().ToUpperInvariant()
        if ($name -eq 'DATE') {
            if ($dateIndex -ne 0) { throw 'Multiple DATE columns detected.' }
            $dateIndex = $col
        }
        if ($name -eq 'SCHEDULED START TIME' -or
            $name -eq 'SCHEDULED END TIME') {
            $drop += $col
            $removedNames += $rawName
        }
    }
    if ($dateIndex -eq 0) { throw 'DATE column was not found in row 1.' }
    if ($lastRow -le 1) { throw 'The attendance worksheet has no data rows.' }

    # This is the equivalent of Format Cells > Custom > yyyymmdd.
    # Excel's underlying date values are NOT converted to strings.
    $dateRange = $sheet.Range(
        $sheet.Cells.Item(2, $dateIndex),
        $sheet.Cells.Item($lastRow, $dateIndex)
    )
    $dateRange.NumberFormat = 'yyyymmdd'

    # Right-to-left deletion prevents column position shifts.
    foreach ($col in ($drop | Sort-Object -Descending)) {
        $sheet.Columns.Item([int]$col).Delete() | Out-Null
    }

    # Excel FileFormat 51 is Office Open XML (.xlsx).
    $workbook.SaveAs($OutputPath, 51)
    Write-Output ('Attendance rows:  ' + ($lastRow - 1))
    Write-Output ('Columns:          ' + $lastCol + ' -> ' + ($lastCol - $drop.Count))
    Write-Output ('DATE display:     YYYYMMDD')
    if ($removedNames.Count -gt 0) {
        Write-Output ('Removed:          ' + ($removedNames -join ', '))
    } else {
        Write-Output 'Removed:          none (scheduled-time columns not present)'
    }
    Write-Output ('Prepared file:    ' + $OutputPath)
}
finally {
    if ($workbook -ne $null) {
        try { $workbook.Close($false) } catch { }
    }
    if ($excel -ne $null) {
        try { $excel.Quit() } catch { }
    }
    if ($sheet -ne $null) {
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($sheet)
    }
    if ($workbook -ne $null) {
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($workbook)
    }
    if ($excel -ne $null) {
        [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel)
    }
}
'''


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Prepare an SGP attendance .xls attachment as Factory Insights .xlsx"
    )
    parser.add_argument("input", type=Path, help="Downloaded attendance Excel .xls")
    parser.add_argument(
        "--output", "-o", type=str,
        help="Optional output .xlsx filename (always saved in the outputs folder)",
    )
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if args.output:
        output_name = Path(args.output)
        if output_name.name != args.output or output_name.is_absolute():
            parser.error("--output must be a filename, not a folder path")
    else:
        output_name = source.with_suffix(".xlsx").name
    target = (source.parent / "outputs" / output_name).resolve()

    if not source.is_file():
        parser.error(f"Input file not found: {source}")
    if source.suffix.lower() not in (".xls", ".xlsx"):
        parser.error("Input must be an Excel .xls or .xlsx file")
    if target.suffix.lower() != ".xlsx":
        parser.error("Output file must have the .xlsx extension")
    if source == target:
        parser.error("Output must not overwrite the input file")
    if sys.platform != "win32":
        parser.error("This script runs on Windows with Microsoft Excel installed")

    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if not powershell:
        parser.error("Windows PowerShell was not found")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="sgp_prepare_") as temp_dir:
        path = Path(temp_dir) / "prepare_excel.ps1"
        path.write_text(EXCEL_SCRIPT, encoding="utf-8-sig")
        command = [powershell, "-NoProfile", "-NonInteractive", "-ExecutionPolicy",
                   "Bypass", "-File", str(path), "-InputPath", str(source),
                   "-OutputPath", str(target)]
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as exc:
            print(f"SGP preparation failed (exit code {exc.returncode}).", file=sys.stderr)
            return exc.returncode or 1
    if not target.is_file():
        print("Excel did not create the expected output file.", file=sys.stderr)
        return 1
    print("Original file:    unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
