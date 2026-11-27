from datetime import date

import pytest
from openpyxl import load_workbook

from factoryprep.config import available_profiles
from factoryprep.engine import run
from factoryprep.transform import parse_date


def output_rows(path):
    wb = load_workbook(path, data_only=True)
    sheet = wb.active
    rows = list(sheet.values)
    wb.close()
    return rows


def test_inventory():
    assert set(available_profiles()) == {
        'sgp','gbr','cbg_core','cbg_starline','ccb','reno','jz',
        'dayforce_ccb','dayforce_non_ccb','taiwan'
    }


def test_sgp_removes_scheduled_fields_and_reformats_dates(workbook_factory, tmp_path):
    src = workbook_factory('sgp', ['DAYFORCEUC1','DATE','NORM','OT',
        'SCHEDULED START TIME', 'SCHEDULED END TIME'],
        [['1000', 20260504, 8, 1, '08:00', '17:00']])
    target = tmp_path / 'sgp_clean.xlsx'
    result = run('sgp', src, target, week_ending=date(2026, 5, 9))
    assert result.status == 'PREPARED', result.as_dict()
    rows = output_rows(target)
    assert rows[0] == ('DAYFORCEUC1','DATE','NORM','OT')
    assert rows[1][1].date() == date(2026, 5, 4)
    assert result.diagnostics['filtered_reconciliation_metrics']['paid_hours_selected_dayforceuc1']['total'] == 8


def test_sgp_allows_blank_norm_and_ot(workbook_factory, tmp_path):
    src = workbook_factory('sgp', ['DAYFORCEUC1','DATE','NORM','OT',
        'SCHEDULED START TIME', 'SCHEDULED END TIME'],
        [['1000', 20260504, None, None, '08:00', '17:00'],
         ['1000', 20260505, 8, None, '08:00', '17:00']])
    target = tmp_path / 'sgp_clean.xlsx'
    result = run('sgp', src, target, week_ending=date(2026, 5, 9))
    assert result.status == 'PREPARED', result.as_dict()
    rows = output_rows(target)
    assert rows[0] == ('DAYFORCEUC1','DATE','NORM','OT')
    assert rows[1][2] is None
    assert rows[1][3] is None
    assert rows[2][2] == 8
    assert rows[2][3] is None
    assert result.diagnostics['filtered_reconciliation_metrics']['paid_hours_selected_dayforceuc1']['total'] == 8


def test_gbr_converts_time_fractions_but_preserves_decimal_hours(workbook_factory, tmp_path):
    src = workbook_factory('gbr', ['DATEIN','DATEOUT','REGHOURS','O1HOURS','O2HOURS','DEPARTMENT','JOBCODEDESC'],
        [['02/03/2026','02/03/2026',0.5,0.125,0,'1000','WORK'],
         ['03/03/2026','03/03/2026',6,0,0,'1000','PTO']])
    target = tmp_path / 'gbr_clean.xlsx'
    wb = load_workbook(src)
    for row in (2, 3):
        if row == 2:
            for col in (3, 4, 5):
                wb.active.cell(row, col).number_format = '[h]:mm'
    wb.save(src)
    wb.close()
    report = run('gbr', src, target, week_ending=date(2026, 3, 7))
    assert report.status == 'PREPARED', report.as_dict()
    rows = output_rows(target)
    assert rows[1][2:5] == (12,3,0)
    assert rows[2][2] == 6
    assert report.diagnostics['filtered_reconciliation_metrics']['paid_hours_filtered']['total'] == 12


def test_cbg_core_preamble_and_total_removed(workbook_factory, tmp_path):
    src = workbook_factory('core', ['Pay Rate','Pay Code','Hours/Units'],
        [['$12.50','REG',8],['Total','',8]], preamble=[['A report'],['Extra headings']])
    target = tmp_path/'core_clean.xlsx'
    result = run('cbg_core', src, target)
    assert result.status == 'PREPARED', result.as_dict()
    assert result.rows_out == 1
    assert output_rows(target)[1][0] == 12.5
    assert load_workbook(target).active.title == 'Core'


def test_cbg_starline_removes_shift(workbook_factory,tmp_path):
    src = workbook_factory('ssi', ['W/E Date', 'Shift', 'BRD', 'CHARGECODE', 'Straight Hrs', 'Overtime Hrs'],
        [['03/14/2026','DAY','$1,234.00','1000',8,2]], preamble=[['Invoice report']])
    target = tmp_path/'starline.xlsx'
    report = run('cbg_starline',src,target)
    assert report.status == 'PREPARED', report.as_dict()
    assert 'Shift' not in output_rows(target)[0]
    assert output_rows(target)[1][1] == 1234


