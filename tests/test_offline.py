import numpy as np
import pandas as pd
import pytest

from xauusd.offline import TorchSequenceAdapter, build_offline_transitions, build_sequence_dataset


def test_sequence_windows_never_include_future_rows():
    index=pd.date_range("2025-01-01",periods=8,freq="min",tz="UTC")
    features=pd.DataFrame({"value":np.arange(8)},index=index); target=pd.Series(np.arange(8),index=index)
    data=build_sequence_dataset(features,target,lookback=3)
    assert data.x[0,:,0].tolist()==[0,1,2]
    assert data.timestamps[0]==index[2]
    assert data.y[0]==2


def test_offline_transitions_are_aligned_and_terminal():
    index=pd.date_range("2025-01-01",periods=5,freq="min",tz="UTC")
    features=pd.DataFrame({"value":np.arange(5)},index=index)
    actions=pd.Series([0,1,1,-1,0],index=index); returns=pd.Series([0,.1,.2,-.1,0],index=index)
    data=build_offline_transitions(features,actions,returns,transaction_cost=.01)
    assert len(data.rewards)==4 and data.terminals[-1]
    assert data.observations[0,0]==0 and data.next_observations[0,0]==1


def test_torch_adapter_explains_missing_extra():
    try:
        import torch  # noqa: F401
    except ImportError:
        with pytest.raises(ImportError,match="optional 'sequence' extra"):
            TorchSequenceAdapter("lstm")
