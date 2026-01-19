# app.py

import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
import sys

# Konfiguracja strony
st.set_page_config(page_title="AI Salaries – Professional", page_icon="💼", layout="wide")

# Ustawienie ścieżek dla modułów
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

BASE_DIR = Path(__file__).resolve().parent

# Import konektora
try:
    from connector.Connector import predict_salary, inverse_salary_search, salary_grid
except Exception as e:
    st.error(f"Błąd importu konektora: {e}")
    predict_salary = inverse_salary_search = salary_grid = None

# --- STYLE CSS ---
st.markdown(
    """
    <style>
      .main .block-container { max-width: 1200px; }
      .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
      .stTabs [data-baseweb="tab"] { padding: 10px 16px; border-radius: 12px; }
      .small-note { color:#666; font-size:0.9rem; }
      .muted { color:#6c757d; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- TŁUMACZENIA ---
LANGUAGES = {
    "PL": {
        "nav_title": "Nawigacja",
        "nav_labels": {
            "home": "Strona główna", "app": "Aplikacja", "cleaning": "Czyszczenie danych",
            "analysis": "Analiza modelu", "models_results": "Wyniki modeli"
        },
        "mock_toggle": "Użyj mocka (awaryjnie)",
        "mock_help": "Gdy model nie jest dostępny lub chcesz testować UI bez modelu.",
        "home_title": "AI Salaries – system predykcji",
        "home_desc": "Aplikacja do predykcji wynagrodzeń na podstawie cech oferty pracy przy użyciu modeli Machine Learning.",
        "app_title": "Aplikacja",
        "tab_pred": "Predykcja", "tab_inverse": "Celowane wynagrodzenie", "tab_grid": "Warianty (grid)",
        "form_intro": "Uzupełnij cechy stanowiska, aby uzyskać predykcję salary_usd.",
        "job_title": "Stanowisko", "experience_level": "Poziom doświadczenia",
        "employment_type": "Typ zatrudnienia", "years_experience": "Lata doświadczenia",
        "education_required": "Wykształcenie", "company_location": "Lokalizacja firmy",
        "employee_residence": "Miejsce zamieszkania", "company_size": "Wielkość firmy",
        "remote_ratio": "Udział pracy zdalnej (%)", "benefits_score": "Ocena benefitów (5–10)",
        "industry": "Branża", "required_skills": "Wymagane umiejętności", "salary_currency": "Waluta",
        "form_submit": "Oblicz", "payload_header": "Payload (JSON)", "result_header": "Wynik predykcji",
        "clean_title": "Czyszczenie i przygotowanie danych",
        "clean_md": "Proces czyszczenia obejmuje normalizację, usuwanie outlierów i kodowanie cech.",
        "analysis_title": "Analiza wizualna", "analysis_select": "Wybierz wykresy:",
        "source": "Źródło danych:", "backend_error": "Błąd backendu:",
        "inverse_intro": "Podaj docelowe wynagrodzenie, aby znaleźć pasujące konfiguracje.",
        "target_salary": "Docelowe wynagrodzenie (USD)", "inverse_submit": "Szukaj",
        "grid_submit": "Generuj grid", "footer": "System AI Salaries © 2026",
        "file_missing": "Nie znaleziono pliku:", "folder_missing": "Folder nie istnieje:"
    },
    "EN": {
        "nav_title": "Navigation",
        "nav_labels": {
            "home": "Home", "app": "Application", "cleaning": "Data Cleaning",
            "analysis": "Model Analysis", "models_results": "Models Results"
        },
        "mock_toggle": "Use mock (fallback)",
        "mock_help": "Use if model is unavailable or for UI testing.",
        "home_title": "AI Salaries – Prediction System",
        "home_desc": "Streamlit app for salary prediction using ML models.",
        "app_title": "Application",
        "tab_pred": "Prediction", "tab_inverse": "Target Salary", "tab_grid": "Variants (Grid)",
        "form_intro": "Fill in job features to get salary_usd prediction.",
        "job_title": "Job Title", "experience_level": "Experience Level",
        "employment_type": "Employment Type", "years_experience": "Years of Experience",
        "education_required": "Education", "company_location": "Company Location",
        "employee_residence": "Residence", "company_size": "Company Size",
        "remote_ratio": "Remote Ratio (%)", "benefits_score": "Benefits Score",
        "industry": "Industry", "required_skills": "Skills", "salary_currency": "Currency",
        "form_submit": "Predict", "payload_header": "Payload", "result_header": "Prediction Result",
        "clean_title": "Data Cleaning & Preprocessing",
        "clean_md": "Steps include normalization, outlier removal, and encoding.",
        "analysis_title": "Model Analysis", "analysis_select": "Select charts:",
        "source": "Source:", "backend_error": "Backend Error:",
        "inverse_intro": "Enter target salary to find matching configurations.",
        "target_salary": "Target Salary (USD)", "inverse_submit": "Search",
        "grid_submit": "Compute Grid", "footer": "AI Salaries System © 2026",
        "file_missing": "File not found:", "folder_missing": "Folder not found:"
    }
}

# --- STATE ---
if "language" not in st.session_state: st.session_state.language = "PL"
if "page" not in st.session_state: st.session_state.page = "home"

# Sidebar
lang_choice = st.sidebar.selectbox("Language / Język", ["PL", "EN"],
                                   index=["PL", "EN"].index(st.session_state.language))
st.session_state.language = lang_choice
T = LANGUAGES[st.session_state.language]
NAV = T["nav_labels"]

# --- DANE STAŁE ---
ROLES = ["AI Research Scientist", "AI Software Engineer", "AI Specialist", "NLP Engineer", "AI Consultant",
         "AI Architect", "Principal Data Scientist", "Data Analyst"]
EXPERIENCE = ["Entry", "Mid", "Senior", "Principal", "Lead"]
EMPLOYMENT = ["FT", "PT", "Contract", "Intern"]
COMPANY_SIZE = ["S", "M", "L", "XL"]
EDU = ["None", "Bachelor", "Master", "PhD"]
INDUSTRY = ["Technology", "Finance", "Healthcare", "Retail", "Manufacturing", "Automotive", "Telecom", "Education",
            "Government"]
SKILLS = ["Python", "TensorFlow", "PyTorch", "NLP", "Computer Vision", "MLOps", "AWS", "GCP", "Azure", "SQL", "Spark"]
LOCATIONS = ["US", "PL", "UK", "DE", "FR", "CA", "IN", "Remote"]

# Nawigacja
nav_keys = ["home", "app", "cleaning", "analysis", "models_results"]
page_label = st.sidebar.radio(T["nav_title"], [NAV[k] for k in nav_keys], index=nav_keys.index(st.session_state.page))
label_to_key = {v: k for k, v in NAV.items()}
st.session_state.page = label_to_key[page_label]

st.sidebar.markdown("---")
mock_toggle = st.sidebar.toggle(T["mock_toggle"], value=False, help=T["mock_help"])

# --- PAGE: HOME ---
if st.session_state.page == "home":
    st.title(T["home_title"])
    st.write(T["home_desc"])
    st.info("Użyj paska bocznego, aby przejść do aplikacji lub analizy danych.")

# --- PAGE: APP ---
if st.session_state.page == "app":
    st.title(T["app_title"])
    tab_pred, tab_inverse, tab_grid = st.tabs([T["tab_pred"], T["tab_inverse"], T["tab_grid"]])

    with tab_pred:
        st.markdown(T["form_intro"])
        with st.form("pred_form"):
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
                "job_title": job_title, "salary_currency": salary_currency,
                "experience_level": experience_level, "employment_type": employment_type,
                "company_location": company_location, "company_size": company_size,
                "employee_residence": employee_residence, "remote_ratio": remote_ratio,
                "required_skills": required_skills, "education_required": education_required,
                "years_experience": years_experience, "industry": industry,
                "benefits_score": float(benefits_score), "company_name": "Unknown",
                "job_description_length": 0,
            }
            st.subheader(T["payload_header"])
            st.json(payload, expanded=False)

            resp = predict_salary(payload, use_mock=mock_toggle)
            if resp.get("status") == "ok":
                est = float(resp["prediction"]["salary_usd"])
                st.subheader(T["result_header"])
                st.success(f"${est:,.2f}")
                st.caption(f"{T['source']} {resp.get('meta', {}).get('source', 'backend')}")
            else:
                st.error(f"{T['backend_error']} {resp.get('error', 'Unknown')}")

    with tab_inverse:
        st.markdown(T["inverse_intro"])
        with st.form("inverse_form"):
            target = st.number_input(T["target_salary"], 20000, 400000, 150000, 5000)
            with st.expander("Filtry", expanded=False):
                inv_roles = st.multiselect(T["job_title"], ROLES)
                inv_exp = st.multiselect(T["experience_level"], EXPERIENCE)
            inv_submit = st.form_submit_button(T["inverse_submit"])

        if inv_submit:
            constraints = {"job_title": inv_roles or None, "experience_level": inv_exp or None}
            resp = inverse_salary_search(target, constraints=constraints, use_mock=mock_toggle, top_n=10)
            if resp.get("status") == "ok":
                st.dataframe(pd.DataFrame(resp.get("solutions", [])), use_container_width=True)
            else:
                st.error(T["backend_error"])

    with tab_grid:
        st.markdown("Generuj wiele wariantów jednocześnie.")
        with st.form("grid_form"):
            g_roles = st.multiselect(T["job_title"], ROLES, default=ROLES[:2])
            g_exp = st.multiselect(T["experience_level"], EXPERIENCE, default=["Senior"])
            g_submit = st.form_submit_button(T["grid_submit"])

        if g_submit:
            spec = {"job_title": g_roles, "experience_level": g_exp}
            base = {"employment_type": "FT", "education_required": "Master", "company_location": "US",
                    "benefits_score": 7.5, "salary_currency": "USD"}
            resp = salary_grid(spec, base, use_mock=mock_toggle)
            if resp.get("status") == "ok":
                st.dataframe(pd.DataFrame(resp.get("rows", [])), use_container_width=True)

# --- PAGE: CLEANING ---
if st.session_state.page == "cleaning":
    st.title(T["clean_title"])
    st.markdown(T["clean_md"])
    cleaned_path = BASE_DIR / "Data" / "clean_data" / "ai_job_dataset_clean.csv"
    if cleaned_path.exists():
        st.dataframe(pd.read_csv(cleaned_path).head(30), use_container_width=True)
    else:
        st.info(f"{T['file_missing']} {cleaned_path}")

# --- PAGE: ANALYSIS ---
if st.session_state.page == "analysis":
    st.title(T["analysis_title"])
    charts_dir = BASE_DIR / "plots" / "etap0"
    if charts_dir.exists():
        images = sorted(list(charts_dir.glob("*.png")))
        selected = st.multiselect(T["analysis_select"], [f.stem for f in images], default=[f.stem for f in images])
        for img_p in images:
            if img_p.stem in selected:
                st.subheader(img_p.stem.replace("_", " ").title())
                st.image(Image.open(img_p), use_container_width=True)
    else:
        st.warning(T["folder_missing"])

# --- PAGE: MODELS ---
if st.session_state.page == "models_results":
    st.title("Wyniki Modelu")
    m_path = BASE_DIR / "Data" / "models_scores" / "models.csv"
    if m_path.exists():
        st.dataframe(pd.read_csv(m_path), use_container_width=True)

# Footer
st.markdown("---")
st.markdown(f"<span class='muted'>{T['footer']}</span>", unsafe_allow_html=True)
