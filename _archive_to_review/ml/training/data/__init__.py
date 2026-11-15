"""Expose the training data preparation utilities.

The original code lived in a top‑level ``training_data`` package. After the
reorganisation it was moved to ``ml/training/data``. This ``__init__`` file
re‑exports the public symbols so that imports such as
``from ml.training.data import prepare_training_data`` continue to work.
"""

# The actual implementation lives in ``ml/training/training_data``.
from ..training_data.prepare_training_data import *  # noqa: F403,F401

__all__ = [
    "DATASETS_DIR",
    "OUT_DIR",
    "config",
    "task1",
    "task2",
    "task3",
    "task4",
    "task5",
    "task6",
    "task7",
    "prepare_training_data",
]
