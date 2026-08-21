import pandas as pd
import pytest
import xauusd.portfolio_research as portfolio_module

from xauusd.core import synthetic_bars
from xauusd.portfolio_research import (
 aligned_returns, classify_regimes, effective_number_of_bets, equity_metrics,
 leave_one_out, portfolio_equity, portfolio_weights,
)
from xauusd.research import build_features


def test_regime_labels_are_causal_and_complete():
 bars=synthetic_bars(1500,seed=121); earlier=build_features(bars.iloc[:1200]); full=build_features(bars)
 left=classify_regimes(earlier); right=classify_regimes(full.loc[earlier.index])
 pd.testing.assert_series_equal(left,right)
 assert not left.isna().any() and all(label.count("|")==2 for label in left)


def test_equity_metrics_measure_portfolio_drawdown():
 index=pd.date_range("2026-01-01",periods=4,freq="min",tz="UTC")
 metrics=equity_metrics(pd.Series([100.,110.,99.,120.],index=index))
 assert metrics["net_profit"]==20 and metrics["max_drawdown"]==pytest.approx(-0.1)


def test_weights_are_long_only_normalized_and_causal():
 index=pd.date_range("2026-01-01",periods=20,freq="min",tz="UTC")
 fit=pd.DataFrame({"a":[.01,-.01]*10,"b":[.002,-.001]*10},index=index)
 for method in ("equal","inverse_volatility","correlation_aware"):
  weights=portfolio_weights(fit.iloc[:10],method)
  future_changed=fit.copy(); future_changed.iloc[10:]*=100
  pd.testing.assert_series_equal(weights,portfolio_weights(future_changed.iloc[:10],method))
  assert weights.sum()==pytest.approx(1) and (weights>=0).all()


def test_portfolio_uses_weighted_returns_and_alignment():
 index=pd.date_range("2026-01-01",periods=4,freq="min",tz="UTC")
 curves={"a":pd.Series([100,110,110,121],index=index),"b":pd.Series([100,100,110,110],index=index)}
 returns=aligned_returns(curves); equity=portfolio_equity(returns,pd.Series({"a":.5,"b":.5}),100)
 assert equity.iloc[-1]==pytest.approx(100*1.05*1.05*1.05)


def test_effective_bets_detect_perfect_correlation():
 returns=pd.DataFrame({"a":[.01,-.01,.02],"b":[.01,-.01,.02]})
 assert effective_number_of_bets(returns,pd.Series({"a":.5,"b":.5}))==pytest.approx(1)


def test_leave_one_out_and_no_trade_metrics():
 returns=pd.DataFrame({"a":[.01,.01,.01],"b":[0.,0.,0.]},index=pd.date_range("2026-01-01",periods=3,freq="min",tz="UTC"))
 report=leave_one_out(returns,pd.Series({"a":.5,"b":.5}))
 assert {row["omitted"] for row in report}=={"a","b"}
 no_trade=equity_metrics(pd.Series([100.,100.,100.]))
 assert no_trade["total_return"]==0 and no_trade["max_drawdown"]==0


def test_portfolio_run_reads_validation_only(tmp_path,monkeypatch):
 index=pd.date_range("2026-01-01",periods=10,freq="min",tz="UTC")
 leaders=[]
 for number,family in ((1,"momentum"),(2,"mean_reversion")):
  equity=tmp_path/f"equity-{number}.parquet"; trades=tmp_path/f"trades-{number}.csv.gz"
  pd.DataFrame({"equity":[100+i*number for i in range(10)]},index=index).to_parquet(equity)
  pd.DataFrame({"exit_time":[index[-1]],"net_pnl":[1.]}).to_csv(trades,index=False,compression="gzip")
  leaders.append({"id":number,"strategy_family":family,"artifacts":{"equity":str(equity),"trades":str(trades)},
                  "validation":{"score":1.},"metrics":{"validation":{"exposure":.2}}})
 class Registry:
  def leaderboard(self,limit): return leaders
 class Dataset:
  reads=[]
  def read(self,partition): self.reads.append(partition); return pd.DataFrame(index=index)
 features=pd.DataFrame({"atr_14":1.,"close":100.,"trend_strength":1.},index=index)
 monkeypatch.setattr(portfolio_module,"build_features",lambda bars:features)
 dataset=Dataset(); report=portfolio_module.PortfolioResearch(Registry(),dataset,tmp_path/"report").run()
 assert dataset.reads==["validation"] and report["holdout_used"] is False
 assert report["baselines"]["no_trade"]["total_return"]==0
