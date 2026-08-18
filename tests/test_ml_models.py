import numpy as np
import pytest

from xauusd.ml_models import (OptionalDependencyError, ProbabilityEnsemble, RegimeTransformer,
                              create_model)


def sample():
    rng=np.random.default_rng(4); x=rng.normal(size=(200,4)); y=(x[:,0]+x[:,1]>0).astype(int); return x,y


def test_core_model_adapters_and_ensemble_probabilities():
    x,y=sample()
    models=[create_model(name,7) for name in ("hist_gradient_boosting","random_forest","extra_trees")]
    probability=ProbabilityEnsemble(models).fit(x,y).predict_proba(x[:10])
    assert probability.shape==(10,2)
    assert np.allclose(probability.sum(axis=1),1)


def test_regime_transformer_is_fit_then_reused():
    x,_=sample()
    for method in ("kmeans","gmm"):
        regimes=RegimeTransformer(3,8,method).fit(x).transform(x[:12])
        assert regimes.shape==(12,3)
        assert np.all(regimes.sum(axis=1)==1)


def test_optional_backend_has_actionable_error_when_missing():
    try:
        import xgboost  # noqa: F401
    except ImportError:
        with pytest.raises(OptionalDependencyError,match="optional 'xgboost'"):
            create_model("xgboost")
