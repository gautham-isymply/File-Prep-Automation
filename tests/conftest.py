from pathlib import Path
import pytest
from openpyxl import Workbook


@pytest.fixture
def workbook_factory(tmp_path):
    def create(name, headers, rows, sheet='Sheet1', preamble=None):
        path = tmp_path / f'{name}.xlsx'
        wb = Workbook()
        sh = wb.active
        sh.title = sheet
        if preamble:
            for row in preamble:
                sh.append(row)
        sh.append(headers)
        for row in rows:
            sh.append(row)
        wb.save(path)
        return path
    return create
