import os
import pandas as pd
from training_data import prepare_training_data


def test_task7_processes_economics(tmp_path, monkeypatch):
    """Ensure task7 reads the economics CSV, creates processed file and updates config."""
    # Ensure the expected dataset path exists – the repository already contains the CSV.
    eco_path = os.path.join(prepare_training_data.DATASETS_DIR, "economics", "crop_economics.csv")
    assert os.path.isfile(eco_path)

    # Run task7 directly
    prepare_training_data.task7()

    # Verify processed CSV exists
    processed_path = os.path.join(prepare_training_data.OUT_DIR, "crop_economics_processed.csv")
    assert os.path.isfile(processed_path)
    df = pd.read_csv(processed_path)
    # Basic sanity: should have at least the column 'crop_name'
    assert "crop_name" in df.columns

    # Verify config entry
    cfg = prepare_training_data.config.get("crop_economics")
    assert cfg is not None
    assert cfg["target_column"] == "crop_name"
    assert "planting_density" in cfg["input_features"]
