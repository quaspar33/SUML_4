import streamlit as st
import pandas as pd
from datetime import date
import itertools

# USTAWIENIA APLIKACJI
st.set_page_config(
    page_title="AI Salaries – Demo",
    page_icon="",
    layout="wide",
)

# --- styl (mock UI) ---
st.markdown(
    """
    <style>
      .main .block-container { max-width: 1200px; }
      .stTabs [data-baseweb=\"tab-list\"] { gap: 0.5rem; }
      .stTabs [data-baseweb=\"tab\"] { padding: 10px 16px; border-radius: 12px; }
      .st-emotion-cache-ue6h4q p, .st-emotion-cache-1vbkxwb p { font-size: 0.99rem; }
      .small-note { color:#666; font-size:0.9rem; }
      .pill { display:inline-block; padding:2px 8px; border-radius:999px; background:#f1f3f5; margin-right:6px; }
      .muted { color:#6c757d; }
    </style>
    """,
    unsafe_allow_html=True,
)

# DANE POMOCNICZE (mock)
ROLES = [
    "AI Research Scientist",
    "AI Software Engineer",
    "AI Specialist",
    "NLP Engineer",
    "AI Consultant",
    "AI Architect",
    "Principal Data Scientist",
    "Data Analyst",
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

# NAWIGACJA – PASEK BOCZNY
st.sidebar.title("AI Salaries Demo")
page = st.sidebar.radio(
    "Nawigacja",
    ["Strona główna", "Aplikacja"],
    index=0,
)

st.sidebar.markdown("---")
mock_toggle = st.sidebar.toggle("Użyj mocka (brak backendu)", value=True,
                                help="Gdy nie ma jeszcze gotowych endpointów backendu, pokaż przykładowe wyniki.")

# STRONA GŁÓWNA
if page == "Strona główna":
    st.title(" AI Salaries – demo frontendu")
    st.write(
        "To jest **mockup** aplikacji do predykcji wynagrodzeń na rynku AI. "
        "Interfejs pozwala przewidywać zarobki na podstawie cech oferty oraz sprawdzać, jakie konfiguracje cech sprzyjają osiągnięciu zadanego poziomu pensji."
    )

    with st.container():
        col1, col2 = st.columns([1.1, 0.9], gap="large")
        with col1:
            st.subheader(" Przepływy użytkownika")
            st.markdown(
                """
                1. **Predykcja wynagrodzenia** – użytkownik podaje cechy oferty/stanowiska → dostaje przewidywane `salary_usd`.
                2. **Celowane wynagrodzenie** – użytkownik podaje *docelowe* `salary_usd` i opcjonalne cechy →
                   dostaje propozycje konfiguracji cech, z którymi takie wynagrodzenie jest możliwe.
                3. **Warianty** – użytkownik podaje zestaw możliwych wartości (lub zostawia puste) dla kilku pól →
                   aplikacja liczy przewidywane wynagrodzenia dla wszystkich kombinacji.
                """
            )
        with col2:
            st.subheader("ℹ Informacja")
            st.markdown(
                "To wersja pokazowa interfejsu użytkownika. Wyniki mogą być generowane w trybie demo (mock)."
            )

# MOCK PREDYKCJI

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

# APLIKACJA

if page == "Aplikacja":
    st.title("⚙Aplikacja")
    tab_pred, tab_inverse, tab_grid = st.tabs([
        " Predykcja wynagrodzenia",
        " Jak osiągnąć podane wynagrodzenie?",
        " Warianty (wiele kombinacji)",
    ])

    # TAB 1: Predykcja wynagrodzenia
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
                salary_currency = st.selectbox("Waluta wynagrodzenia", ["USD"])  # uproszczenie

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

            # BACKEND: wywołanie najlepiej endpointa predykcji (np. POST /predict)
            if mock_toggle:
                est = _estimate_salary_mock(
                    job_title, experience_level, remote_ratio,
                    education_required, company_size, required_skills, benefits_score
                )
                st.success(f" **Predykcja (mock):** ${est:,}")
                st.caption("To tylko symulacja po stronie frontendu**.")

    # TAB 2: Jak osiągnąć podane wynagrodzenie?
    with tab_inverse:
        st.markdown(
            "Wprowadź docelowe wynagrodzenie w USD oraz (opcjonalnie) wybrane parametry. \n"
            "Zwrócimy przykładowe konfiguracje cech, przy których takie wynagrodzenie jest możliwe."
        )

        with st.form("inverse_form", clear_on_submit=False):
            target_salary = st.number_input("Docelowe wynagrodzenie (USD)", min_value=30_000, max_value=500_000, value=140_000, step=1_000)

            c1, c2, c3 = st.columns(3)
            with c1:
                i_job_title = st.selectbox("Stanowisko (opcjonalnie)", ["(dowolne)"] + ROLES)
                i_experience = st.selectbox("Doświadczenie (opcjonalnie)", ["(dowolne)"] + EXPERIENCE)
                i_employment = st.selectbox("Typ zatrudnienia (opcjonalnie)", ["(dowolny)"] + EMPLOYMENT)
            with c2:
                i_company_loc = st.selectbox("Lokalizacja firmy (opcjonalnie)", ["(dowolna)"] + LOCATIONS)
                i_company_size = st.selectbox("Wielkość firmy (opcjonalnie)", ["(dowolna)"] + COMPANY_SIZE)
                i_remote = st.slider("Udział pracy zdalnej (opcjonalnie)", 0, 100, 50, step=5)
            with c3:
                i_edu = st.selectbox("Wykształcenie (opcjonalnie)", ["(dowolne)"] + EDU)
                i_years = st.number_input("Lata doświadczenia (opcjonalnie)", 0, 40, 5)
                i_benefits = st.slider("Ocena benefitów (opcjonalnie)", 5.0, 10.0, 7.5, step=0.1)

            i_skills = st.multiselect("Umiejętności (opcjonalnie)", SKILLS)
            i_industry = st.selectbox("Branża (opcjonalnie)", ["(dowolna)"] + INDUSTRY)

            inverse_submitted = st.form_submit_button(" Pokaż możliwe konfiguracje")

        if inverse_submitted:
            constraints = {
                "target_salary_usd": target_salary,
                "job_title": None if i_job_title.startswith("(") else i_job_title,
                "experience_level": None if i_experience.startswith("(") else i_experience,
                "employment_type": None if i_employment.startswith("(") else i_employment,
                "company_location": None if i_company_loc.startswith("(") else i_company_loc,
                "company_size": None if i_company_size.startswith("(") else i_company_size,
                "remote_ratio": i_remote,
                "education_required": None if i_edu.startswith("(") else i_edu,
                "years_experience": i_years,
                "benefits_score": float(i_benefits),
                "required_skills": i_skills or None,
                "industry": None if i_industry.startswith("(") else i_industry,
            }

            st.subheader(" Wejście do wyszukiwania konfiguracji (constraints)")
            st.json(constraints, expanded=False)

            # BACKEND: wywołanie najlepiej endpointa *odwrotnej* analizy/eksplainer ( POST /inverse)
            if mock_toggle:
                examples = [
                    {
                        "job_title": constraints["job_title"] or "AI Architect",
                        "experience_level": constraints["experience_level"] or "Senior",
                        "employment_type": constraints["employment_type"] or "FT",
                        "company_location": constraints["company_location"] or "US",
                        "company_size": constraints["company_size"] or "L",
                        "remote_ratio": constraints["remote_ratio"],
                        "education_required": constraints["education_required"] or "Master",
                        "years_experience": constraints["years_experience"],
                        "industry": constraints["industry"] or "Technology",
                        "required_skills": ", ".join(constraints["required_skills"] or ["Python", "PyTorch", "MLOps"]),
                        "benefits_score": constraints["benefits_score"],
                        "salary_usd (est.)": f"${target_salary:,}",
                        "dopasowanie": "wysokie",
                    },
                    {
                        "job_title": constraints["job_title"] or "NLP Engineer",
                        "experience_level": constraints["experience_level"] or "Lead",
                        "employment_type": constraints["employment_type"] or "FT",
                        "company_location": constraints["company_location"] or "UK",
                        "company_size": constraints["company_size"] or "XL",
                        "remote_ratio": constraints["remote_ratio"],
                        "education_required": constraints["education_required"] or "PhD",
                        "years_experience": max(0, constraints["years_experience"] - 1),
                        "industry": constraints["industry"] or "Finance",
                        "required_skills": ", ".join(constraints["required_skills"] or ["Python", "NLP", "AWS"]),
                        "benefits_score": max(5.0, min(10.0, constraints["benefits_score"] + 0.3)),
                        "salary_usd (est.)": f"${int(target_salary*1.03):,}",
                        "dopasowanie": "średnie",
                    },
                    {
                        "job_title": constraints["job_title"] or "AI Software Engineer",
                        "experience_level": constraints["experience_level"] or "Mid",
                        "employment_type": constraints["employment_type"] or "Contract",
                        "company_location": constraints["company_location"] or "DE",
                        "company_size": constraints["company_size"] or "M",
                        "remote_ratio": constraints["remote_ratio"],
                        "education_required": constraints["education_required"] or "Bachelor",
                        "years_experience": max(0, constraints["years_experience"] - 2),
                        "industry": constraints["industry"] or "Automotive",
                        "required_skills": ", ".join(constraints["required_skills"] or ["Python", "TensorFlow", "GCP"]),
                        "benefits_score": max(5.0, min(10.0, constraints["benefits_score"] - 0.2)),
                        "salary_usd (est.)": f"${int(target_salary*0.97):,}",
                        "dopasowanie": "wstępne",
                    },
                ]
                df = pd.DataFrame(examples)
                st.dataframe(df, use_container_width=True)
                st.caption("Symulacyjne przykłady.")

    # TAB 3: Warianty – wiele kombinacji (grid)
    with tab_grid:
        st.markdown("Zdefiniuj *zestaw wartości* dla wybranych pól (lub zostaw puste), aby policzyć przewidywane wynagrodzenia dla wszystkich kombinacji.")

        with st.form("grid_form", clear_on_submit=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                g_job_titles = st.multiselect("Stanowiska (puste = wszystkie)", ROLES)
                g_experience = st.multiselect("Poziomy doświadczenia (puste = wszystkie)", EXPERIENCE)
                g_company_sizes = st.multiselect("Wielkości firm (puste = wszystkie)", COMPANY_SIZE)
            with c2:
                g_locations = st.multiselect("Lokalizacje firm (puste = wszystkie)", LOCATIONS)
                g_education = st.multiselect("Wykształcenie (puste = wszystkie)", EDU)
                g_remote_min, g_remote_max = st.slider("Zakres pracy zdalnej (%)", 0, 100, (40, 80), step=5)
            with c3:
                g_skills = st.multiselect("Umiejętności (liczone jako zestaw bazowy)", SKILLS, default=["Python", "SQL"])
                g_benefits = st.slider("Ocena benefitów", 5.0, 10.0, 7.5, step=0.1)
                g_currency = st.selectbox("Waluta", ["USD"])

            g_years = st.number_input("Lata doświadczenia (jedna wartość)", 0, 40, 3)
            g_industry = st.selectbox("Branża (jedna wartość)", INDUSTRY)
            g_employment = st.selectbox("Typ zatrudnienia (jedna wartość)", EMPLOYMENT)

            max_rows = st.number_input("Limit kombinacji", 1, 2000, 200)
            grid_submit = st.form_submit_button("Oblicz wszystkie kombinacje")

        if grid_submit:
            titles = g_job_titles or ROLES
            exps = g_experience or EXPERIENCE
            sizes = g_company_sizes or COMPANY_SIZE
            locs = g_locations or LOCATIONS
            edus = g_education or EDU
            # Dyskretyzacja zakresu remote co 10 p.p.
            remotes = list(range(g_remote_min, g_remote_max + 1, 10)) or [50]

            combos = list(itertools.product(titles, exps, sizes, locs, edus, remotes))
            if len(combos) > max_rows:
                st.warning(f"Dużo kombinacji: {len(combos)}. Pokazuję pierwsze {int(max_rows)}.")
                combos = combos[: int(max_rows)]

            records = []
            for jt, xp, sz, loc, edu in [(c[0], c[1], c[2], c[3], c[4]) for c in combos]:
                # Wyciągane remote z odpowiadającego tuple
                remote = combos[records.__len__()][5]
                # BACKEND: tutaj predict
                if mock_toggle:
                    est = _estimate_salary_mock(jt, xp, remote, edu, sz, g_skills, g_benefits)
                else:
                    est = None  # wynik z backendu
                records.append({
                    "job_title": jt,
                    "experience_level": xp,
                    "company_size": sz,
                    "company_location": loc,
                    "education_required": edu,
                    "remote_ratio": remote,
                    "skills(bazowe)": ", ".join(g_skills),
                    "benefits_score": g_benefits,
                    "employment_type": g_employment,
                    "years_experience": g_years,
                    "industry": g_industry,
                    "salary_usd (est.)": est,
                })

            out_df = pd.DataFrame(records)
            st.dataframe(out_df, use_container_width=True)
            st.caption("Wyniki na podstawie wszystkich kombinacji wybranych pól. Dla demo.")

    st.markdown("---")
    st.markdown(
        """
        <span class=\"muted\">Wersja demo. Miejsca integracji z backendem oznaczone w kodzie jako <code># BACKEND:</code>.</span>
        """,
        unsafe_allow_html=True,
    )
