import numpy as np
import pandas as pd
from typing import Any, Dict, List


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log entries.

    The function expects each log dictionary to contain at least the keys
    ``duration_ms`` (numeric) and ``status_code`` (numeric). It safely handles
    missing or non‑numeric values by ignoring malformed rows rather than raising
    an exception.

    Parameters
    ----------
    log_data: List[Dict[str, Any]]
        A list of log records where each record is a mapping with the required
        fields.

    Returns
    -------
    Dict[str, Any]
        A dictionary with aggregated metrics such as total requests, P95
        latency, error rate, and a health status.
    """
    # Guard against empty input early
    if not log_data:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Data",
        }

    # Convert to DataFrame; any missing keys become NaN
    df = pd.DataFrame(log_data)

    # Ensure required columns exist; if not, raise a clear error
    required_columns = {"duration_ms", "status_code"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required log fields: {', '.join(sorted(missing))}")

    # Coerce columns to numeric, turning invalid entries into NaN
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce")

    # Drop rows where either required field is NaN after coercion
    df = df.dropna(subset=["duration_ms", "status_code"])

    # If all rows were invalid, return a no‑data result
    if df.empty:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Valid Data",
        }

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