def test_ccb_manual_fix_is_not_automatic(workbook_factory,tmp_path):
    src = workbook_factory('ccb',['Row Labels','Plant','Dept','Sum of Reg Hr','Sum of OT1.5 Hr',
       'Sum of OT2 Hr','Sum of Total Hr','Notes'],
       [['01/05/2026','3617','3600171000',65.8,5,0,80.8,'please review']])
    target = tmp_path/'ccb_prepared.xlsx'
    report = run('ccb',src,target)
    assert report.status == 'PREPARED', report.as_dict()
    assert any(i.code == 'MANUAL_REVIEW_REQUIRED' for i in report.issues)
    assert any(i.code == 'TOTAL_MISMATCH' for i in report.issues)
    assert output_rows(target)[1][3] == 65.8
    assert run('ccb', src, tmp_path/'strict.xlsx',strict=True).status == 'FAILED'
    assert not (tmp_path/'strict.xlsx').exists()


def test_reno_timecards_generate_seven_calendar_days(workbook_factory,tmp_path):
    header = ['Name', date(2026,3,1), date(2026,3,2), date(2026,3,3), date(2026,3,4),
              date(2026,3,5), date(2026,3,6), date(2026,3,7)]
    src = workbook_factory('reno',header,[['Person A',0,9,9,0,0,0,0],
                                            ['Person B',0,16,0,0,0,0,0]])
    target = tmp_path/'reno_out.xlsx'
    report = run('reno',src,target,week_ending=date(2026,3,7))
    assert report.status == 'PREPARED', report.as_dict()
    assert report.rows_out == 7
    rows = output_rows(target)
    assert rows[2][6] == 25
    assert rows[2][7] == 0
    assert sum(r[6] for r in rows[1:]) == 34


def test_jz_maps_five_category_rows(workbook_factory,tmp_path):
    categories = ['Starline','Cables','Fibra','Connectors','Servertech']
    src = workbook_factory('jz',['Category','Paid Hours','OT Hours'],
         [[f'Direct Hours ({cat})',10+i,2+i] for i,cat in enumerate(categories)])
    output = tmp_path/'jz_prepared.xlsx'
    r = run('jz',src,output,week_ending=date(2026,2,28))
    assert r.status == 'PREPARED', r.as_dict()
    records = output_rows(output)
    assert len(records) == 6
    assert records[1][0:2] == ('BUS','3618')
    assert records[2][0:2] == ('DAT','3614')
    assert records[1][5].date() == date(2026,2,22)
    assert any(i.code == 'PROVISIONAL_SOURCE_SCHEMA' for i in r.issues)


def test_dayforce_ccb_excludes_receiving_cost_center(workbook_factory,tmp_path,refresh_evidence):
    header = ['Cost_Center','Pay_Date','Location','Pay_Category','Normal']
    src = workbook_factory('dayforce',header,[
        ['3600172100 > Receiving Farmingdale','03/02/2026','DPC CCB','Reg',11],
        ['1000 > Direct Labor','03/02/2026','DPC CCB','Reg',8]])
    path = tmp_path/'df.xlsx'
    r = run('dayforce_ccb',src,path,week_ending=date(2026,3,7),overrides=refresh_evidence(src))
    assert r.status == 'PREPARED', r.as_dict()
    assert r.rows_out == 1
    assert r.diagnostics['excluded_rows'] == 1
    assert r.diagnostics['filtered_reconciliation_metrics']['us_ccb_reg_hours']['total'] == 8


def test_dayforce_non_ccb_keeps_all_rows_and_filters_metrics_only(workbook_factory,tmp_path,refresh_evidence):
    header = ['Cost_Center','Pay_Date','Location','Pay_Category','Normal']
    src = workbook_factory('nonccb',header,[
        ['1025 > Plugs','03/02/2026','DPC BUS','Reg',5],
        ['1025 > Plugs','03/02/2026','OTHER','Reg',100]])
    path=tmp_path/'nonccb_prepared.xlsx'
    r=run('dayforce_non_ccb',src,path,week_ending=date(2026,3,7),overrides=refresh_evidence(src))
    assert r.status == 'PREPARED', r.as_dict()
    assert r.rows_out == 2
    assert r.diagnostics['filtered_reconciliation_metrics']['us_non_ccb_reg_hours']['total'] == 5


def test_taiwan_checks_missing_days_nulls_negatives(workbook_factory,tmp_path):
    src=workbook_factory('taiwan',['Date','Earn_Hours','Paid_Hours','Overtime_Hours'],
        [['03/01/2026',9,10,0],['03/03/2026',None,-1,0]])
    result=run('taiwan',src,tmp_path/'taiwan_clean.csv')
    assert result.status == 'FAILED'
    codes={i.code for i in result.issues}
    assert {'MISSING_DATES','NEGATIVE_VALUE','NULL_VALUE'} <= codes
    assert not (tmp_path/'taiwan_clean.csv').exists()
    assert (tmp_path/'taiwan_clean_quality.json').exists()


def test_fuzzy_header_and_reference_mismatch_block(workbook_factory,tmp_path):
    src=workbook_factory('typo',['DATE','NORM','OXT'],[[20260504,8,0]])
    result=run('sgp',src,tmp_path/'out.xlsx')
    assert result.status == 'FAILED'
    assert any(i.code == 'MISSING_COLUMN' and 'possible typo' in i.message for i in result.issues)
    correct=workbook_factory('correct',['DATE','NORM','OT'],[[20260504,8,0]])
    ref=workbook_factory('ref',['DATE','NORM','OT','Extra'],[])
    result=run('sgp',correct,tmp_path/'out2.xlsx',reference=ref)
    assert result.status == 'FAILED'
    assert any(i.code == 'DESTINATION_COLUMNS_MISSING' for i in result.issues)


