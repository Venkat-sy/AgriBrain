"""Compatibility shim for the original ``backend.ml.crop_recommendation`` module.

The implementation now resides in ``ml/inference/crop_recommendation.py``. To
preserve the public import path used by the test suite we simply re‑export the
objects.
"""

from ml.inference.crop_recommendation import (  # noqa: F401
    merge_data,
    train_model,
    recommend,
)

__all__ = ["merge_data", "train_model", "recommend"]
