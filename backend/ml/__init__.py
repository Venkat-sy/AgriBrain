"""Compatibility shim for legacy imports.

The project originally referenced ``backend.ml.crop_recommendation``. After the
re‑organisation the implementation lives under ``ml/inference``. To avoid
touching the test suite (or any external code that still uses the old import
path) we expose a thin wrapper that re‑exports the public API.
"""

from ml.inference.crop_recommendation import (  # noqa: F401
    merge_data,
    train_model,
    recommend,
)

__all__ = ["merge_data", "train_model", "recommend"]
