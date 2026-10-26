"""Sanitized application exchanges, distinct from private model reasoning.

Content-addressed bodies avoid repeating unchanged instructions. Reads are paged;
seven-day and 20 MB/2,000-entry limits bound operational storage on both backends.
"""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

MAX_BYTES = 20_000_000
MAX_ENTRIES = 2000
MAX_CAPTURE_CHARS = 2_000_000


class ConversationStore:
    def __init__(self, store):
        self.store = store
        with store.state.db() as db:
            db.execute('CREATE TABLE IF NOT EXISTS agent_conversation_bodies (digest TEXT PRIMARY KEY, content TEXT NOT NULL, size_bytes INTEGER NOT NULL)')
            db.execute('CREATE TABLE IF NOT EXISTS agent_conversation_entries (id TEXT PRIMARY KEY, recorded_at TEXT NOT NULL, kind TEXT NOT NULL, session_id TEXT NOT NULL, turn_id TEXT NOT NULL, digest TEXT NOT NULL)')
            db.execute('CREATE INDEX IF NOT EXISTS idx_conversation_time ON agent_conversation_entries(recorded_at,id)')

    def append(self, kind, payload, session_id='', turn_id='', now=None):
        now = now or datetime.now(timezone.utc)
        # Filter BEFORE any digest, persistence, slicing or preview is created.
        payload = self.store.filter.clean(payload)
        if isinstance(payload, dict) and isinstance(payload.get('detail'), dict):
            payload = {**payload, 'detail': {k:v for k,v in payload['detail'].items() if k not in ('session_id','turn_id')}}
        content = json.dumps(payload, ensure_ascii=False, allow_nan=False, indent=2)
        if len(content) > MAX_CAPTURE_CHARS:
            content = json.dumps({'capture_truncated': True, 'original_characters': len(content),
                                  'text': content[:max(0, MAX_CAPTURE_CHARS//2-100)]}, ensure_ascii=False)
        digest = hashlib.sha256(content.encode()).hexdigest()
        row = {'id': uuid4().hex, 'recorded_at': now.isoformat(), 'kind': kind,
               'session_id': session_id or '', 'turn_id': turn_id or '', 'digest': digest}
        with self.store.state.transaction() as tx:
            tx.lock('lab:conversation_lock')
            tx.db.execute('INSERT INTO agent_conversation_bodies(digest,content,size_bytes) VALUES(?,?,?) ON CONFLICT(digest) DO NOTHING',
                          (digest, content, len(content.encode())))
            tx.db.execute('INSERT INTO agent_conversation_entries(id,recorded_at,kind,session_id,turn_id,digest) VALUES(?,?,?,?,?,?)', tuple(row.values()))
            self._prune(tx, now)
        return row

    def _prune(self, tx, now):
        cutoff = (now - timedelta(days=7)).isoformat()
        removed = tx.db.execute('DELETE FROM agent_conversation_entries WHERE recorded_at < ?', (cutoff,)).rowcount
        rows = tx.db.execute('SELECT id FROM agent_conversation_entries ORDER BY recorded_at DESC,id DESC').fetchall()
        for row in rows[MAX_ENTRIES:]:
            tx.db.execute('DELETE FROM agent_conversation_entries WHERE id=?', (row['id'],)); removed += 1
        self._orphans(tx)
        size = tx.db.execute('SELECT COALESCE(SUM(size_bytes),0) n FROM agent_conversation_bodies').fetchone()['n']
        for row in reversed(rows[:MAX_ENTRIES]):
            if size <= MAX_BYTES: break
            tx.db.execute('DELETE FROM agent_conversation_entries WHERE id=?', (row['id'],)); removed += 1
            self._orphans(tx)
            size = tx.db.execute('SELECT COALESCE(SUM(size_bytes),0) n FROM agent_conversation_bodies').fetchone()['n']
        return removed

    @staticmethod
    def _orphans(tx):
        tx.db.execute('DELETE FROM agent_conversation_bodies WHERE NOT EXISTS (SELECT 1 FROM agent_conversation_entries e WHERE e.digest=agent_conversation_bodies.digest)')

    def prune(self, now=None):
        with self.store.state.transaction() as tx:
            tx.lock('lab:conversation_lock')
            return self._prune(tx, now or datetime.now(timezone.utc))

    def entries(self, before=None, limit=50):
        limit = min(100, max(1, limit))
        cutoff = (datetime.now(timezone.utc)-timedelta(days=7)).isoformat()
        before_time, _, before_id = (before or '').partition('|')
        with self.store.state.db() as db:
            rows = db.execute('SELECT e.*,b.size_bytes FROM agent_conversation_entries e JOIN agent_conversation_bodies b ON b.digest=e.digest WHERE e.recorded_at >= ? AND (? = ? OR e.recorded_at < ? OR (e.recorded_at = ? AND e.id < ?)) ORDER BY e.recorded_at DESC,e.id DESC LIMIT ?',
                              (cutoff, before_time, '', before_time, before_time, before_id, limit+1)).fetchall()
        return {'entries': [dict(r) for r in rows[:limit]], 'next_before': rows[limit-1]['recorded_at']+'|'+rows[limit-1]['id'] if len(rows)>limit else None,
                'retention_days': 7, 'max_bytes': MAX_BYTES, 'private_reasoning_available': False}

    def page(self, entry_id, offset=0, limit=3000):
        offset = max(0, offset); limit = min(12000, max(1, limit))
        cutoff = (datetime.now(timezone.utc)-timedelta(days=7)).isoformat()
        with self.store.state.db() as db:
            row = db.execute('SELECT e.*,b.content FROM agent_conversation_entries e JOIN agent_conversation_bodies b ON b.digest=e.digest WHERE e.id=? AND e.recorded_at>=?', (entry_id, cutoff)).fetchone()
        if not row: return {'ok': False, 'error_code': 'conversation_not_retained'}
        text = row['content']; end = min(len(text), offset+limit)
        return {'ok': True, 'id': entry_id, 'kind': row['kind'], 'session_id': row['session_id'], 'turn_id': row['turn_id'],
                'digest': row['digest'], 'text': text[offset:end], 'offset': offset, 'next_offset': end if end<len(text) else None, 'total_characters': len(text)}

    def download(self, entry_id):
        cutoff = (datetime.now(timezone.utc)-timedelta(days=7)).isoformat()
        with self.store.state.db() as db:
            row = db.execute('SELECT b.content FROM agent_conversation_entries e JOIN agent_conversation_bodies b ON b.digest=e.digest WHERE e.id=? AND e.recorded_at>=?', (entry_id, cutoff)).fetchone()
        return self.store.filter.clean(row['content']) if row else None
