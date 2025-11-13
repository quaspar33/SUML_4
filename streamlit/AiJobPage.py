import streamlit as st
import pandas as pd
import itertools
from datetime import date
from pathlib import Path
from PIL import Image
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


# -------------------------------------
# ⚙️ USTAWIENIA APLIKACJI
# -------------------------------------
st.set_page_config(
    page_title="AI Salaries – Demo",
    page_icon="🤖",
    layout="wide",
)

# --- styl (mock UI) ---
st.markdown(
    """
    <style>
      .main .block-container { max-width: 1200px; }
      .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
      .stTabs [data-baseweb="tab"] { padding: 10px 16px; border-radius: 12px; }
      .st-emotion-cache-ue6h4q p, .st-emotion-cache-1vbkxwb p { font-size: 0.99rem; }
      .small-note { color:#666; font-size:0.9rem; }
      .pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#f1f3f5; margin-right:6px; }
      .muted { color:#6c757d; }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------
# 📋 DANE POMOCNICZE (mock)
# -------------------------------------
ROLES = [
    "AI Research Scientist", "AI Software Engineer", "AI Specialist",
    "NLP Engineer", "AI Consultant", "AI Architect",
    "Principal Data Scientist", "Data Analyst",
]
EXPERIENCE = ["Entry", "Mid", "Senior", "Principal", "Lead"]
EMPLOYMENT = ["FT", "PT", "Contract", "Intern"]
COMPANY_SIZE = ["S", "M", "L", "XL"]
EDU = ["None", "Bachelor", "Master", "PhD"]
INDUSTRY = [
    "Technology", "Finance", "Healthcare", "Retail", "Manufacturing",
    "Automotive", "Telecom", "Education", "Government",
]
SKILLS = [
    "Python", "TensorFlow", "PyTorch", "NLP", "Computer Vision",
    "MLOps", "AWS", "GCP", "Azure", "SQL", "Spark",
]
LOCATIONS = ["US", "PL", "UK", "DE", "FR", "CA", "IN", "Remote"]

# -------------------------------------
# 🧭 NAWIGACJA – PASEK BOCZNY
# -------------------------------------
st.sidebar.title("AI Salaries Demo")
page = st.sidebar.radio(
    "Nawigacja",
    ["Strona główna", "Aplikacja", "Czyszczenie danych", "Analiza modelu"],
    index=0,
)

st.sidebar.markdown("---")
mock_toggle = st.sidebar.toggle(
    "Użyj mocka (brak backendu)",
    value=True,
    help="Gdy nie ma jeszcze gotowych endpointów backendu, pokaż przykładowe wyniki."
)

# -------------------------------------
# 🏠 STRONA GŁÓWNA
# -------------------------------------
if page == "Strona główna":
    st.title("🤖 AI Salaries – demo frontendu")
    st.write(
        "To jest **mockup** aplikacji do predykcji wynagrodzeń na rynku AI. "
        "Interfejs pozwala przewidywać zarobki na podstawie cech oferty oraz sprawdzać, "
        "jakie konfiguracje cech sprzyjają osiągnięciu zadanego poziomu pensji."
    )

    col1, col2 = st.columns([1.1, 0.9], gap="large")
    with col1:
        st.subheader("🔄 Przepływy użytkownika")
        st.markdown(
            """
            1. **Predykcja wynagrodzenia** – użytkownik podaje cechy oferty/stanowiska → dostaje przewidywane `salary_usd`.  
            2. **Celowane wynagrodzenie** – użytkownik podaje *docelowe* `salary_usd` → dostaje konfiguracje cech, które pozwalają osiągnąć taki poziom.  
            3. **Warianty** – użytkownik podaje zestaw wartości → aplikacja liczy przewidywane zarobki dla wszystkich kombinacji.
            """
        )
    with col2:
        st.subheader("ℹ️ Informacja")
        st.markdown("To wersja pokazowa interfejsu użytkownika. Wyniki mogą być generowane w trybie demo (mock).")

# -------------------------------------
# 🔮 MOCK FUNKCJA PREDYKCJI
# -------------------------------------
def _estimate_salary_mock(job_title: str, experience_level: str, remote_ratio: int,
                          education_required: str, company_size: str, required_skills: list,
                          benefits_score: float) -> int:
    base = {
        "AI Research Scientist": 155_000,
        "AI Software Engineer": 135_000,
        "AI Specialist": 120_000,
        "NLP Engineer": 140_000,
        "AI Consultant": 125_000,
        "AI Architect": 150_000,
        "Principal Data Scientist": 165_000,
        "Data Analyst": 95_000,
    }.get(job_title, 120_000)
    exp_boost = {"Entry": -0.15, "Mid": 0.0, "Senior": 0.25, "Principal": 0.45, "Lead": 0.4}[experience_level]
    remote_adj = 0.05 if remote_ratio >= 80 else (0.02 if remote_ratio >= 50 else 0.0)
    edu_adj = {"None": -0.05, "Bachelor": 0.0, "Master": 0.05, "PhD": 0.12}[education_required]
    size_adj = {"S": -0.03, "M": 0.0, "L": 0.03, "XL": 0.05}[company_size]
    skills_adj = min(len(required_skills) * 0.01, 0.08)
    benefits_adj = (benefits_score - 7.5) * 0.01
    est = base * (1 + exp_boost + remote_adj + edu_adj + size_adj + skills_adj + benefits_adj)
    return int(round(est, -2))

# -------------------------------------
# ⚙️ APLIKACJA (predykcja, odwrotna analiza, warianty)
# -------------------------------------
if page == "Aplikacja":
    st.title("⚙️ Aplikacja")
    tab_pred, tab_inverse, tab_grid = st.tabs([
        "Predykcja wynagrodzenia",
        "Jak osiągnąć podane wynagrodzenie?",
        "Warianty (wiele kombinacji)",
    ])

    # --- TAB 1: Predykcja ---
    with tab_pred:
        st.markdown("Podaj cechy stanowiska, aby obliczyć przewidywane wynagrodzenie (USD).")

        with st.form("pred_form", clear_on_submit=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                job_title = st.selectbox("Stanowisko", ROLES)
                experience_level = st.selectbox("Poziom doświadczenia", EXPERIENCE)
                employment_type = st.selectbox("Typ zatrudnienia", EMPLOYMENT)
                years_experience = st.number_input("Lata doświadczenia", 0, 40, 3)
                education_required = st.selectbox("Wykształcenie", EDU)
            with c2:
                company_location = st.selectbox("Lokalizacja firmy", LOCATIONS)
                employee_residence = st.selectbox("Miejsce zamieszkania", LOCATIONS)
                company_size = st.selectbox("Wielkość firmy", COMPANY_SIZE)
                remote_ratio = st.slider("Udział pracy zdalnej (%)", 0, 100, 50, step=5)
                benefits_score = st.slider("Ocena benefitów (5–10)", 5.0, 10.0, 7.5, step=0.1)
            with c3:
                industry = st.selectbox("Branża", INDUSTRY)
                required_skills = st.multiselect("Wymagane umiejętności", SKILLS, default=["Python", "SQL"])
                salary_currency = st.selectbox("Waluta wynagrodzenia", ["USD"])

            submitted = st.form_submit_button("Oblicz wynagrodzenie")

        if submitted:
            payload = {
                "job_title": job_title,
                "salary_currency": salary_currency,
                "experience_level": experience_level,
                "employment_type": employment_type,
                "company_location": company_location,
                "company_size": company_size,
                "employee_residence": employee_residence,
                "remote_ratio": remote_ratio,
                "required_skills": required_skills,
                "education_required": education_required,
                "years_experience": years_experience,
                "industry": industry,
                "benefits_score": float(benefits_score),
            }

            st.subheader("Wejście do predykcji (payload)")
            st.json(payload, expanded=False)

            if mock_toggle:
                est = _estimate_salary_mock(
                    job_title, experience_level, remote_ratio,
                    education_required, company_size, required_skills, benefits_score
                )
                st.success(f"**Predykcja (mock):** ${est:,}")
                st.caption("To tylko symulacja po stronie frontendu.")

# -------------------------------------
# 🧹 CZYSZCZENIE DANYCH
# -------------------------------------
if page == "Czyszczenie danych":
    st.title("🧹 Czyszczenie, kodowanie i usuwanie wartości odstających")

    st.markdown("""
    W tej sekcji opisano etapy przygotowania danych wejściowych dla modelu predykcji wynagrodzeń:
    1. **Usunięcie białych znaków** w kolumnach tekstowych  
    2. **Konwersja dat** do formatu `datetime`  
    3. **Normalizacja `remote_ratio`** do wartości {0, 50, 100}  
    4. **Usuwanie wartości odstających (IQR)**  
    5. **Kodowanie kategorycznych** (`.cat.codes`, One-Hot)  
    6. **Mapowanie wartości porządkowych** (`company_size`, `education_required`)  
    7. **Ekstrakcja top umiejętności** z kolumny `required_skills`  
    """)

    with st.expander("📄 Zobacz kod czyszczenia"):
        clean_script = BASE_DIR.parent / "Czysczenie.py"
        if clean_script.exists():
            st.code(open(clean_script).read(), language="python")
        else:
            st.warning(f"Nie znaleziono pliku: {clean_script}")

    cleaned_path = BASE_DIR.parent / "Data" / "ai_job_dataset_clean.csv"
    if cleaned_path.exists():
        df_clean = pd.read_csv(cleaned_path)
        st.subheader("📊 Podgląd wyczyszczonych danych")
        st.dataframe(df_clean.head(20), use_container_width=True)
    else:
        st.info(f"Plik `{cleaned_path.name}` nie został znaleziony.")

# -------------------------------------
# 📊 ANALIZA MODELU (z PNG)
# -------------------------------------
if page == "Analiza modelu":
    st.title("📊 Analiza modelu predykcji wynagrodzeń")

    st.markdown("""
    W tej sekcji prezentowane są wyniki i wizualizacje analizy modelu.  
    Wykresy pokazują m.in. rozkłady danych, korelacje, ważność cech oraz jakość predykcji.
    """)

    charts_dir = BASE_DIR.parent / "plots" / "etap0"

    if not charts_dir.exists():
        st.warning(f"Nie znaleziono folderu z wykresami: {charts_dir}")
    else:
        image_files = sorted(list(charts_dir.glob("*.png")))
        if not image_files:
            st.info("Brak plików PNG w folderze analizy modelu.")
        else:
            selected = st.multiselect(
                "Wybierz wykresy do wyświetlenia:",
                [f.stem for f in image_files],
                default=[f.stem for f in image_files]
            )

            for img_path in image_files:
                if img_path.stem in selected:
                    st.subheader(img_path.stem.replace("_", " ").title())
                    st.image(Image.open(img_path), use_container_width=True)
                    st.caption(f"Źródło: {img_path.name}")

# -------------------------------------
# 📘 STOPKA
# -------------------------------------
st.markdown("---")
st.markdown(
    "<span class='muted'>Wersja demo. Miejsca integracji z backendem oznaczone w kodzie jako "
    "<code># BACKEND:</code>.</span>",
    unsafe_allow_html=True,
)
