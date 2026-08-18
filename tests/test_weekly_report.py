from datetime import datetime,timezone

from xauusd.experiment_registry import ExperimentRegistry,ExperimentSpec
from xauusd.weekly_report import WeeklyTournamentReport


def test_weekly_report_tracks_throughput_families_and_multiple_testing(tmp_path):
 registry=ExperimentRegistry(tmp_path/"registry.db")
 spec=ExperimentSpec("momentum","f",{},"v","d","e","c"); row,_=registry.register(spec); claimed=registry.claim_next("w")
 registry.complete(claimed["id"],"w",{"validation":{"net_profit":2}}, {"score":1.5,"passed":True})
 report=WeeklyTournamentReport(registry,tmp_path/"weekly").build(datetime.now(timezone.utc))
 assert report["all_time_completed"]==1 and report["families"]["momentum"]["passed"]==1
 assert report["multiple_testing"]["experiments"]==1 and (tmp_path/"weekly"/"latest.json").exists()
