import hashlib

import pytest
import yaml
from openpyxl import Workbook


@pytest.fixture
def refresh_evidence(tmp_path):
    def create(source):
        path = tmp_path / f"{source.stem}-refresh.yaml"
        path.write_text(yaml.safe_dump({"source_evidence": {
            "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "refreshed_at": "2026-03-15T09:00:00-05:00", "approved_by": "synthetic owner",
        }}), encoding="utf-8")
        return path
    return create


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
