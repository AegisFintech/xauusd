import sqlite3
from datetime import datetime, timezone
import pytest
from xauusd.bits_jobs import BitsStore, AgentLock, AgentAlreadyRunning
from xauusd.local_state import SQLitePaperTradingStore, SQLiteAgentTranscriptStore
from xauusd.paper_trading import PaperTrading, PaperDecision
from xauusd.session_reset import reset_paper_session
from xauusd.state_backup import restore_local_state


def seeded(tmp_path):
    path=str(tmp_path/'state.db')
    paper=PaperTrading(SQLitePaperTradingStore(path, initial_cash=10000))
    transcript=SQLiteAgentTranscriptStore(path)
    transcript.start_run('old-run');transcript.append('old-run',1,'assistant',{'summary':'old reasoning'})
    store=BitsStore(transcript);store.put('memory',{'recent':['old context']});store.put('cycle',{'phase':'idle'})
    paper.start('test');now=datetime(2026,9,23,10,tzinfo=timezone.utc)
    paper.evaluate(PaperDecision('old-trade','XAUUSD','BUY',1,3000,now),now)
    paper.stop('operator')
    with sqlite3.connect(path) as db:
        db.execute('CREATE TABLE unrelated_research (note TEXT)');db.execute("INSERT INTO unrelated_research VALUES('preserve')")
    return paper,transcript,store


def test_reset_clears_session_atomically_and_keeps_verified_backup(tmp_path):
    paper,transcript,store=seeded(tmp_path)
    result=reset_paper_session(paper,transcript,tmp_path/'backups')
    assert paper.state()['cash']==10000 and paper.state()['position']==0
    assert paper.state()['stopped'] and paper.state()['ledger']==[]
    assert transcript.runs()==[] and transcript.steps()==[]
    assert store.get('memory') is None and store.get('cycle') is None
    assert store.get('session_reset')['initial_cash']==10000
    with sqlite3.connect(paper.store.db_path) as db:
        assert db.execute('SELECT COUNT(*) FROM paper_trading_decisions').fetchone()[0]==0
        assert db.execute('SELECT note FROM unrelated_research').fetchone()[0]=='preserve'
    restored=tmp_path/'restored.db'
    restore_local_state(result['backup'],restored)
    assert SQLitePaperTradingStore(str(restored)).state()['position']==1


def test_reset_refuses_active_agent_and_unstopped_paper(tmp_path):
    paper,transcript,store=seeded(tmp_path)
    paper.start('test')
    with pytest.raises(ValueError): reset_paper_session(paper,transcript,tmp_path/'backups')
    paper.stop('operator');lock=AgentLock(transcript)
    try:
        with pytest.raises(AgentAlreadyRunning):reset_paper_session(paper,transcript,tmp_path/'backups')
    finally:lock.close()
    assert len(paper.state()['ledger'])==1
