# app.py

import streamlit as st
import pandas as pd
from pathlib import Path
from PIL import Image
import sys

st.set_page_config(page_title="AI Salaries – Demo", page_icon="💼", layout="wide")

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from connector.Connector import predict_salary, inverse_salary_search, salary_grid
except Exception as e:
    print("DEBUG import connector FAILED")
    print("ROOT_DIR:", ROOT_DIR)
    print("sys.path:", sys.path)
    raise e

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
            "models_resutls": "Wyniki modeli"
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
        "model_title": "Wyniki modeli",
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
        "models_explained": """
        W tej sekcji przedstawiono logikę tworzenia i porównywania modeli predykcji wynagrodzeń używaną w aplikacji. Obecna implementacja korzysta z modelu, który wylicza pensję na podstawie zestawu cech oferty (stanowisko, doświadczenie, praca zdalna, wykształcenie, rozmiar firmy, umiejętności i benefity).
        Dodatkowo opisano dwa procesy analityczne:
        Inverse salary search – przeszukiwanie przestrzeni możliwych konfiguracji cech w celu znalezienia profili o wynagrodzeniu najbliższym wartości zadanej.
        Salary grid – generowanie siatki wariantów (grid search) i obliczanie przewidywanych wynagrodzeń dla każdej kombinacji parametrów.
        """,
        "clean_code": "Zobacz kod czyszczenia",
        "clean_notfound": "Nie znaleziono pliku:",
        "clean_preview": "Podgląd wyczyszczonych danych",
        "models_preview": "Podgląd wyników modeli",
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
        "footer": "Wersja demo. Miejsca integracji z backendem oznaczone w kodzie jako <code># BACKEND:</code>.",

        # --- NOWE TEKSTY DLA ZAKŁADEK 2 i 3 ---
        "inverse_intro": "Podaj docelowe wynagrodzenie oraz (opcjonalnie) ograniczenia cech, "
                         "aby zobaczyć konfiguracje sprzyjające takiej pensji.",
        "target_salary": "Docelowe wynagrodzenie (USD)",
        "inverse_filters_header": "Ograniczenia (opcjonalne)",
        "inverse_submit": "Znajdź konfiguracje",
        "inverse_results_header": "Proponowane konfiguracje stanowiska",
        "grid_intro": "Wybierz zestawy wartości, dla których chcesz policzyć wszystkie kombinacje "
                      "i przewidywane wynagrodzenia.",
        "grid_submit": "Policz kombinacje",
        "grid_results_header": "Wyniki dla wszystkich kombinacji",
        "backend_error": "Błąd podczas komunikacji z backendem:",
    },
    "EN": {
        "nav_title": "Navigation",
        "nav_labels": {
            "home": "Home",
            "app": "Application",
            "cleaning": "Data Cleaning",
            "analysis": "Model Analysis",
            "models_resutls": "Models Results"
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
        "model_title": "Models results",
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
        "models_explained": """
        This section explains the logic used to build and compare salary prediction models within the application. The current implementation uses a model that estimates salary based on job features such as job title, experience level, remote ratio, education, company size, skills, and benefits.
        The section also describes two analytical procedures:
        Inverse salary search – exploring the space of possible job configurations to find those whose predicted salary is closest to a target value.
        Salary grid – generating a parameter grid and computing salary predictions for every combination.
        """,
        "clean_code": "View Cleaning Code",
        "clean_notfound": "File not found:",
        "clean_preview": "Preview of Cleaned Data",
        "models_preview": "Preview of Models Results",
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
        "footer": "Demo version. Backend integration points marked with <code># BACKEND:</code>.",

        # --- NEW TEXTS ---
        "inverse_intro": "Provide a target salary and (optionally) feature constraints "
                         "to see configurations that support this level.",
        "target_salary": "Target salary (USD)",
        "inverse_filters_header": "Constraints (optional)",
        "inverse_submit": "Find configurations",
        "inverse_results_header": "Suggested job configurations",
        "grid_intro": "Select sets of values for which you want to compute all combinations "
                      "and predicted salaries.",
        "grid_submit": "Compute combinations",
        "grid_results_header": "Results for all combinations",
        "backend_error": "Backend error:",
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
# MOCK DATA (POZOSTAJE JAK BYŁO)
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
nav_keys = ["home", "app", "cleaning", "analysis", "models_resutls"]
page_label = st.sidebar.radio(T["nav_title"], [NAV[k] for k in nav_keys],
                              index=nav_keys.index(st.session_state.page))
label_to_key = {v: k for k, v in NAV.items()}
st.session_state.page = label_to_key[page_label]

st.sidebar.markdown("---")
mock_toggle = st.sidebar.toggle(T["mock_toggle"], value=True, help=T["mock_help"])

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

    # ----------------- TAB 1: PREDYKCA -----------------
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

            # BACKEND: predykcja wynagrodzenia
            resp = predict_salary(payload, use_mock=mock_toggle)
            if resp.get("status") == "ok":
                est = resp["prediction"]["salary_usd"]
                st.success(f"**{T['mock_result']}** ${est:,}")
                if resp.get("meta", {}).get("source") == "mock":
                    st.caption(T["mock_caption"])
            else:
                st.error(f"{T['backend_error']} {resp.get('error', 'Unknown error')}")

    # ----------------- TAB 2: INVERSE -----------------
    with tab_inverse:
        st.markdown(T["inverse_intro"])
        with st.form("inverse_form"):
            target_salary = st.number_input(T["target_salary"], min_value=20_000, max_value=400_000, value=150_000, step=5_000)

            with st.expander(T["inverse_filters_header"], expanded=False):
                c1, c2 = st.columns(2)
                with c1:
                    inv_roles = st.multiselect(T["job_title"], ROLES)
                    inv_exp = st.multiselect(T["experience_level"], EXPERIENCE)
                with c2:
                    inv_company_size = st.multiselect(T["company_size"], COMPANY_SIZE)
                    inv_remote_ratio = st.multiselect(T["remote_ratio"], [0, 50, 100])

            inverse_submit = st.form_submit_button(T["inverse_submit"])

        if inverse_submit:
            constraints = {
                "job_title": inv_roles or None,
                "experience_level": inv_exp or None,
                "company_size": inv_company_size or None,
                "remote_ratio": inv_remote_ratio or None,
            }

            # BACKEND: wyszukiwanie konfiguracji dla target salary
            resp = inverse_salary_search(target_salary, constraints=constraints, use_mock=mock_toggle)

            if resp.get("status") == "ok":
                solutions = resp.get("solutions", [])
                if solutions:
                    st.subheader(T["inverse_results_header"])
                    df_solutions = pd.DataFrame(solutions)
                    st.dataframe(df_solutions, use_container_width=True)
                    meta = resp.get("meta", {})
                    grid_size = meta.get("grid_size", None)
                    if grid_size:
                        st.caption(f"<span class='small-note'>Liczba sprawdzonych konfiguracji: {grid_size}</span>",
                                   unsafe_allow_html=True)
                else:
                    st.info("Brak konfiguracji spełniających kryteria.")
            else:
                st.error(f"{T['backend_error']} {resp.get('error', 'Unknown error')}")

    # ----------------- TAB 3: GRID -----------------
    with tab_grid:
        st.markdown(T["grid_intro"])

        with st.form("grid_form"):
            c1, c2 = st.columns(2)
            with c1:
                grid_roles = st.multiselect(T["job_title"], ROLES, default=ROLES[:2])
                grid_exp = st.multiselect(T["experience_level"], EXPERIENCE, default=["Senior"])
            with c2:
                grid_company_size = st.multiselect(T["company_size"], COMPANY_SIZE, default=["M", "L"])
                grid_remote_ratio = st.multiselect(T["remote_ratio"], [0, 50, 100], default=[0, 50, 100])

            st.markdown("---")
            st.markdown("<span class='small-note'>Poniżej możesz ustawić parametry wspólne dla wszystkich kombinacji.</span>",
                        unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            with c3:
                grid_employment_type = st.selectbox(T["employment_type"], EMPLOYMENT, index=0)
                grid_education = st.selectbox(T["education_required"], EDU, index=2)
            with c4:
                grid_company_location = st.selectbox(T["company_location"], LOCATIONS, index=0)
                grid_benefits = st.slider(T["benefits_score"], 5.0, 10.0, 7.5, step=0.1)

            grid_submit = st.form_submit_button(T["grid_submit"])

        if grid_submit:
            # Zabezpieczenie przed pustymi listami
            if not grid_roles or not grid_exp or not grid_company_size or not grid_remote_ratio:
                st.warning("Wybierz co najmniej jedną wartość w każdej z list (stanowisko, poziom, rozmiar firmy, udział zdalny).")
            else:
                grid_spec = {
                    "job_title": grid_roles,
                    "experience_level": grid_exp,
                    "company_size": grid_company_size,
                    "remote_ratio": grid_remote_ratio,
                }

                base_payload = {
                    "employment_type": grid_employment_type,
                    "education_required": grid_education,
                    "company_location": grid_company_location,
                    "employee_residence": grid_company_location,
                    "industry": "Technology",
                    "required_skills": ["Python", "SQL"],
                    "years_experience": 3,
                    "benefits_score": float(grid_benefits),
                    "salary_currency": "USD",
                }

                # BACKEND: liczenie siatki kombinacji
                resp = salary_grid(grid_spec, base_payload, use_mock=mock_toggle)

                if resp.get("status") == "ok":
                    rows = resp.get("rows", [])
                    if rows:
                        st.subheader(T["grid_results_header"])
                        df_grid = pd.DataFrame(rows)
                        st.dataframe(df_grid, use_container_width=True)
                        meta = resp.get("meta", {})
                        st.caption(
                            f"<span class='small-note'>Liczba kombinacji: {meta.get('grid_size', len(rows))}</span>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.info("Brak wyników dla podanych kombinacji.")
                else:
                    st.error(f"{T['backend_error']} {resp.get('error', 'Unknown error')}")

# -------------------------------------
# CLEANING
# -------------------------------------
if st.session_state.page == "cleaning":
    st.title(T["clean_title"])
    st.markdown(T["clean_md"])
    with st.expander(T["clean_code"]):
        clean_script = BASE_DIR / "Czysczenie.py"
        if clean_script.exists():
            st.code(open(clean_script).read(), language="python")
        else:
            st.warning(f"{T['clean_notfound']} {clean_script}")
    cleaned_path = BASE_DIR / "Data" / "clean_data" / "ai_job_dataset_clean.csv"
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
    charts_dir = BASE_DIR / "plots" / "etap0"
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
                    try:
                        img = Image.open(img_path)
                        try:
                            st.image(img, use_container_width=True)
                        except TypeError:
                            st.image(img, use_column_width=True)
                    except Exception as e:
                        st.error(f"Nie można załadować obrazu: {img_path.name}")
                        st.error(str(e))
                    st.caption(f"{T['source']} {img_path.name}")

# -------------------------------------
# MODELS
# -------------------------------------
if st.session_state.page == "models_resutls":
    st.title(T["model_title"])
    st.markdown(T["models_explained"])
    cleaned_path = BASE_DIR / "Data" / "models_scores" / "models.csv"
    if cleaned_path.exists():
        df_clean = pd.read_csv(cleaned_path)
        st.subheader(T["models_preview"])
        st.dataframe(df_clean.head(20), use_container_width=True)
    else:
        st.info(T["clean_csv_missing"].format(cleaned_path.name))

# -------------------------------------
# FOOTER
# -------------------------------------
st.markdown("---")
st.markdown(f"<span class='muted'>{T['footer']}</span>", unsafe_allow_html=True)
