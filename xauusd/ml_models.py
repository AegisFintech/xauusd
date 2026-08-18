from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Protocol

import numpy as np
from sklearn.base import ClassifierMixin
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture


class ProbabilityModel(Protocol):
    def fit(self, x, y): ...
    def predict_proba(self, x): ...


class OptionalDependencyError(ImportError):
    pass


def create_model(name: str, random_state: int = 31) -> ProbabilityModel:
    """Create a deterministic classifier; heavy backends remain optional extras."""
    if name == "hist_gradient_boosting":
        return HistGradientBoostingClassifier(max_iter=150, max_leaf_nodes=15, learning_rate=.05,
                                              random_state=random_state)
    if name == "random_forest":
        return RandomForestClassifier(n_estimators=150, max_depth=8, min_samples_leaf=20,
                                      n_jobs=-1, random_state=random_state, class_weight="balanced_subsample")
    if name == "extra_trees":
        return ExtraTreesClassifier(n_estimators=150, max_depth=8, min_samples_leaf=20,
                                    n_jobs=-1, random_state=random_state, class_weight="balanced")
    optional = {
        "xgboost": ("xgboost", "XGBClassifier", {"n_estimators": 150, "max_depth": 4, "learning_rate": .05,
                                                   "n_jobs": -1, "random_state": random_state}),
        "lightgbm": ("lightgbm", "LGBMClassifier", {"n_estimators": 150, "max_depth": 5,
                                                       "learning_rate": .05, "n_jobs": -1,
                                                       "random_state": random_state, "verbosity": -1}),
        "catboost": ("catboost", "CatBoostClassifier", {"iterations": 150, "depth": 5,
                                                           "learning_rate": .05, "random_seed": random_state,
                                                           "verbose": False}),
    }
    if name in optional:
        module, class_name, kwargs = optional[name]
        try:
            constructor = getattr(import_module(module), class_name)
        except ImportError as exc:
            raise OptionalDependencyError(f"{name} requires the optional '{module}' package") from exc
        return constructor(**kwargs)
    raise ValueError(f"unknown model backend: {name}")


@dataclass
class ProbabilityEnsemble:
    models: list[ProbabilityModel]

    def fit(self, x, y):
        for model in self.models:
            model.fit(x, y)
        return self

    def predict_proba(self, x):
        probabilities = np.stack([model.predict_proba(x) for model in self.models])
        return probabilities.mean(axis=0)


class RegimeTransformer:
    """Training-only scaler/KMeans regime model with one-hot output."""

    def __init__(self, clusters: int = 3, random_state: int = 31, method: str = "kmeans"):
        self.clusters = clusters
        self.scaler = StandardScaler()
        if method == "kmeans":
            self.model = KMeans(n_clusters=clusters, n_init=10, random_state=random_state)
        elif method == "gmm":
            self.model = GaussianMixture(n_components=clusters, covariance_type="full", random_state=random_state)
        else:
            raise ValueError("regime method must be 'kmeans' or 'gmm'")

    def fit(self, x):
        scaled = self.scaler.fit_transform(x)
        self.model.fit(scaled)
        return self

    def transform(self, x):
        labels = self.model.predict(self.scaler.transform(x))
        return np.eye(self.clusters, dtype=float)[labels]


class OfflinePolicyAdapter(Protocol):
    """Interface for future sequence/RL research; it cannot submit orders."""
    def fit(self, features, labels): ...
    def predict_signal(self, features): ...
