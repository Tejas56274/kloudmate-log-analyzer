import numpy as np
import pandas as pd
from typing import List, Dict, Any


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log entries.

    The function expects each log entry to contain at least the following keys:
    - ``duration_ms``: numeric latency of the request in milliseconds
    - ``status_code``: HTTP status code of the request

    It returns a dictionary with aggregated metrics such as total request count,
    the 95th‑percentile latency, error rate, and a simple health status.

    Args:
        log_data: List of dictionaries representing log records.

    Returns:
        A dictionary with analysis results.

    Raises:
        ValueError: If required fields are missing or contain non‑numeric values.
    """
    if not log_data:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Data",
        }

    df = pd.DataFrame(log_data)

    # Validate required columns
    required_columns = {"duration_ms", "status_code"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required fields in log data: {', '.join(sorted(missing))}")

    # Ensure numeric types for duration_ms
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    if df["duration_ms"].isnull().any():
        raise ValueError("Non‑numeric values found in 'duration_ms' field.")

    # Ensure numeric types for status_code
    df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce")
    if df["status_code"].isnull().any():
        raise ValueError("Non‑numeric values found in 'status_code' field.")

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
