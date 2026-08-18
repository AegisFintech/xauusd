from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SequenceDataset:
    x: np.ndarray
    y: np.ndarray
    timestamps: pd.DatetimeIndex


def build_sequence_dataset(features: pd.DataFrame, target: pd.Series, lookback: int = 60) -> SequenceDataset:
    """Create past-only windows ending at each target timestamp."""
    if lookback < 2:
        raise ValueError("lookback must be at least two")
    target = target.reindex(features.index)
    arrays, labels, timestamps = [], [], []
    for end in range(lookback - 1, len(features)):
        if pd.isna(target.iloc[end]):
            continue
        arrays.append(features.iloc[end - lookback + 1:end + 1].to_numpy(dtype=np.float32))
        labels.append(target.iloc[end])
        timestamps.append(features.index[end])
    shape = (0, lookback, features.shape[1])
    return SequenceDataset(np.stack(arrays) if arrays else np.empty(shape, dtype=np.float32),
                           np.asarray(labels), pd.DatetimeIndex(timestamps))


@dataclass(frozen=True)
class OfflineTransitions:
    observations: np.ndarray
    actions: np.ndarray
    rewards: np.ndarray
    next_observations: np.ndarray
    terminals: np.ndarray


def build_offline_transitions(features: pd.DataFrame, actions: pd.Series, future_returns: pd.Series,
                              transaction_cost: float = 0.0) -> OfflineTransitions:
    """Build an immutable historical transition table for offline PPO/SAC experiments."""
    aligned_actions = actions.reindex(features.index).fillna(0).clip(-1, 1).to_numpy(dtype=np.int8)
    returns = future_returns.reindex(features.index).fillna(0).to_numpy(dtype=float)
    observations = features.to_numpy(dtype=np.float32)
    rewards = aligned_actions[:-1] * returns[:-1] - transaction_cost * np.abs(np.diff(aligned_actions))
    terminals = np.zeros(len(rewards), dtype=bool)
    if len(terminals):
        terminals[-1] = True
    return OfflineTransitions(observations[:-1], aligned_actions[:-1], rewards,
                              observations[1:], terminals)


class TorchSequenceAdapter:
    """Dependency gate for offline LSTM/TCN/Transformer implementations."""

    def __init__(self, architecture: str):
        if architecture not in {"lstm", "tcn", "transformer"}:
            raise ValueError("architecture must be lstm, tcn, or transformer")
        try:
            import torch  # noqa: F401
        except ImportError as exc:
            raise ImportError("sequence models require the optional 'sequence' extra") from exc
        self.architecture = architecture
