from typing import Any, Dict, List, Optional
from pathlib import Path
import itertools
import pandas as pd

try:
    from autogluon.tabular import TabularPredictor
except Exception:
    TabularPredictor = None


MODELS_DIR = Path("Data/models")
LABEL_COL = "salary_usd"

_MODEL_CACHE: Dict[str, Any] = {"predictor": None}


def _estimate_salary_mock(payload: Dict[str, Any]) -> int:
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


def _load_predictor() -> "TabularPredictor":
    if _MODEL_CACHE["predictor"] is not None:
        return _MODEL_CACHE["predictor"]

    if TabularPredictor is None:
        raise RuntimeError("AutoGluon nie jest zainstalowany w środowisku.")

    if not MODELS_DIR.exists():
        raise FileNotFoundError(f"Nie znaleziono katalogu z modelem: {MODELS_DIR}")

    predictor = TabularPredictor.load(str(MODELS_DIR))
    _MODEL_CACHE["predictor"] = predictor
    return predictor


def _payload_to_frame(payload: Dict[str, Any]) -> pd.DataFrame:
    df = pd.DataFrame([payload])

    required_cols = ['posting_date', 'application_deadline']
    for col in required_cols:
        if col not in df.columns:
            df[col] = pd.NA

    if "remote_ratio" in df.columns:
        df["remote_ratio"] = pd.to_numeric(df["remote_ratio"], errors="coerce")
    if "years_experience" in df.columns:
        df["years_experience"] = pd.to_numeric(df["years_experience"], errors="coerce")
    if "benefits_score" in df.columns:
        df["benefits_score"] = pd.to_numeric(df["benefits_score"], errors="coerce")

    for col in ["posting_date", "application_deadline"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    if "job_description_length" in df.columns:
        df["job_description_length"] = pd.to_numeric(df["job_description_length"], errors="coerce").fillna(0)
    else:
        df["job_description_length"] = 0

    if "company_name" in df.columns:
        df["company_name"] = df["company_name"].astype(str).fillna("Unknown")
    else:
        df["company_name"] = "Unknown"

    if "required_skills" in df.columns:
        v = df.at[0, "required_skills"]
        if isinstance(v, list):
            df.at[0, "required_skills"] = ", ".join([str(x) for x in v])

    return df


def predict_salary(payload: Dict[str, Any], use_mock: bool = False) -> Dict[str, Any]:
    if use_mock:
        salary_usd = _estimate_salary_mock(payload)
        return {
            "status": "ok",
            "prediction": {"salary_usd": salary_usd},
            "meta": {"source": "mock"},
        }

    try:
        predictor = _load_predictor()
        X = _payload_to_frame(payload)

        if LABEL_COL in X.columns:
            X = X.drop(columns=[LABEL_COL])

        pred = predictor.predict(X)
        salary_usd = float(pred.iloc[0])

        return {
            "status": "ok",
            "prediction": {"salary_usd": salary_usd},
            "meta": {"source": "autogluon"},
        }
    except Exception as exc:
        return {
            "status": "error",
            "error": str(exc),
            "meta": {"source": "autogluon"},
        }


def inverse_salary_search(
    target_salary: int,
    constraints: Optional[Dict[str, Optional[List[Any]]]] = None,
    use_mock: bool = False,
    top_n: int = 10,
) -> Dict[str, Any]:
    constraints = constraints or {}

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
    for job_title, exp, size, rr in itertools.product(job_titles, exp_levels, company_sizes, remote_ratios):
        payload = {
            "job_title": job_title,
            "experience_level": exp,
            "company_size": size,
            "remote_ratio": rr,
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

        resp = predict_salary(payload, use_mock=use_mock)
        if resp.get("status") != "ok":
            return resp

        salary = float(resp["prediction"]["salary_usd"])
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

    candidates.sort(key=lambda x: x["diff_from_target"])
    solutions = candidates[:top_n]

    return {
        "status": "ok",
        "solutions": solutions,
        "meta": {"source": "mock" if use_mock else "autogluon", "target_salary": target_salary},
    }


def salary_grid(
    grid_spec: Dict[str, List[Any]],
    base_payload: Dict[str, Any],
    use_mock: bool = False,
) -> Dict[str, Any]:
    try:
        keys = list(grid_spec.keys())
        values_lists = [grid_spec[k] for k in keys]

        rows: List[Dict[str, Any]] = []

        for combo in itertools.product(*values_lists):
            payload = dict(base_payload)
            for k, v in zip(keys, combo):
                payload[k] = v

            resp = predict_salary(payload, use_mock=use_mock)
            if resp.get("status") != "ok":
                return resp

            salary = float(resp["prediction"]["salary_usd"])
            row = {k: payload[k] for k in keys}
            row["salary_usd"] = salary
            rows.append(row)

        return {
            "status": "ok",
            "rows": rows,
            "meta": {"source": "mock" if use_mock else "autogluon", "grid_size": len(rows)},
        }
    except Exception as exc:
        return {"status": "error", "error": str(exc)}
