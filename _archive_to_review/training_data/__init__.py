"""Compatibility shim for the original ``training_data`` package.

The original tests import ``prepare_training_data`` directly from a top‑level
``training_data`` package. After reorganising the repository the implementation
was moved to ``ml/training/data``. This shim re‑exports the public objects so
the existing test suite continues to work without modification.
"""

# The implementation resides in ``ml/training/training_data/prepare_training_data.py``.
# Import the helper module so that ``training_data.prepare_training_data`` is
# available as an attribute (the tests use ``from training_data import
# prepare_training_data``).
from ml.training.training_data import prepare_training_data as prepare_training_data  # noqa: F401
# Re‑export all public symbols for convenience.
from ml.training.training_data.prepare_training_data import *  # noqa: F403,F401

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
