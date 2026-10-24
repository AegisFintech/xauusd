import pandas as pd
from xauusd import lab_api


def test_dashboard_uses_metadata_and_bounded_tail_not_store_read(tmp_path, monkeypatch):
    from xauusd.data import HistoricalDataStore, DataConfig
    from xauusd import lab_market
    index=pd.date_range('2026-01-01',periods=6000,freq='min',tz='UTC',name='timestamp')
    frame=pd.DataFrame({'open':1.,'high':2.,'low':.5,'close':1.5,'volume':2.},index=index)
    path=tmp_path/'XAUUSD_M1.parquet';frame.to_parquet(path,row_group_size=500)
    store=HistoricalDataStore(DataConfig(processed_dir=tmp_path))
    monkeypatch.setattr(lab_market,'market_store',lambda:store)
    monkeypatch.setattr(HistoricalDataStore,'read',lambda self: (_ for _ in ()).throw(AssertionError('full history read')))
    summary=lab_market.coverage()
    assert summary['rows']==6000 and summary['end']==index[-1].isoformat()
    tail=lab_api._data('M1',20)
    assert len(tail)<=22 and tail.index[-1]==index[-1]
    assert lab_api.chart('M1',20)['count']==20
    # Replacement invalidates cache even if its pathname is unchanged.
    frame.iloc[:1000].to_parquet(path,row_group_size=500)
    assert lab_market.coverage()['rows']==1000
    assert lab_api._data('M1',20).index[-1]==index[999]
