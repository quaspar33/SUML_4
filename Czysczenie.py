# Czyszczenie, kodowanie i usuwanie wartości odstających

import pandas as pd
import numpy as np
from pathlib import Path

data_path = Path("data/ai_job_dataset.csv")
output_path = Path("data/ai_job_dataset_clean.csv")

# Wczytanie danych
df = pd.read_csv(data_path)
print("Dane wczytane:", df.shape)

# Usunięcie białych znaków
obj_cols = df.select_dtypes(include=["object"]).columns
for col in obj_cols:
    df[col] = df[col].str.strip()

# Konwersja dat
for col in ["posting_date", "application_deadline"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

# Normalizacja remote_ratio
if "remote_ratio" in df.columns:
    df["remote_ratio"] = pd.to_numeric(df["remote_ratio"], errors="coerce").clip(0, 100)
    df["remote_ratio"] = df["remote_ratio"].apply(lambda x: min([0, 50, 100], key=lambda v: abs(v - x)))

# Usuwanie wartości odstających (IQR)
def remove_outliers_iqr(data, cols):
    clean_data = data.copy()
    for col in cols:
        Q1 = clean_data[col].quantile(0.25)
        Q3 = clean_data[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        before = len(clean_data)
        clean_data = clean_data[(clean_data[col] >= lower) & (clean_data[col] <= upper)]
        after = len(clean_data)
        if before != after:
            print(f"Usunięto {before - after} odstających rekordów z kolumny {col}")
    return clean_data

num_cols_for_outliers = [
    col for col in ["salary_usd", "salary_local", "years_experience", "benefits_score", "job_description_length"]
    if col in df.columns
]
df = remove_outliers_iqr(df, num_cols_for_outliers)

# Kodowanie kategorycznych
encode_cols = ["job_title", "job_category", "industry", "company_location", "employee_residence"]
for col in encode_cols:
    if col in df.columns:
        df[col + "_num"] = df[col].astype("category").cat.codes

# One-Hot Encoding
onehot_cols = ["experience_level", "employment_type", "company_size", "education_required"]
df = pd.get_dummies(df, columns=[c for c in onehot_cols if c in df.columns], prefix_sep="_", dtype=int)

# Wartości porządkowe
if "company_size" in df.columns:
    df["company_size_ord"] = df["company_size"].map({"S": 0, "M": 1, "L": 2})

if "education_required" in df.columns:
    edu_map = {
        "No degree": 0, "High School": 1, "Associate": 2,
        "Bachelor": 3, "Master": 4, "PhD": 5
    }
    df["education_required_ord"] = df["education_required"].map(
        lambda x: edu_map.get(str(x).title(), np.nan)
    )

# Top 10 najczęstszych umiejętności
if "required_skills" in df.columns:
    skills = df["required_skills"].dropna().str.lower().str.split(",")
    all_skills = [s.strip() for sublist in skills for s in sublist]
    top_skills = pd.Series(all_skills).value_counts().head(10).index
    for skill in top_skills:
        df["skill_" + skill.replace(" ", "_")] = df["required_skills"].str.contains(skill, case=False).astype(int)

# Zapis wyniku
df.to_csv(output_path, index=False)
print("Zapisano do:", output_path)