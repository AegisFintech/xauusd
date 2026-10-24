import json
from datetime import datetime,timezone


def test_graph_snapshots_keep_latest_three_and_pins_and_unknown_files(tmp_path):
    from xauusd.retention import retention_plan
    root=tmp_path/'graphify-out';root.mkdir()
    (root/'graph.json').write_text(json.dumps({'nodes':[],'links':[]}))
    for day in range(1,8):
        directory=root/f'2026-09-{day:02d}';directory.mkdir()
        (directory/'graph.json').write_text('{}')
    (root/'2026-09-02'/'.pin').touch()
    (root/'2026-09-03'/'manual-notes.txt').write_text('keep')
    plan=retention_plan(tmp_path,datetime(2026,10,24,tzinfo=timezone.utc))
    selected={str(p['path']) for p in plan['files']}
    assert str(root/'2026-09-01'/'graph.json') in selected
    for day in (2,3,5,6,7):
        assert str(root/f'2026-09-{day:02d}'/'graph.json') not in selected
