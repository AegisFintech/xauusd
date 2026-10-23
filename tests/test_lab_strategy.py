import numpy as np
import pandas as pd
import pytest


def bars(n=400):
    close=100+np.sin(np.arange(n)/8)+np.arange(n)*.002
    return pd.DataFrame({"open":close,"high":close+.2,"low":close-.2,"close":close,"volume":1},
                        index=pd.date_range("2026-01-01",periods=n,freq="min",tz="UTC"))


def test_expression_is_causal_and_bounded():
    from xauusd.lab_strategy import signals
    frame=bars()
    expr="where(ema(close, 8) > ema(close, 24), 1, -1)"
    full=signals(expr,frame)
    pd.testing.assert_series_equal(full.iloc[:150],signals(expr,frame.iloc[:150]))
    assert set(full.unique()) <= {-1,0,1}


@pytest.mark.parametrize("expr",["lag(close, -1)","close.shift(-1)","__import__('os')", "mean(close, 10000000)","close ** 999999", "open('/etc/passwd')"])
def test_expression_rejects_future_and_unbounded_code(expr):
    from xauusd.lab_strategy import signals, StrategyError
    with pytest.raises(StrategyError): signals(expr,bars())


def test_nonfinite_signal_fails_closed():
    from xauusd.lab_strategy import signals, StrategyError
    with pytest.raises(StrategyError): signals("close / 0",bars())


def test_frozen_partition_and_embargo_never_exposes_holdout():
    from xauusd.lab_strategy import freeze_dataset, partition
    frame=bars(1000); manifest=freeze_dataset(frame,embargo=32)
    train,validation=partition(frame,manifest)
    assert len(train)==568 and len(validation)==200
    assert train.index.max()<validation.index.min()
    assert validation.index.max()<pd.Timestamp(manifest['holdout_start'])
    extended=pd.concat([frame,bars(1200).iloc[1000:]])
    a,b=partition(extended,manifest)
    pd.testing.assert_frame_equal(a,train); pd.testing.assert_frame_equal(b,validation)


def test_validation_never_promotes_empty_or_forged_candidate():
    from xauusd.lab_strategy import assess, freeze_dataset
    frame=bars(1000)
    report=assess({'name':'flat','expression':'0'},frame,freeze_dataset(frame))
    assert report['passed'] is False and report['metrics']['profit_factor'] is None
    assert report['gates']['minimum_trades'] is False
    assert report['holdout_consumed'] is False
    assert report['execution']['spread'] > 0
