# Connector.py
"""
Connector module for AI Salaries Streamlit app.

Zadania:
- Udostępnia proste funkcje, które wywołuje frontend (Streamlit)
- Na razie wszystko liczy lokalnie (mock), ale w jednym miejscu
  – tu później można podmienić logikę na prawdziwe API HTTP.

Funkcje:
- predict_salary(payload, use_mock=True)
- inverse_salary_search(target_salary, constraints, use_mock=True)
- salary_grid(grid_spec, base_payload, use_mock=True)
"""

from typing import Any, Dict, List, Optional
import itertools


# -------------------------------
# MOCK – logika predykcji
# -------------------------------

def _estimate_salary_mock(payload: Dict[str, Any]) -> int:
    """
    Prosta funkcja mockująca model ML.
    Bazuje na tym samym wzorze, który był w Streamlit (_estimate_salary_mock),
    ale oparta jest na słowniku payload.
    """
    job_title = payload.get("job_title", "AI Specialist")
    experience_level = payload.get("experience_level", "Mid")
    remote_ratio = payload.get("remote_ratio", 0)
    education_required = payload.get("education_required", "Bachelor")
    company_size = payload.get("company_size", "M")
    required_skills = payload.get("required_skills", []) or []
    benefits_score = float(payload.get("benefits_score", 7.5))

    base_map = {
        "AI Research Scientist": 155_000,
        "AI Software Engineer": 135_000,
        "AI Specialist": 120_000,
        "NLP Engineer": 140_000,
        "AI Consultant": 125_000,
        "AI Architect": 150_000,
        "Principal Data Scientist": 165_000,
        "Data Analyst": 95_000,
    }
    base = base_map.get(job_title, 120_000)

    exp_boost = {
        "Entry": -0.15,
        "Mid": 0.0,
        "Senior": 0.25,
        "Principal": 0.45,
        "Lead": 0.4,
    }.get(experience_level, 0.0)

    if remote_ratio >= 80:
        remote_adj = 0.05
    elif remote_ratio >= 50:
        remote_adj = 0.02
    else:
        remote_adj = 0.0

    edu_adj = {
        "None": -0.05,
        "Bachelor": 0.0,
        "Master": 0.05,
        "PhD": 0.12,
    }.get(education_required, 0.0)

    size_adj = {
        "S": -0.03,
        "M": 0.0,
        "L": 0.03,
        "XL": 0.05,
    }.get(company_size, 0.0)

    skills_adj = min(len(required_skills) * 0.01, 0.08)
    benefits_adj = (benefits_score - 7.5) * 0.01

    salary = base * (1 + exp_boost + remote_adj + edu_adj + size_adj + skills_adj + benefits_adj)
    return int(round(salary, -2))


# -------------------------------
# PUBLICZNE API dla frontendu
# -------------------------------

def predict_salary(payload: Dict[str, Any], use_mock: bool = True) -> Dict[str, Any]:
    """
    Główna funkcja do predykcji wynagrodzenia.

    payload – słownik z cechami oferty (to co budujesz w Streamlit)
    use_mock – gdy False, tu w przyszłości można wpiąć prawdziwy backend.
    """
    try:
        # Na razie ignoruje use_mock i zawsze używamy mocka,
        # ale zostawiłem to pole w odpowiedzi, żeby w przyszłości
        # łatwo było odróżnić źródło.
        salary_usd = _estimate_salary_mock(payload)
        return {
            "status": "ok",
            "prediction": {
                "salary_usd": salary_usd,
            },
            "meta": {
                "source": "mock",  # docelowo: "backend" / "mock_fallback" itd.
                "use_mock_flag": use_mock,
            },
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
        }


def inverse_salary_search(
    target_salary: int,
    constraints: Optional[Dict[str, Optional[List[Any]]]] = None,
    use_mock: bool = True,
    top_n: int = 10,
) -> Dict[str, Any]:
    """
    Znajduje konfiguracje cech, które dają wynagrodzenie bliskie target_salary.

    constraints:
        {
          "job_title": [..] lub None,
          "experience_level": [..] lub None,
          "company_size": [..] lub None,
          "remote_ratio": [..] lub None,
        }

    Zwraca listę konfiguracji posortowaną po |salary - target|.
    """
    constraints = constraints or {}

    # Domyślne przestrzenie przeszukiwania
    default_job_titles = [
        "AI Research Scientist",
        "AI Software Engineer",
        "AI Specialist",
        "NLP Engineer",
        "AI Consultant",
        "AI Architect",
        "Principal Data Scientist",
        "Data Analyst",
    ]
    default_experience = ["Entry", "Mid", "Senior", "Principal", "Lead"]
    default_company_size = ["S", "M", "L", "XL"]
    default_remote_ratio = [0, 50, 100]

    job_titles = constraints.get("job_title") or default_job_titles
    exp_levels = constraints.get("experience_level") or default_experience
    company_sizes = constraints.get("company_size") or default_company_size
    remote_ratios = constraints.get("remote_ratio") or default_remote_ratio

    candidates = []
    for job_title, exp, size, rr in itertools.product(
        job_titles, exp_levels, company_sizes, remote_ratios
    ):
        payload = {
            "job_title": job_title,
            "experience_level": exp,
            "company_size": size,
            "remote_ratio": rr,
            # Przykładowe wartości
            "employment_type": "FT",
            "company_location": "US",
            "employee_residence": "US",
            "education_required": "Master",
            "required_skills": ["Python", "SQL"],
            "industry": "Technology",
            "years_experience": 3,
            "benefits_score": 7.5,
            "salary_currency": "USD",
        }
        salary = _estimate_salary_mock(payload)
        diff = abs(salary - target_salary)
        candidates.append(
            {
                "job_title": job_title,
                "experience_level": exp,
                "company_size": size,
                "remote_ratio": rr,
                "salary_usd": salary,
                "diff_from_target": diff,
            }
        )

    # Sortujemy po różnicy od targetu
    candidates.sort(key=lambda x: x["diff_from_target"])
    solutions = candidates[:top_n]

    return {
        "status": "ok",
        "solutions": solutions,
        "meta": {
            "source": "mock",
            "target_salary": target_salary,
            "use_mock_flag": use_mock,
        },
    }


def salary_grid(
    grid_spec: Dict[str, List[Any]],
    base_payload: Dict[str, Any],
    use_mock: bool = True,
) -> Dict[str, Any]:
    """
    Liczy przewidywane wynagrodzenia dla wszystkich kombinacji w grid_spec.
    base_payload – słownik z innymi cechami, które są stałe dla wszystkich kombinacji.
    """
    try:
        keys = list(grid_spec.keys())
        values_lists = [grid_spec[k] for k in keys]

        rows: List[Dict[str, Any]] = []

        for combo in itertools.product(*values_lists):
            payload = dict(base_payload)  # kopia
            for k, v in zip(keys, combo):
                payload[k] = v
            salary = _estimate_salary_mock(payload)

            row = {k: payload[k] for k in keys}
            row["salary_usd"] = salary
            rows.append(row)

        return {
            "status": "ok",
            "rows": rows,
            "meta": {
                "source": "mock",
                "use_mock_flag": use_mock,
                "grid_size": len(rows),
            },
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
        }
