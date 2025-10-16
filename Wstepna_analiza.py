# === ETAP 0: Podstawowa analiza danych (przed obróbką) ===

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --- Ścieżki ---
data_path = Path("data/ai_job_dataset.csv")
plots_dir = Path("plots/etap0")
plots_dir.mkdir(parents=True, exist_ok=True)

# --- Wczytanie danych ---
df = pd.read_csv(data_path)
print(f"Liczba wierszy: {df.shape[0]}, liczba kolumn: {df.shape[1]}\n")

# --- Podstawowe informacje ---
print("Podgląd danych:")
print(df.head(10))

print("\n Typ danych:")
print(df.info())

print("\nStatystyki opisowe (numeryczne):")
print(df.describe())

print("\nLista kolumn:")
print(df.columns.tolist())

# --- Identyfikacja typów danych ---
num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

print("\nKolumny numeryczne:", num_cols)
print("Kolumny kategoryczne:", cat_cols)

# --- Sprawdzenie braków danych ---
missing = df.isnull().sum().sort_values(ascending=False)
missing_ratio = (missing / len(df)).round(3)
missing_table = pd.DataFrame({'Braki': missing, 'Udział (%)': missing_ratio * 100})
print("\n Braki danych:")
print(missing_table.head(20))

# --- Wykres braków danych ---
plt.figure(figsize=(10, 6))
missing_ratio.head(20).plot(kind='bar', color='tomato')
plt.title('Odsetek braków danych')
plt.ylabel('Odsetek braków [%]')
plt.tight_layout()
plt.savefig(plots_dir / 'missing_values_initial.png')
plt.close()

# --- Rozkłady wybranych zmiennych numerycznych ---
for col in ['salary_usd', 'salary_local', 'years_experience', 'job_description_length', 'benefits_score']:
    if col in df.columns:
        plt.figure(figsize=(8, 5))
        sns.histplot(df[col].dropna(), kde=True, bins=30)
        plt.title(f'Rozkład wartości: {col}')
        plt.xlabel(col)
        plt.tight_layout()
        plt.savefig(plots_dir / f'{col}_hist.png')
        plt.close()

# --- Rozkłady zmiennych kategorycznych ---
for col in ['experience_level', 'employment_type', 'company_size', 'remote_ratio']:
    if col in df.columns:
        plt.figure(figsize=(7, 4))
        sns.countplot(x=df[col])
        plt.title(f'Rozkład kategorii: {col}')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(plots_dir / f'{col}_count.png')
        plt.close()

# --- Korelacja między zmiennymi numerycznymi ---
if len(num_cols) > 1:
    plt.figure(figsize=(10, 8))
    corr = df[num_cols].corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Macierz korelacji cech numerycznych')
