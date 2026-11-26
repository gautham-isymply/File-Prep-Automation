"""CCB Excel display contracts survive row cleanup and column removal."""
from datetime import date
from hashlib import sha256

import pytest
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

from factoryprep.config import ConfigError, load_profile
from factoryprep.engine import run


def test_ccb_formats_and_colours_follow_retained_source_rows(workbook_factory, tmp_path):
    source = workbook_factory('coloured_ccb',
        ['Notes', 'Date', 'Dept', 'Reg Hr', 'OT1.5 Hr', 'OT2 Hr', 'Total Hr'],
        [['remove', '03/14/2026', '3600171000', '8.125', '2', '1', '11.125'],
         ['Grand Total', None, None, 8.125, 2, 1, 11.125],
         [None, None, None, None, None, None, None],
         ['remove', '03/14/2026', '3600171001', '7', '0', '0', '7']],
        preamble=[['Source title']])
    wb = load_workbook(source)
    wb.active['B3'].fill = PatternFill('solid', fgColor='FF9999FF')
    wb.active['B6'].fill = PatternFill('solid', fgColor='FFFFFF00')
    wb.save(source)
    wb.close()
    before = sha256(source.read_bytes()).hexdigest()
    target = tmp_path / 'prepared.xlsx'
    report = run('ccb', source, target, week_ending=date(2026, 3, 14))
    assert report.status == 'PREPARED', report.as_dict()
    assert sha256(source.read_bytes()).hexdigest() == before
    wb = load_workbook(target)
    sh = wb.active
    assert sh.max_row == 3
    assert sh.auto_filter.ref == 'A1:F3'
    assert sh['A2'].fill.fgColor.rgb == 'FF9999FF'
    assert sh['A3'].fill.fgColor.rgb == 'FFFFFF00'
    assert sh['A2'].number_format == 'mm/dd/yy'
    for row in sh.iter_rows(min_row=2, min_col=3, max_col=6):
        assert all(c.data_type == 'n' and c.number_format == '0.00' for c in row)
    assert sh['C2'].value == 8.125  # Display precision never rounds stored hours.
    assert sh['F2'].value == 11.125
    wb.close()


@pytest.mark.parametrize('setting,value', [
    ('number_formats', []), ('number_formats', {'Sum of Reg Hr': 2}),
    ('preserve_fill_columns', 'Row Labels'), ('auto_filter', 'yes'),
])
def test_output_format_config_is_validated(tmp_path, setting, value):
    import yaml

    profile = load_profile('ccb')
    profile['output'][setting] = value
    (tmp_path / 'ccb.yaml').write_text(yaml.safe_dump(profile), encoding='utf-8')
    with pytest.raises(ConfigError):
        load_profile('ccb', tmp_path)
