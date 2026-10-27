"""Bounded completion provenance and separate software/trading scorecards."""
from functools import wraps
from uuid import uuid4
from .lab_store import timestamp


def tracked_cycle(function):
    @wraps(function)
    def run(self,*args,**kwargs):
        cycle={'id':uuid4().hex,'origin':self.origin,'started_at':timestamp(),'state':'running'}
        self.cycle_id=cycle['id']
        def save():
            self.store.update('learning_cycles',lambda rows:([r for r in rows or [] if r['id']!=cycle['id']]+[dict(cycle)])[-120:],[])
        before={r['id'] for r in self.store.meta('research_outcomes') or []};save()
        try:
            value=function(self,*args,**kwargs);cycle['state']='completed';return value
        except BaseException:
            cycle['state']='failed';raise
        finally:
            findings=[r for r in self.store.meta('research_outcomes') or [] if r['id'] not in before and r.get('recorded_cycle_id')==cycle['id']]
            cycle.update(finished_at=timestamp(),findings=[r['id'] for r in findings],
                autonomous_findings=[r['id'] for r in findings if r.get('origin')=='autonomous' and r.get('recorded_by')=='autonomous'])
            save()
    return run


def scorecard(store):
    from .experiment_learning import assessment
    cycles=store.meta('learning_cycles') or [];outcomes=store.meta('research_outcomes') or []
    autonomous=[r for r in outcomes if r.get('origin')=='autonomous' and r.get('recorded_by')=='autonomous']
    accounts=[{'id':r['id'],'name':r.get('name','Unnamed experiment'),**assessment(r)} for r in store.meta('experiments') or []]
    candidates=store.candidates()
    return {'scope':'bounded_retained_records','software':{'verified_repairs':sum(r.get('state')=='verified' for r in store.meta('improvements') or []),
        'working_repairs':sum(r.get('state')=='working' for r in store.meta('improvements') or [])},
        'research':{'findings':len(outcomes),'autonomous_findings':len(autonomous),
            'operator_findings':sum(r.get('origin')=='operator' for r in outcomes),
            'legacy_origin_unknown':sum('origin' not in r for r in outcomes),
            'cycles_observed':len(cycles),'autonomous_cycles':sum(r['origin']=='autonomous' for r in cycles),
            'autonomous_cycles_with_findings':sum(bool(r.get('autonomous_findings')) for r in cycles),
            'last_autonomous_finding':autonomous[-1]['recorded_at'] if autonomous else None},
        'trading':{'qualified_candidates':sum(r['state'] in ('qualified','active') for r in candidates),
            'probation_candidates':sum(r['state']=='probation' for r in candidates),
            'profitability_proven':False,'paper_accounts':accounts},
        'reviews_due':sum(r['review_due'] for r in accounts),
        'policy':'Software verification, research completion and trading qualification are separate. Legacy/operator evidence never proves unattended discovery.'}
