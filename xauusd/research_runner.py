"""Dependency-free, training-only tc02 baseline runner. Prints evidence, never trades.

Usage: python3 research_runner.py train.csv LOOKBACK HOLD momentum|reversal
CSV timestamp, open, close; price P/L per fixed ounce, never account returns.
Choose parameters before execution; this is a diagnostic, not qualification.
"""
import csv
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import sys


def run(rows, lookback, hold, mode):
    if not 1 <= lookback <= 240 or not 1 <= hold <= 240 or mode not in ('momentum', 'reversal'):
        raise ValueError('invalid_fixed_rule')
    times = [datetime.fromisoformat(r['timestamp']) for r in rows]
    if any(t.tzinfo is None for t in times) or any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError('unordered_or_naive_timestamps')
    prices = [(float(r['open']), float(r['close'])) for r in rows]
    if any(not math.isfinite(v) or v <= 0 for pair in prices for v in pair):
        raise ValueError('invalid_prices')
    breaks = [0]
    for a, b in zip(times, times[1:]):
        breaks.append(breaks[-1] + int((b-a).total_seconds() != 60))
    trades = []; busy = -1; skipped = 0
    for i in range(lookback, len(rows)-hold-1):
        if i <= busy:
            continue
        if breaks[i+hold+1] != breaks[i-lookback]:
            skipped += 1
            continue
        delta = prices[i][1]-prices[i-lookback][1]
        direction = (1 if delta > 0 else -1 if delta < 0 else 0) * (1 if mode == 'momentum' else -1)
        if not direction:
            continue
        pnl = direction*(prices[i+hold+1][0]-prices[i+1][0])
        trades.append((i, pnl)); busy = i+hold
    def metrics(values):
        n=len(values); gross=sum(values)
        return {'trades':n, 'gross':gross, 'base_net':gross-.47*n,
                'stress_net':gross-1.08*n, 'win_rate':sum(v>.47 for v in values)/n if n else None}
    values=[v for _,v in trades]
    return {**metrics(values), 'schema':'xauusd.training-baseline/1', 'classification':'unvalidated_training_only',
            'units':'fixed one ounce price P/L, not account return', 'rows':len(rows),
            'rule':{'lookback':lookback,'hold':hold,'mode':mode,'entry':'next open','exit':'open after hold bars'},
            'costs_per_roundtrip':{'base':.47,'stress':1.08},
            'thirds':[metrics([v for i,v in trades if min(2,i*3//max(1,len(rows)))==part]) for part in range(3)],
            'remove_best_two':metrics(sorted(values)[:-2]),'gap_windows_skipped':skipped}


if __name__ == '__main__':
    path=Path(sys.argv[1]); content=path.read_bytes()
    rows=list(csv.DictReader(content.decode().splitlines()))
    result=run(rows,int(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
    result['data_sha256']=hashlib.sha256(content).hexdigest()
    print(json.dumps(result,allow_nan=False))
