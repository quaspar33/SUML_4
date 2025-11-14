import streamlit as st
import pandas as pd
import itertools
from datetime import date
from pathlib import Path
from PIL import Image
import os

BASE_DIR = Path(__file__).resolve().parent

# -------------------------------------
# TRANSLATIONS (UX only)
# -------------------------------------
LANGUAGES = {
    "PL": {
        "nav_title": "Nawigacja",
        "nav_labels": {
            "home": "Strona główna",
            "app": "Aplikacja",
            "cleaning": "Czyszczenie danych",
            "analysis": "Analiza modelu",
        },
        "mock_toggle": "Użyj mocka (brak backendu)",
        "mock_help": "Gdy nie ma gotowych endpointów backendu, pokaż przykładowe wyniki.",
        "home_title": "AI Salaries – demo frontendu",
        "home_desc": "To jest **mockup** aplikacji do predykcji wynagrodzeń na rynku AI. "
                     "Interfejs pozwala przewidywać zarobki na podstawie cech oferty oraz sprawdzać, "
                     "jakie konfiguracje cech sprzyjają osiągnięciu zadanego poziomu pensji.",
        "home_flows": "Przepływy użytkownika",
        "home_flows_md": """
            1. **Predykcja wynagrodzenia** – użytkownik podaje cechy oferty/stanowiska → dostaje przewidywane `salary_usd`.  
            2. **Celowane wynagrodzenie** – użytkownik podaje *docelowe* `salary_usd` → dostaje konfiguracje cech, które pozwalają osiągnąć taki poziom.  
            3. **Warianty** – użytkownik podaje zestaw wartości → aplikacja liczy przewidywane zarobki dla wszystkich kombinacji.
        """,
        "info_header": "Informacja",
        "info_text": "To wersja pokazowa interfejsu użytkownika. Wyniki mogą być generowane w trybie demo (mock).",
        "app_title": "Aplikacja",
        "tab_pred": "Predykcja wynagrodzenia",
        "tab_inverse": "Jak osiągnąć podane wynagrodzenie?",
        "tab_grid": "Warianty (wiele kombinacji)",
        "form_intro": "Podaj cechy stanowiska, aby obliczyć przewidywane wynagrodzenie (USD).",
        "job_title": "Stanowisko",
        "experience_level": "Poziom doświadczenia",
        "employment_type": "Typ zatrudnienia",
        "years_experience": "Lata doświadczenia",
        "education_required": "Wykształcenie",
        "company_location": "Lokalizacja firmy",
        "employee_residence": "Miejsce zamieszkania",
        "company_size": "Wielkość firmy",
        "remote_ratio": "Udział pracy zdalnej (%)",
        "benefits_score": "Ocena benefitów (5–10)",
        "industry": "Branża",
        "required_skills": "Wymagane umiejętności",
        "salary_currency": "Waluta wynagrodzenia",
        "form_submit": "Oblicz wynagrodzenie",
        "payload_header": "Wejście do predykcji (payload)",
        "mock_result": "Predykcja (mock):",
        "mock_caption": "To tylko symulacja po stronie frontendu.",
        "clean_title": "Czyszczenie, kodowanie i usuwanie wartości odstających",
        "clean_md": """
        W tej sekcji opisano etapy przygotowania danych wejściowych dla modelu predykcji wynagrodzeń:
        1. Usunięcie białych znaków w kolumnach tekstowych  
        2. Konwersja dat do formatu `datetime`  
        3. Normalizacja `remote_ratio` do wartości {0, 50, 100}  
        4. Usuwanie wartości odstających (IQR)  
        5. Kodowanie kategorycznych (`.cat.codes`, One-Hot)  
        6. Mapowanie wartości porządkowych (`company_size`, `education_required`)  
        7. Ekstrakcja top umiejętności z kolumny `required_skills`
        """,
        "clean_code": "Zobacz kod czyszczenia",
        "clean_notfound": "Nie znaleziono pliku:",
        "clean_preview": "Podgląd wyczyszczonych danych",
        "clean_csv_missing": "Plik `{}` nie został znaleziony.",
        "analysis_title": "Analiza modelu predykcji wynagrodzeń",
        "analysis_md": """
        W tej sekcji prezentowane są wyniki i wizualizacje analizy modelu.  
        Wykresy pokazują m.in. rozkłady danych, korelacje, ważność cech oraz jakość predykcji.
        """,
        "analysis_folder_missing": "Nie znaleziono folderu z wykresami:",
        "analysis_no_png": "Brak plików PNG w folderze analizy modelu.",
        "analysis_select": "Wybierz wykresy do wyświetlenia:",
        "source": "Źródło:",
        "footer": "Wersja demo. Miejsca integracji z backendem oznaczone w kodzie jako <code># BACKEND:</code>."
    },
    "EN": {
        "nav_title": "Navigation",
        "nav_labels": {
            "home": "Home",
            "app": "Application",
            "cleaning": "Data Cleaning",
            "analysis": "Model Analysis",
        },
        "mock_toggle": "Use mock (no backend)",
        "mock_help": "Show sample results when backend endpoints are unavailable.",
        "home_title": "AI Salaries – frontend demo",
        "home_desc": "This is a **mockup** of an AI salary prediction app. "
                     "The interface allows you to predict salaries based on job attributes "
                     "and explore which configurations support specific salary levels.",
        "home_flows": "User Flows",
        "home_flows_md": """
            1. **Salary prediction** – the user provides job attributes → gets predicted `salary_usd`.  
            2. **Target salary** – the user specifies a *desired* `salary_usd` → gets feature configurations to reach it.  
            3. **Variants** – the user provides sets of values → the app computes predicted salaries for all combinations.
        """,
        "info_header": "Information",
        "info_text": "This is a demo version of the UI. Results may be mock-generated.",
        "app_title": "Application",
        "tab_pred": "Salary Prediction",
        "tab_inverse": "How to Reach Target Salary?",
        "tab_grid": "Variants (Multiple Combinations)",
        "form_intro": "Enter job features to estimate salary (USD).",
        "job_title": "Job Title",
        "experience_level": "Experience Level",
        "employment_type": "Employment Type",
        "years_experience": "Years of Experience",
        "education_required": "Education Required",
        "company_location": "Company Location",
        "employee_residence": "Employee Residence",
        "company_size": "Company Size",
        "remote_ratio": "Remote Ratio (%)",
        "benefits_score": "Benefits Score (5–10)",
        "industry": "Industry",
        "required_skills": "Required Skills",
        "salary_currency": "Salary Currency",
        "form_submit": "Estimate Salary",
        "payload_header": "Prediction Input (payload)",
        "mock_result": "Prediction (mock):",
        "mock_caption": "Frontend-only simulation.",
        "clean_title": "Cleaning, Encoding, and Outlier Removal",
        "clean_md": """
        This section describes preprocessing steps for salary prediction data:
        1. Strip whitespace in text columns  
        2. Convert dates to `datetime`  
        3. Normalize `remote_ratio` to {0, 50, 100}  
        4. Remove outliers (IQR)  
        5. Encode categorical (`.cat.codes`, One-Hot)  
        6. Map ordinal features (`company_size`, `education_required`)  
        7. Extract top skills from `required_skills`
        """,
        "clean_code": "View Cleaning Code",
        "clean_notfound": "File not found:",
        "clean_preview": "Preview of Cleaned Data",
        "clean_csv_missing": "File `{}` not found.",
        "analysis_title": "Model Analysis and Visualization",
        "analysis_md": """
        This section presents model evaluation and visualizations — 
        distributions, correlations, feature importance, and prediction quality.
        """,
        "analysis_folder_missing": "Charts folder not found:",
        "analysis_no_png": "No PNG charts found in the analysis folder.",
        "analysis_select": "Select charts to display:",
        "source": "Source:",
        "footer": "Demo version. Backend integration points marked with <code># BACKEND:</code>."
    }
}

