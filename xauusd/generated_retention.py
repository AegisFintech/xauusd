"""Retention for regenerable Graphify snapshots, separate from research evidence."""
from datetime import datetime, timedelta, timezone
import json
import re


def graph_snapshot_files(root, now):
    from .retention import _safe, _pinned, _record
    graph = root / 'graphify-out'
    current = graph / 'graph.json'
    try:
        if not _safe(current, root) or not current.is_file(): return []
        value = json.loads(current.read_text())
        if not isinstance(value, dict) or not isinstance(value.get('nodes'), list): return []
    except (OSError, ValueError): return []
    allowed = {'graph.json','GRAPH_REPORT.md','manifest.json','.graphify_analysis.json',
               '.graphify_labels.json','.graphify_labels.json.sig'}
    directories = sorted((p for p in graph.iterdir() if re.fullmatch(r'\d{4}-\d{2}-\d{2}',p.name)), reverse=True)
    files = []
    for directory in directories[3:]:
        try:
            dated = datetime.strptime(directory.name, '%Y-%m-%d').replace(tzinfo=timezone.utc)
            if now-dated <= timedelta(days=7) or not _safe(directory,root) or _pinned(directory,root): continue
            children = list(directory.iterdir())
            if any(p.name not in allowed or not _safe(p,root) or not p.is_file() for p in children): continue
            files.extend(_record(p,'expired_generated_graph_snapshot') for p in children)
        except (OSError, ValueError): continue
    return files