def test_invalid_dates_fail_before_writing(workbook_factory,tmp_path):
    src=workbook_factory('invalid',['DATE','NORM','OT'],[['31/02/2026',8,0]])
    target=tmp_path/'bad.xlsx'
    r=run('sgp',src,target)
    assert r.status == 'FAILED'
    assert any(i.code == 'FORMAT_MISMATCH' for i in r.issues)
    assert not target.exists()


def test_date_ambiguity_blocks_without_convention():
    with pytest.raises(ValueError, match='ambiguous'):
        parse_date('03/04/2026','auto')


def test_auto_detect_sgp_and_dayforce_tie_requires_hint(workbook_factory, tmp_path):
    from factoryprep.detect import DetectionError, detect_profile
    sgp = workbook_factory('sgp_auto', ['DATE', 'NORM', 'OT'], [[20260504, 8, 1]])
    assert detect_profile(sgp) == 'sgp'
    source = workbook_factory('labor_export',
      ['Cost_Center','Pay_Date','Location','Pay_Category','Normal'],
      [['1000 > Direct Labor','03/02/2026','DPC CCB','Reg',8]])
    with pytest.raises(DetectionError, match='Ambiguous'):
        detect_profile(source)
    dayforce_ccb = tmp_path / 'DAYFORCE_CCB.xlsx'
    dayforce_ccb.write_bytes(source.read_bytes())
    assert detect_profile(dayforce_ccb) == 'dayforce_ccb'


def test_starline_ignored_empty_semicolon_and_rejects_extra_data(workbook_factory, tmp_path):
    src = workbook_factory('ssi_semicolon', ['W/E Date', 'BRD'], [['03/14/2026;', 15]])
    out = tmp_path / 'ssi_semicolon_out.xlsx'
    r = run('cbg_starline',src,out)
    assert r.status == 'PREPARED', r.as_dict()
    assert any(i.code == 'EMPTY_DATE_DELIMITER_REMOVED' for i in r.issues)
    invalid = workbook_factory('ssi_unsafe', ['W/E Date', 'BRD'], [['03/14/2026;HIDDEN DATA', 15]])
    out2 = tmp_path / 'ssi_unsafe_out.xlsx'
    r2 = run('cbg_starline', invalid, out2)
    assert r2.status == 'FAILED'
    assert not out2.exists()


def test_reviewed_ccb_correction_uses_exact_keys(workbook_factory, tmp_path):
    from textwrap import dedent
    source = workbook_factory('ccb_corrected', ['Row Labels', 'Plant', 'Dept',
        'Sum of Reg Hr','Sum of OT1.5 Hr','Sum of OT2 Hr','Sum of Total Hr'],
        [['01/05/2026','3617','3600171000',65.8,5,0,80.8]])
    yaml_file = tmp_path/'approved.yaml'
    yaml_file.write_text(dedent('''
      corrections:
        - profile: ccb
          match:
            Row Labels: '2026-01-05'
            Plant: '3617'
            Dept: '3600171000'
          column: Sum of Reg Hr
          expected_old: 65.8
          new_value: 75.8
    '''))
    target = tmp_path/'corrected.xlsx'
    r = run('ccb', source, target, overrides=yaml_file)
    assert r.status == 'PREPARED', r.as_dict()
    assert any(i.code == 'APPROVED_CORRECTION' for i in r.issues)
    assert not any(i.code == 'TOTAL_MISMATCH' for i in r.issues)
    assert output_rows(target)[1][3] == 75.8
    strict_target = tmp_path/'strict_corrected.xlsx'
    strict_result = run('ccb', source, strict_target, overrides=yaml_file, strict=True, week_ending=date(2026,1,10))
    assert strict_result.status == 'PREPARED', strict_result.as_dict()


def test_auto_prepare_end_to_end_and_wrong_extension(workbook_factory,tmp_path):
    src=workbook_factory('s_auto',['DATE','NORM','OT'],[[20260504,8,0]])
    out=tmp_path/'detected.xlsx'
    r=run('auto',src,out)
    assert r.profile=='sgp'
    assert r.status=='PREPARED', r.as_dict()
    bad=run('auto',src,tmp_path/'wrong.csv')
    assert bad.status=='FAILED'
    assert any(i.code=='OUTPUT_EXTENSION_MISMATCH' for i in bad.issues)
    assert not (tmp_path/'wrong.csv').exists()


def test_destination_template_aligns_column_order(workbook_factory, tmp_path):
    src=workbook_factory('src_order',['DATE','NORM','OT'],[[20260504,8,1]])
    template=workbook_factory('template',['OT','DATE','NORM'],[])
    dest=tmp_path/'reordered.xlsx'
    r=run('sgp',src,dest,reference=template)
    assert r.status=='PREPARED', r.as_dict()
    assert output_rows(dest)[0]==('OT','DATE','NORM')
    assert any(i.code=='DESTINATION_COLUMN_ORDER' for i in r.issues)