# -------------------------------------
# LANGUAGE STATE
# -------------------------------------
if "language" not in st.session_state:
    st.session_state.language = "PL"
if "page" not in st.session_state:
    st.session_state.page = "home"

# Sidebar language switcher
lang_choice = st.sidebar.selectbox("Language / Język", ["PL", "EN"], index=["PL", "EN"].index(st.session_state.language))
if lang_choice != st.session_state.language:
    st.session_state.language = lang_choice

T = LANGUAGES[st.session_state.language]
NAV = T["nav_labels"]

# -------------------------------------
# APP SETTINGS
# -------------------------------------
st.set_page_config(page_title="AI Salaries – Demo", page_icon="💼", layout="wide")

# --- STYLE ---
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
# MOCK DATA
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
INDUSTRY = ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Automotive", "Telecom", "Education", "Government"]
SKILLS = ["Python", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "MLOps", "AWS", "GCP", "Azure", "SQL", "Spark"]
LOCATIONS = ["US", "PL", "UK", "DE", "FR", "CA", "IN", "Remote"]

# -------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------
nav_keys = ["home", "app", "cleaning", "analysis"]
page_label = st.sidebar.radio(T["nav_title"], [NAV[k] for k in nav_keys],
                              index=nav_keys.index(st.session_state.page))
label_to_key = {v: k for k, v in NAV.items()}
st.session_state.page = label_to_key[page_label]

