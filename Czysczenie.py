# === ETAP 1: Czyszczenie i zamiana kolumn kategorycznych na numeryczne ===

import pandas as pd
import numpy as np
from pathlib import Path

# --- Ścieżki ---
data_path = Path("Data/ai_job_dataset.csv")
output_path = Path("Data/ai_job_dataset_clean.csv")

# --- Wczytanie danych ---
df = pd.read_csv(data_path)

# --- Usunięcie białych znaków z napisów ---
obj_cols = df.select_dtypes(include=["object"]).columns
for col in obj_cols:
    df[col] = df[col].str.strip()

# --- Konwersja kolumn dat na typ datetime ---
date_cols = ["posting_date", "application_deadline"]
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# --- Normalizacja wartości remote_ratio (upewnienie, że to 0, 50, 100) ---
if "remote_ratio" in df.columns:
    df["remote_ratio"] = pd.to_numeric(df["remote_ratio"], errors="coerce").clip(0, 100)
    df["remote_ratio"] = df["remote_ratio"].apply(lambda x: min([0, 50, 100], key=lambda v: abs(v - x)))

# --- Kodowanie kolumn kategorycznych ---

# Encoding dla kolumn o wielu wartościach
encode_cols = ["job_title", "job_category", "industry", "company_location", "employee_residence"]
for col in encode_cols:
    if col in df.columns:
        df[col + "_num"] = df[col].astype("category").cat.codes

# One-Hot Encoding dla prostych kategorii
onehot_cols = ["experience_level", "employment_type", "company_size", "education_required"]
df = pd.get_dummies(df, columns=[c for c in onehot_cols if c in df.columns], prefix_sep="_", dtype=int)

# Zamiana wartości ordinalnych
# company_size: S<M<L
if "company_size_S" not in df.columns and "company_size" in df.columns:
    size_map = {"S": 0, "M": 1, "L": 2}
    df["company_size_ord"] = df["company_size"].map(size_map)

# education_required (jeśli istnieje)
if "education_required" in df.columns:
    edu_map = {
        "No degree": 0, "High School": 1, "Associate": 2,
        "Bachelor": 3, "Master": 4, "PhD": 5
    }
    df["education_required_ord"] = df["education_required"].map(
        lambda x: edu_map.get(str(x).title(), np.nan)
    )

# Zamiana skills na cechy binarne (dla top 10 najczęstszych)
if "required_skills" in df.columns:
    skills = df["required_skills"].dropna().str.lower().str.split(",")
    all_skills = [s.strip() for sublist in skills for s in sublist]
    top_skills = pd.Series(all_skills).value_counts().head(10).index
    for skill in top_skills:
        df["skill_" + skill.replace(" ", "_")] = df["required_skills"].str.contains(skill, case=False).astype(int)

# --- Zapis gotowego zbioru ---
df.to_csv(output_path, index=False)
print("Zapisano do:", output_path)
print("Zakonczono.")
