from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path
import json
app=FastAPI(title="XAUUSD Research Dashboard")
@app.get("/health")
def health(): return {"status":"ok","mode":"research-only"}
@app.get("/api/leaderboard")
def leaderboard():
 p=Path("reports/leaderboard.json"); return json.loads(p.read_text()) if p.exists() else []
@app.get("/",response_class=HTMLResponse)
def home(): return "<html><body style='background:#111;color:#eee;font-family:sans-serif'><h1>XAUUSD Research Dashboard</h1><p>Research-only mode · <a href='/docs'>API</a></p><pre id='x'>Loading…</pre><script>fetch('/api/leaderboard').then(r=>r.json()).then(x=>document.querySelector('#x').textContent=JSON.stringify(x,null,2))</script></body></html>"