st.sidebar.markdown("---")
mock_toggle = st.sidebar.toggle(T["mock_toggle"], value=True, help=T["mock_help"])

# -------------------------------------
# MOCK PREDICTION
# -------------------------------------
def _estimate_salary_mock(job_title, experience_level, remote_ratio,
                          education_required, company_size, required_skills, benefits_score):
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
    return int(round(base * (1 + exp_boost + remote_adj + edu_adj + size_adj + skills_adj + benefits_adj), -2))

# -------------------------------------
# HOME PAGE
# -------------------------------------
if st.session_state.page == "home":
    st.title(T["home_title"])
    st.write(T["home_desc"])
    col1, col2 = st.columns([1.1, 0.9], gap="large")
    with col1:
        st.subheader(T["home_flows"])
        st.markdown(T["home_flows_md"])
    with col2:
        st.subheader(T["info_header"])
        st.markdown(T["info_text"])

# -------------------------------------
# APPLICATION
# -------------------------------------
if st.session_state.page == "app":
    st.title(T["app_title"])
    tab_pred, tab_inverse, tab_grid = st.tabs([T["tab_pred"], T["tab_inverse"], T["tab_grid"]])
    with tab_pred:
        st.markdown(T["form_intro"])
        with st.form("pred_form", clear_on_submit=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                job_title = st.selectbox(T["job_title"], ROLES)
                experience_level = st.selectbox(T["experience_level"], EXPERIENCE)
                employment_type = st.selectbox(T["employment_type"], EMPLOYMENT)
                years_experience = st.number_input(T["years_experience"], 0, 40, 3)
                education_required = st.selectbox(T["education_required"], EDU)
            with c2:
                company_location = st.selectbox(T["company_location"], LOCATIONS)
                employee_residence = st.selectbox(T["employee_residence"], LOCATIONS)
                company_size = st.selectbox(T["company_size"], COMPANY_SIZE)
                remote_ratio = st.slider(T["remote_ratio"], 0, 100, 50, step=5)
                benefits_score = st.slider(T["benefits_score"], 5.0, 10.0, 7.5, step=0.1)
            with c3:
                industry = st.selectbox(T["industry"], INDUSTRY)
                required_skills = st.multiselect(T["required_skills"], SKILLS, default=["Python", "SQL"])
                salary_currency = st.selectbox(T["salary_currency"], ["USD"])
            submitted = st.form_submit_button(T["form_submit"])

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
            st.subheader(T["payload_header"])
            st.json(payload, expanded=False)
            if mock_toggle:
                est = _estimate_salary_mock(job_title, experience_level, remote_ratio,
                                            education_required, company_size, required_skills, benefits_score)
                st.success(f"**{T['mock_result']}** ${est:,}")
                st.caption(T["mock_caption"])

# -------------------------------------
# CLEANING
# -------------------------------------
if st.session_state.page == "cleaning":
    st.title(T["clean_title"])
    st.markdown(T["clean_md"])
    with st.expander(T["clean_code"]):
        clean_script = BASE_DIR.parent / "Czysczenie.py"
        if clean_script.exists():
            st.code(open(clean_script).read(), language="python")
        else:
            st.warning(f"{T['clean_notfound']} {clean_script}")
    cleaned_path = BASE_DIR.parent / "Data" / "ai_job_dataset_clean.csv"
    if cleaned_path.exists():
        df_clean = pd.read_csv(cleaned_path)
        st.subheader(T["clean_preview"])
        st.dataframe(df_clean.head(20), use_container_width=True)
    else:
        st.info(T["clean_csv_missing"].format(cleaned_path.name))

# -------------------------------------
# ANALYSIS
# -------------------------------------
if st.session_state.page == "analysis":
    st.title(T["analysis_title"])
    st.markdown(T["analysis_md"])
    charts_dir = BASE_DIR.parent / "plots" / "etap0"
    if not charts_dir.exists():
        st.warning(f"{T['analysis_folder_missing']} {charts_dir}")
    else:
        image_files = sorted(list(charts_dir.glob("*.png")))
        if not image_files:
            st.info(T["analysis_no_png"])
        else:
            selected = st.multiselect(T["analysis_select"], [f.stem for f in image_files],
                                      default=[f.stem for f in image_files])
            for img_path in image_files:
                if img_path.stem in selected:
                    st.subheader(img_path.stem.replace("_", " ").title())
                    st.image(Image.open(img_path), use_container_width=True)
                    st.caption(f"{T['source']} {img_path.name}")

# -------------------------------------
# FOOTER
# -------------------------------------
st.markdown("---")
st.markdown(f"<span class='muted'>{T['footer']}</span>", unsafe_allow_html=True)
