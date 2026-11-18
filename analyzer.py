import numpy as np
import pandas as pd
from typing import List, Dict, Any


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log entries.

    The function expects each log entry to contain at least the keys
    ``duration_ms`` (numeric) and ``status_code`` (numeric). It returns a
    dictionary with aggregated metrics such as total requests, the 95th
    percentile latency, error rate, and a simple health status.

    Robustness improvements:
    * Validates that ``log_data`` is a list and contains the required fields.
    * Converts ``duration_ms`` and ``status_code`` to numeric types, coercing
      invalid values to ``NaN`` and handling them gracefully.
    * Returns a default "no‑data" result when the input is empty or when all
      rows are filtered out due to invalid data.
    """
    # Guard against incorrect input types
    if not isinstance(log_data, list):
        raise ValueError("log_data must be a list of dictionaries.")

    if not log_data:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Data",
        }

    df = pd.DataFrame(log_data)

    # Ensure required columns exist
    required_columns = {"duration_ms", "status_code"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(sorted(missing))}")

    # Convert columns to numeric, coercing errors to NaN
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce")

    # Drop rows where duration is not a valid number (cannot compute latency)
    df = df.dropna(subset=["duration_ms"])
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
