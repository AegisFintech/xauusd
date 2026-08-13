from xauusd.core import synthetic_bars,features,Backtester
def test_backtest():
 b=synthetic_bars(500); f=features(b); r=Backtester().run(f,(f.momentum>0).astype(int)); assert "sharpe" in r
