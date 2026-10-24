"""Read-only dashboard projections with bounded memory and compact caches."""
from collections import OrderedDict
from threading import RLock
import json
import pandas as pd
import pyarrow.parquet as pq

RULES = {'M1':'1min','M5':'5min','M15':'15min','H1':'1h','H4':'4h','D1':'1D'}
AGG = {'open':'first','high':'max','low':'min','close':'last','volume':'sum'}
_lock = RLock()
_cache = OrderedDict()


def market_store():
    from .data import HistoricalDataStore
    return HistoricalDataStore()


def _file():
    path = market_store().path
    stat = path.stat()
    return (str(path.resolve()),stat.st_ino,stat.st_mtime_ns,stat.st_size), pq.ParquetFile(path)


def _index_name(file):
    metadata = json.loads(file.schema_arrow.metadata[b'pandas'])
    indexes = metadata['index_columns']
    if len(indexes) != 1 or not isinstance(indexes[0], str):
        raise ValueError('unsupported_market_index')
    return indexes[0]


def coverage():
    with _lock:
        key,file = _file()
        cache_key=(key,'coverage')
        if cache_key in _cache: return dict(_cache[cache_key])
        column=_index_name(file)
        position=file.schema_arrow.get_field_index(column)
        starts=[];ends=[]
        for i in range(file.num_row_groups):
            group=file.metadata.row_group(i)
            stats=group.column(position).statistics
            if stats is not None and stats.has_min_max:
                starts.append(pd.Timestamp(stats.min));ends.append(pd.Timestamp(stats.max))
            else:
                # Timestamp-only batches, never all OHLCV history.
                for batch in file.iter_batches(batch_size=8192,row_groups=[i],columns=[column]):
                    index=pd.DatetimeIndex(batch.column(0).to_pandas())
                    if len(index): starts.append(index.min());ends.append(index.max())
        if not starts: raise ValueError('empty_market_store')
        result={'rows':file.metadata.num_rows,'start':min(starts).isoformat(),
                'end':max(ends).isoformat(),'columns':list(AGG)}
        _put(cache_key,result)
        return dict(result)


def _put(key,value):
    _cache[key]=value
    while len(_cache)>16: _cache.popitem(last=False)


def chart_bars(timeframe='M1',limit=1000,now=None):
    rule=RULES[timeframe]; interval=pd.Timedelta(rule)
    now=pd.Timestamp(now or pd.Timestamp.now(tz='UTC'))
    with _lock:
        key,file=_file()
        cache_key=(key,timeframe,limit,now.floor('min').isoformat())
        if cache_key in _cache: return _cache[cache_key].copy()
        needed=(limit+2)*int(interval.total_seconds()/60)
        groups=[];count=0
        for i in reversed(range(file.num_row_groups)):
            groups.append(i);count+=file.metadata.row_group(i).num_rows
            if count>=needed: break
        view=pd.DataFrame(columns=list(AGG),index=pd.DatetimeIndex([],tz='UTC'))
        for batch in file.iter_batches(batch_size=8192,row_groups=sorted(groups)):
            part=batch.to_pandas()
            part=part.loc[part.index+pd.Timedelta(minutes=1)<=now]
            if part.empty: continue
            part=part.resample(rule).agg(AGG).dropna() if timeframe!='M1' else part
            view=pd.concat([view,part]) if len(view) else part
            if view.index.has_duplicates:
                view=view.groupby(level=0,sort=True).agg(AGG)
            view=view.tail(limit+2)
        view=view.loc[view.index+interval<=now].tail(limit)
        _put(cache_key,view)
        return view.copy()
