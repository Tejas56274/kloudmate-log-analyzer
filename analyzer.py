import numpy as np
import pandas as pd
from typing import List, Dict, Any


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log entries.

    The function expects each log entry to contain at least the keys
    ``duration_ms`` (numeric) and ``status_code`` (int). Entries missing these
    fields or containing non‑numeric ``duration_ms`` values are ignored in the
    calculations. If no valid entries remain, a default result indicating no
    data is returned.

    Parameters
    ----------
    log_data: List[Dict[str, Any]]
        Raw log records received from the API payload.

    Returns
    -------
    Dict[str, Any]
        A dictionary with aggregated metrics such as total requests, P95
        latency, error rate, and a health status.
    """
    # Guard against non‑list input
    if not isinstance(log_data, list):
        raise ValueError("log_data must be a list of dictionaries")

    if not log_data:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Data",
        }

    # Create DataFrame and ensure required columns exist
    df = pd.DataFrame(log_data)
    required_cols = {"duration_ms", "status_code"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required fields in log data: {', '.join(missing_cols)}")

    # Drop rows where required fields are missing or NaN
    df = df.dropna(subset=["duration_ms", "status_code"])

    # Coerce duration to numeric, invalid parsing becomes NaN and are dropped
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    df = df.dropna(subset=["duration_ms"])

    if df.empty:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Valid Data",
        }

    # Calculate P95 latency using NumPy (ignores NaN automatically)
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
