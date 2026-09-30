import os
import tempfile
import pandas as pd
import numpy as np

from pathlib import Path

# Import the module under test
from backend.ml.crop_recommendation import merge_data, train_model, recommend


def _create_dummy_training_csv(path: Path) -> None:
    """Create a minimal training CSV that matches the expectations of ``merge_data``.

    The CSV contains three numeric feature columns and a ``label_encoded`` target.
    """
    df = pd.DataFrame(
        {
            "feature_a": np.random.rand(10),
            "feature_b": np.random.rand(10),
            "feature_c": np.random.rand(10),
            "label_encoded": np.random.randint(0, 3, size=10),
        }
    )
    df.to_csv(path, index=False)


def test_merge_data_returns_features_and_target(tmp_path: Path):
    # Arrange – place a dummy CSV in the expected training_data location.
    training_dir = Path(r"c:\Users\USER\Downloads\FinalYearProject\training_data")
    training_dir.mkdir(parents=True, exist_ok=True)
    dummy_path = training_dir / "crop_recommendation_train.csv"
    _create_dummy_training_csv(dummy_path)

    # Act
    X, y = merge_data()

    # Assert
    assert isinstance(X, pd.DataFrame)
    assert isinstance(y, pd.Series)
    assert "label_encoded" not in X.columns
    assert X.shape[0] == y.shape[0] == 10


def test_train_model_fits_and_predicts(tmp_path: Path):
    # Create synthetic data directly (no file I/O needed for training).
    X = pd.DataFrame(
        {
            "f1": np.random.rand(20),
            "f2": np.random.rand(20),
            "f3": np.random.rand(20),
        }
    )
    y = np.random.randint(0, 2, size=20)

    model = train_model(X, y)
    # The model should have a ``predict`` method and produce the correct shape.
    preds = model.predict(X)
    assert preds.shape == (20,)
    # All predictions must be within the known class set.
    assert set(preds) <= {0, 1}


def test_recommend_returns_top_k(tmp_path: Path):
    # Train a quick model on synthetic data.
    X = pd.DataFrame({"a": [0, 1, 2], "b": [1, 0, 1]})
    y = [0, 1, 0]
    model = train_model(X, y)

    input_features = {"a": 0.5, "b": 0.5}
    recs = recommend(model, input_features, top_k=3)
    assert isinstance(recs, list)
    assert len(recs) == 3
    for r in recs:
        assert "crop_name" in r and "confidence" in r
        # Confidence should be a float between 0 and 1.
        assert 0.0 <= r["confidence"] <= 1.0

