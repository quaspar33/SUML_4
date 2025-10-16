import pandas as pd
import numpy as np

df = pd.read_csv('data/ai_job_dataset.csv')
print(df.head)
df.info()
df.describe()
df.columns

num_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

print(num_cols)
print(cat_cols)

df.isnull().sum().sort_values(ascending=False).head(20)

import matplotlib.pyplot as plt
import seaborn as sns

num_cols = df.select_dtypes(include=['int64', 'float64']).columns

plt.figure(figsize=(16, len(num_cols) * 4))

for i, col in enumerate(num_cols, 1):
    plt.subplot(len(num_cols), 2, i)
    sns.histplot(df[col].dropna(), bins=30, kde=True)
    plt.title(f'Histogram: {col}')
    plt.xlabel(col)
    plt.ylabel('Liczba wystąpień')

plt.tight_layout()
plt.show()
#
# corr_value = df['salary_usd'].corr(df['experience_years'], method='pearson')
# print(f"Korelacja salary_usd vs experience_years: {corr_value:.2f}")
# plt.figure(figsize=(8, 6))
# sns.scatterplot(data=df, x='experience_years', y='salary_usd', alpha=0.6)
# sns.regplot(data=df, x='experience_years', y='salary_usd', scatter=False, color='red')
# plt.title(f"Korelacja salary_usd vs experience_years (r = {corr_value:.2f})")
# plt.xlabel("Liczba lat doświadczenia")
# plt.ylabel("Wynagrodzenie (USD)")
# plt.grid(True)
# plt.show()
