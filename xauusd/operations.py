from __future__ import annotations

from datetime import datetime,timezone
from pathlib import Path
import json
import shutil
import sqlite3
import gzip
import hashlib
import os
import statistics

from .experiment_registry import ExperimentRegistry


class OperationsManager:
 def __init__(self,registry_path=Path("data/experiments/registry.sqlite3"),
              backup_root=Path("backups/tournament"),reports=Path("reports/tournament")):
  self.registry_path=Path(registry_path); self.backup_root=Path(backup_root); self.reports=Path(reports)

 def health(self) -> dict:
  database={"available":self.registry_path.exists(),"integrity":"missing"}
  if self.registry_path.exists():
   with sqlite3.connect(self.registry_path) as db: database["integrity"]=db.execute("PRAGMA quick_check").fetchone()[0]
  disk=shutil.disk_usage(Path.cwd()); free_percent=100*disk.free/disk.total
  latest_path=self.backup_root/"latest.json"
  latest=json.loads(latest_path.read_text()) if latest_path.exists() else None
  backup_age=None
  if latest: backup_age=(datetime.now(timezone.utc)-datetime.fromisoformat(latest["created_at"])).total_seconds()/3600
  alerts=[]
  if database["integrity"]!="ok": alerts.append("database integrity check failed")
  if free_percent<15: alerts.append("disk free space below 15%")
  if backup_age is None or backup_age>30: alerts.append("backup missing or older than 30 hours")
  return {"healthy":not alerts,"database":database,"disk_free_percent":round(free_percent,1),
          "latest_backup":latest,"backup_age_hours":backup_age,"alerts":alerts}

 def scaling_checkpoint(self,registry: ExperimentRegistry | None=None,
                        status_path=Path("reports/tournament/distributed/status.json"),target: int=500_000) -> dict:
  registry=registry or ExperimentRegistry(); status_path=Path(status_path)
  status=json.loads(status_path.read_text()) if status_path.exists() else {}
  with registry.connect() as db:
   row=db.execute("""SELECT COUNT(*) total,
      SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) completed,
      SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) failed,
      SUM(CASE WHEN status='queued' THEN 1 ELSE 0 END) queued,
      SUM(CASE WHEN status='running' THEN 1 ELSE 0 END) running,
      SUM(CASE WHEN retry_count>0 THEN 1 ELSE 0 END) retried,
      COALESCE(SUM(retry_count),0) retries,COUNT(DISTINCT fingerprint) distinct_fingerprints
      FROM experiments""").fetchone()
  counts={key:int(row[key] or 0) for key in ("total","completed","failed","queued","running","retried","retries")}
  terminal=counts["completed"]+counts["failed"]
  duplicates=counts["total"]-int(row["distinct_fingerprints"] or 0)
  throughput=float(status.get("throughput_per_hour") or 0); remaining=max(0,target-counts["completed"])
  projected_hours=remaining/throughput if throughput>0 else None
  history=status.get("history") or []; cpu=[float(item.get("cpu_percent") or 0) for item in history]
  cpu_p95=None
  if cpu:
   ordered=sorted(cpu); cpu_p95=ordered[min(len(ordered)-1,int(.95*(len(ordered)-1)))]
  stages=status.get("stage_duration") or {}
  medians={name:(values or {}).get("median_seconds") for name,values in stages.items()}
  compute=float(medians.get("computing") or 0); overhead=sum(float(medians.get(name) or 0) for name in ("dispatching","importing"))
  network=((status.get("telemetry") or {}).get("network") or {})
  bottleneck="not_yet_verified"
  if compute>overhead and cpu_p95 is not None and cpu_p95>=85: bottleneck="secondary_compute"
  elif float(medians.get("importing") or 0)>compute: bottleneck="result_persistence"
  elif float(medians.get("dispatching") or 0)>compute: bottleneck="dispatch_or_network"
  checkpoints={str(value):{"target":value,"status":"reached" if counts["completed"]>=value else "pending",
                            "remaining":max(0,value-counts["completed"])} for value in (50_000,100_000,250_000,500_000)}
  return {"generated_at":datetime.now(timezone.utc).isoformat(),"target":target,"registry":counts,
          "checkpoints":checkpoints,"workers":status.get("workers"),"throughput_per_hour":throughput,
          "projected_hours_to_target":projected_hours,
          "required_throughput_for_24h":remaining/24,"throughput_multiplier_for_24h":remaining/24/throughput if throughput else None,
          "failure_rate":counts["failed"]/terminal if terminal else 0,"retried_scenario_rate":counts["retried"]/counts["total"] if counts["total"] else 0,
          "retry_attempts":counts["retries"],"duplicate_fingerprints":duplicates,
          "duration":status.get("duration"),"stage_duration":stages,
          "cpu_p95_percent":cpu_p95,"memory":(status.get("telemetry") or {}).get("memory"),
          "disk":(status.get("telemetry") or {}).get("disk"),"network":network,
          "measured_bottleneck":bottleneck,
          "limitations":["Projection uses the current coordinator-session throughput and must be refreshed after workload-family changes.",
                         "Cloud database billing and secondary-host price are not available, so monetary cost remains not yet verified."]}

 def backup(self) -> dict:
  run_id=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); directory=self.backup_root/run_id
  directory.mkdir(parents=True,exist_ok=False)
  destination=directory/"registry.sqlite3"
  with sqlite3.connect(self.registry_path) as source,sqlite3.connect(destination) as target: source.backup(target)
  copied=[]
  for source in (Path("data/tournaments/active.json"),self.reports/"worker-status.json",
                 self.reports/"adaptive.json",self.reports/"proposals.json"):
   if source.exists(): shutil.copy2(source,directory/source.name); copied.append(str(source))
  for source in self.reports.glob("*/champion.json"):
   target=directory/(source.parent.name+"-champion.json"); shutil.copy2(source,target); copied.append(str(source))
  state={"run_id":run_id,"created_at":datetime.now(timezone.utc).isoformat(),"directory":str(directory),
         "registry_bytes":destination.stat().st_size,"copied":copied}
  (directory/"manifest.json").write_text(json.dumps(state,indent=2))
  latest=self.backup_root/"latest.json"; temporary=latest.with_suffix(".json.tmp"); temporary.write_text(json.dumps(state,indent=2)); temporary.replace(latest)
  return state

 def compact_artifacts(self) -> dict:
  compressed=skipped=0; before=after=0
  with sqlite3.connect(self.registry_path) as db:
   rows=db.execute("SELECT id,artifacts_json FROM experiments WHERE artifacts_json IS NOT NULL").fetchall()
   for experiment_id,encoded in rows:
    artifacts=json.loads(encoded); changed=False
    for key in ("trades","holdout_trades"):
     value=artifacts.get(key)
     if not value: continue
     source=Path(value)
     if source.suffix==".gz" or not source.is_file(): skipped+=1; continue
     target=source.with_suffix(source.suffix+".gz"); before+=source.stat().st_size
     temporary=target.with_suffix(target.suffix+".tmp")
     with source.open("rb") as input_file,gzip.open(temporary,"wb",compresslevel=6) as output_file:
      shutil.copyfileobj(input_file,output_file)
     temporary.replace(target); after+=target.stat().st_size
     source.unlink(); artifacts[key]=str(target); compressed+=1; changed=True
    if changed: db.execute("UPDATE experiments SET artifacts_json=? WHERE id=?",(json.dumps(artifacts,sort_keys=True,separators=(",",":")),experiment_id))
  return {"compressed":compressed,"skipped":skipped,"bytes_before":before,"bytes_after":after,"bytes_saved":before-after}

 @staticmethod
 def artifact_retention_inventory(root: Path) -> dict:
  root=Path(root); groups={}; invalid=directories=without_result=0
  for directory in root.glob("xauusd-result-*"):
   if not directory.is_dir(): continue
   directories+=1; result_path=directory/"result.json"
   if not result_path.is_file(): without_result+=1; continue
   try: bundle=json.loads(result_path.read_text())
   except (OSError,json.JSONDecodeError): invalid+=1; continue
   retention=bundle.get("artifact_retention") or {}; reason=retention.get("reason","legacy_unclassified")
   row=groups.setdefault(reason,{"scenarios":0,"total_bytes":0,"detailed_scenarios":0,"detailed_files":0,
                                  "declared_detailed":0,"missing_declared_detail":0,"unexpected_detail":0})
   try: files=[path for path in directory.iterdir() if path.is_file()]
   except OSError: invalid+=1; continue
   detail=sum(path.name in {"trades.csv.gz","equity.parquet"} for path in files)
   declared=bool(retention.get("detailed")); row["scenarios"]+=1
   row["total_bytes"]+=sum(path.stat().st_size for path in files); row["detailed_files"]+=detail
   row["detailed_scenarios"]+=int(detail>0); row["declared_detailed"]+=int(declared)
   row["missing_declared_detail"]+=int(declared and detail<2); row["unexpected_detail"]+=int(not declared and detail>0)
  for row in groups.values(): row["average_bytes_per_scenario"]=round(row["total_bytes"]/row["scenarios"]) if row["scenarios"] else 0
  usage=shutil.disk_usage(root)
  return {"root":str(root.resolve()),"directories":directories,"result_bundles":sum(row["scenarios"] for row in groups.values()),
          "directories_without_result":without_result,"invalid_result_json":invalid,"groups":dict(sorted(groups.items())),
          "disk":{"total":usage.total,"used":usage.used,"free":usage.free,"percent":round(100*usage.used/usage.total,1)}}

 def remote_artifacts_plan(self,output=Path("reports/tournament/remote-artifact-compaction-plan.json"),audit_percent=1) -> dict:
  candidates=[]; protected=[]
  with sqlite3.connect(self.registry_path) as db:
   db.row_factory=sqlite3.Row
   rows=db.execute("""SELECT id,fingerprint,status,promoted,validation_json,artifacts_json
                      FROM experiments WHERE status='completed' AND artifacts_json IS NOT NULL ORDER BY id""").fetchall()
  for row in rows:
   artifacts=json.loads(row["artifacts_json"] or "{}"); remote=artifacts.get("remote_directory")
   if not remote: continue
   validation=json.loads(row["validation_json"] or "{}"); gates=validation.get("gates") or {}
   reason=None
   if row["promoted"]: reason="promoted"
   elif validation.get("passed"): reason="validation_passed"
   elif gates and sum(not bool(value) for value in gates.values())<=1: reason="validation_near_pass"
   elif int(row["fingerprint"][:8],16)%100<max(0,min(100,int(audit_percent))): reason="deterministic_audit_sample"
   item={"experiment_id":row["id"],"fingerprint":row["fingerprint"],"remote_directory":remote}
   if reason: protected.append({**item,"reason":reason})
   else: candidates.append({**item,"reason":"ordinary_completed_reject"})
  payload={"created_at":datetime.now(timezone.utc).isoformat(),"mode":"dry_run",
           "audit_percent":audit_percent,"candidate_count":len(candidates),"protected_count":len(protected),
           "candidates":candidates,"protected":protected}
  payload["plan_digest"]=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
  output=Path(output); output.parent.mkdir(parents=True,exist_ok=True)
  temporary=output.with_suffix(output.suffix+".tmp"); temporary.write_text(json.dumps(payload,indent=2)); temporary.replace(output)
  return {"output":str(output),"plan_digest":payload["plan_digest"],"candidate_count":len(candidates),
          "protected_count":len(protected),"audit_percent":audit_percent}

 @staticmethod
 def apply_remote_artifacts_plan(plan_path: Path,digest: str,journal_path: Path,
                                 allowed_root="/opt/xauusd/var/results") -> dict:
  plan=json.loads(Path(plan_path).read_text()); stored=plan.pop("plan_digest",None)
  actual=hashlib.sha256(json.dumps(plan,sort_keys=True,separators=(",",":")).encode()).hexdigest()
  if stored!=digest or actual!=digest: raise ValueError("compaction plan digest mismatch")
  completed={}
  journal_path=Path(journal_path); journal_path.parent.mkdir(parents=True,exist_ok=True)
  if journal_path.exists():
   for line in journal_path.read_text().splitlines():
    row=json.loads(line); completed[int(row["experiment_id"])]=row
  removed_files=removed_bytes=missing_paths=0
  with journal_path.open("a") as journal:
   for item in plan["candidates"]:
    eid=int(item["experiment_id"])
    if eid in completed: continue
    directory=Path(item["remote_directory"])
    valid=str(directory).startswith(f"{allowed_root}/xauusd-result-") or str(directory).startswith("/tmp/xauusd-result-")
    if not valid or directory.name!=f"xauusd-result-{eid}": raise ValueError(f"unsafe compaction path for {eid}")
    files=bytes_=0
    if directory.is_dir():
     for name in ("trades.csv.gz","equity.parquet"):
      target=directory/name
      if target.is_file(): bytes_+=target.stat().st_size; target.unlink(); files+=1
    else: missing_paths+=1
    row={"experiment_id":eid,"fingerprint":item["fingerprint"],"remote_directory":str(directory),
         "removed_files":files,"removed_bytes":bytes_,"completed_at":datetime.now(timezone.utc).isoformat()}
    journal.write(json.dumps(row,sort_keys=True)+"\n"); journal.flush(); os.fsync(journal.fileno())
    removed_files+=files; removed_bytes+=bytes_
  return {"plan_digest":digest,"planned":len(plan["candidates"]),"previously_completed":len(completed),
          "removed_files":removed_files,"removed_bytes":removed_bytes,"missing_paths":missing_paths,
          "journal":str(journal_path)}

 def reconcile_remote_artifacts(self,plan_path: Path,digest: str,journal_path: Path) -> dict:
  plan=json.loads(Path(plan_path).read_text()); stored=plan.pop("plan_digest",None)
  actual=hashlib.sha256(json.dumps(plan,sort_keys=True,separators=(",",":")).encode()).hexdigest()
  if stored!=digest or actual!=digest: raise ValueError("compaction plan digest mismatch")
  candidates={int(x["experiment_id"]):x for x in plan["candidates"]}; rows={}
  for line in Path(journal_path).read_text().splitlines():
   row=json.loads(line); eid=int(row["experiment_id"])
   if eid not in candidates or row["fingerprint"]!=candidates[eid]["fingerprint"]: raise ValueError("journal does not match plan")
   rows[eid]=row
  now=datetime.now(timezone.utc).isoformat(); updated=0
  with sqlite3.connect(self.registry_path) as db:
   for eid,row in rows.items():
    current=db.execute("SELECT artifacts_json FROM experiments WHERE id=? AND status='completed'",(eid,)).fetchone()
    if not current: raise ValueError(f"experiment {eid} is not completed")
    artifacts=json.loads(current[0] or "{}"); artifacts["detail_retention"]={"detailed":False,
     "reason":"historical_ordinary_reject_compacted","plan_digest":digest,"compacted_at":row["completed_at"],
     "removed_files":row["removed_files"],"removed_bytes":row["removed_bytes"]}
    db.execute("UPDATE experiments SET artifacts_json=? WHERE id=?",(json.dumps(artifacts,sort_keys=True,separators=(",",":")),eid))
    db.execute("INSERT INTO experiment_events(experiment_id,occurred_at,event,payload_json) VALUES(?,?,?,?)",
     (eid,now,"remote_artifacts_compacted",json.dumps({"plan_digest":digest,"removed_files":row["removed_files"],"removed_bytes":row["removed_bytes"]},sort_keys=True,separators=(",",":"))))
    updated+=1
  return {"plan_digest":digest,"journal_rows":len(rows),"updated":updated,
          "removed_files":sum(x["removed_files"] for x in rows.values()),"removed_bytes":sum(x["removed_bytes"] for x in rows.values())}
