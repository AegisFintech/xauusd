from __future__ import annotations

from datetime import datetime,timezone
from pathlib import Path
import json
import shutil
import sqlite3
import gzip
import hashlib


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
