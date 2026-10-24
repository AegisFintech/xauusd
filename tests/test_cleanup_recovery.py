import json
from tests.test_lab import setup


def test_reconciliation_and_evidence_remain_available_at_unresolved_limit(tmp_path):
    from xauusd.agent_advisor import AgentAdvisor
    store, _ = setup(tmp_path)
    class Tools:
        def execute(self, name, arguments):
            assert name == 'tc02_job_status'
            return {'ok': True, 'state': 'completed', 'returncode': 0}
    advisor = AgentAdvisor(store, None, tmp_path, Tools())
    store.meta('agent_calls', [{'id': str(i), 'name': 'tc02_run', 'state': 'unknown',
        'remote_job_id': f'{i:032x}', 'result': {'ok': False}} for i in range(20)])
    read = advisor.execute({'id': 'read', 'name': 'evidence_read',
        'arguments_json': json.dumps({'call_id': '0'})}, tmp_path)
    assert read['result']['ok'] is True
    result = advisor.execute({'id': 'check', 'name': 'action_reconcile',
        'arguments_json': json.dumps({'call_id': '0'})}, tmp_path)
    assert result['result']['state'] == 'completed'
    assert next(r for r in store.meta('agent_calls') if r['id'] == '0')['state'] == 'completed'
    store.meta('agent_calls', [{'id': str(i), 'state': 'unknown'} for i in range(20)])
    refused = advisor.execute({'id': 'new', 'name': 'tc02_run', 'arguments_json': '{}'}, tmp_path)
    assert refused['result']['error_code'] == 'unresolved_action_limit'
