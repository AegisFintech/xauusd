from datetime import datetime, timezone
from types import SimpleNamespace
import time
import pytest
from xauusd.agent_loop import AgentConfig, build_agent_registry
from xauusd.bits_runner import BitsAgentRunner
from xauusd.demo_execution import PaperToCTraderDemoCoordinator
from xauusd.local_state import SQLiteAgentTranscriptStore
from xauusd.paper_trading import PaperTrading, InMemoryPaperTradingStore
from xauusd.bits import BitsError

NOW = datetime(2026, 9, 23, 10, tzinfo=timezone.utc)


class Planner:
    def __init__(self): self.invocations=[]
    def submit(self, invocation):
        self.invocations.append(invocation)
        return "instance"
    def poll(self, instance, cycle, message):
        actions=[]
        if len(self.invocations)==1:
            actions=[dict(id="one",type="shell",args=dict(command="printf 42",cwd="/tmp",timeout_sec=2,max_output_bytes=1024))]
        return dict(protocol="xauusd/1",cycle_id=cycle,reply_to=message,
                    status="action_required" if actions else "completed",summary="ok",actions=actions,
                    next_review_at=None,blocker=None)


def runner(tmp_path, planner=None, paper=None):
    source=SimpleNamespace(read=lambda: SimpleNamespace(price=3000., observed_at=NOW))
    paper=paper or PaperTrading(InMemoryPaperTradingStore())
    paper.start("test")
    coordinator=PaperToCTraderDemoCoordinator(paper,paper_only=True)
    config=AgentConfig()
    registry=build_agent_registry(source,paper,coordinator,config)
    agent=BitsAgentRunner(planner or Planner(),registry,SQLiteAgentTranscriptStore(str(tmp_path/'state.db')),
                          source,paper,coordinator,config,now_provider=lambda:NOW)
    agent._age=lambda market: 0
    return agent


def test_complete_action_feedback_cycle(tmp_path):
    agent=runner(tmp_path)
    assert agent.run_tick()['status']=='bits_waiting'
    assert agent.run_tick()['status']=='shell_running'
    for _ in range(60):
        result=agent.run_tick()
        if result['status']=='bits_waiting': break
        time.sleep(.03)
    assert agent.planner.invocations[-1]['results'][0]['stdout']=='42'
    assert agent.run_tick()['status']=='completed'
    assert agent.run_tick()['status']=='waiting'
    agent.stop()


def test_market_closed_and_stopped_never_submit(tmp_path):
    agent=runner(tmp_path)
    agent._now_provider=lambda: datetime(2026,9,26,10,tzinfo=timezone.utc)
    assert agent.run_tick()['status']=='market_closed'
    agent.paper_trading.stop('operator')
    assert agent.run_tick()['status']=='stopped'
    assert agent.planner.invocations==[]
    agent.stop()


def test_pending_workflow_survives_restart(tmp_path):
    first=runner(tmp_path)
    first.run_tick()
    planner=first.planner
    first.stop()
    second=runner(tmp_path,planner)
    assert second.run_tick()['status']=='shell_running'
    assert len(planner.invocations)==1
    second.stop()


def test_second_process_refused_and_uncertain_submission_stops(tmp_path):
    first=runner(tmp_path)
    with pytest.raises(BitsError): runner(tmp_path)
    first.bits_store.put('cycle',{'phase':'submitting'})
    first.stop()
    second=runner(tmp_path)
    assert second.paper_trading.state()['kill_switch_reason']=='recovery_failed'
    assert second.run_tick()['status']=='stopped'
    second.stop()


def test_monitor_stops_loss_without_planner_call(tmp_path):
    from xauusd.paper_trading import PaperDecision
    agent=runner(tmp_path)
    agent.paper_trading.evaluate(PaperDecision('buy','XAUUSD','BUY',1,4000,NOW),NOW)
    assert agent.monitor_once()['status']=='stopped'
    assert agent.paper_trading.state()['kill_switch_reason']=='risk_limit'
    assert not agent.paper_trading.maybe_resume('restart')['resumed']
    assert agent.planner.invocations==[]
    agent.stop()


def test_stale_analysis_is_never_executed(tmp_path):
    from datetime import timedelta
    agent=runner(tmp_path)
    agent.run_tick()
    agent._now_provider=lambda: NOW+timedelta(seconds=200)
    assert agent.run_tick()['status']=='step_limit'
    assert agent.bits_store.get('cycle')['phase']=='idle'
    agent.stop()
