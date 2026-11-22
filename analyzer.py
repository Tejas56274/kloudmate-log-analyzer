import numpy as np
import pandas as pd
from typing import List, Dict, Any


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log entries.

    Each log entry must contain the keys ``duration_ms`` (numeric) and ``status_code`` (int).
    The function returns aggregated metrics such as total requests, P95 latency, error rate,
    and a health status.

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
    required_keys = {"duration_ms", "status_code"}
    missing_keys = required_keys - set(df.columns)
    if missing_keys:
        raise ValueError(f"Missing required field(s): {', '.join(sorted(missing_keys))}")

    # Ensure duration_ms is numeric
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    if df["duration_ms"].isnull().any():
        raise ValueError("All 'duration_ms' values must be numeric")

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
