import numpy as np
import pandas as pd
from typing import List, Dict, Any


def _validate_log_data(log_data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Validate raw log entries and return a clean DataFrame.

    The function ensures that the required columns ``duration_ms`` and ``status_code``
    exist and contain numeric values. Rows with invalid data are dropped, and a clear
    ``ValueError`` is raised if the resulting DataFrame is empty.
    """
    df = pd.DataFrame(log_data)

    # Required columns
    required_cols = {"duration_ms", "status_code"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required column(s): {', '.join(sorted(missing))}")

    # Coerce to numeric, invalid parsing becomes NaN
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce")

    # Drop rows where either field is NaN
    df = df.dropna(subset=["duration_ms", "status_code"])
    if df.empty:
        raise ValueError("No valid log records after cleaning input data.")

    # Ensure correct dtypes for later calculations
    df["duration_ms"] = df["duration_ms"].astype(float)
    df["status_code"] = df["status_code"].astype(int)
    return df


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log entries.

    Returns a dictionary with total request count, the 95th‑percentile latency,
    error rate, number of anomalies, and an overall health status.
    """
    if not log_data:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Data",
        }

    # Validate and clean the input data
    df = _validate_log_data(log_data)

    # Calculate P95 latency using NumPy
    durations = df["duration_ms"].values
    p95_latency = np.percentile(durations, 95)

    # Detect error anomalies (HTTP status codes >= 400)
    errors = df[df["status_code"] >= 400]
    error_rate = (len(errors) / len(df)) * 100

    return {
        "total_requests": int(len(df)),
        "p95_latency_ms": float(round(p95_latency, 2)),
        "error_rate_pct": float(round(error_rate, 2)),
        "anomalies_detected": int(len(errors)),
        "status": "Healthy" if error_rate < 5 else "Warning: High Error Rate",
    }
