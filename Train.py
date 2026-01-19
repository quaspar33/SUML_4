import os
from pathlib import Path

import pandas as pd
from autogluon.tabular import TabularDataset, TabularPredictor


def main():

    # Ścieżki
    models_dir = Path("Data/models")

    models_dir.mkdir(parents=True, exist_ok=True)

    train_path = Path("data/raw_data/ai_job_dataset.csv")

    if not train_path.exists():
        raise FileNotFoundError(f"Nie znaleziono pliku z danymi treningowymi: {train_path}")

    train_data = TabularDataset(str(train_path))
    label_column = "salary_usd"

    if label_column not in train_data.columns:
        raise ValueError(
            f"Kolumna celu '{label_column}' nie istnieje w danych. "
            f"Dostępne kolumny: {list(train_data.columns)}"
        )

    predictor = TabularPredictor(
        label=label_column,
        path=str(models_dir),
        problem_type="regression",
        eval_metric="root_mean_squared_error"
    ).fit(
        train_data=train_data,
        presets="medium_quality",  # best_quality/faster_train
        time_limit=600,          # limit czasu
        verbosity=2
    )

    # tabela z informacjami o wszystkich modelach
    leaderboard_df = predictor.leaderboard(train_data, silent=True)

    models_csv_path = models_dir / "models.csv"
    leaderboard_df.to_csv(models_csv_path, index=False)



if __name__ == "__main__":
    main()
