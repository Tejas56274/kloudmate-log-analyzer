import numpy as np
import pandas as pd
from typing import List, Dict, Any


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log entries.

    Each log entry must contain the keys ``duration_ms`` (numeric) and ``status_code`` (int).
    The function returns a dictionary with aggregated metrics such as total requests,
    95th‑percentile latency, error rate and a health status.

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

    # Validate required keys and types
    required_keys = {"duration_ms", "status_code"}
    for idx, entry in enumerate(log_data):
        missing = required_keys - entry.keys()
        if missing:
            raise ValueError(f"Log entry at index {idx} is missing required fields: {', '.join(missing)}")
        # Ensure duration is numeric
        try:
            float(entry["duration_ms"])
        except (TypeError, ValueError):
            raise ValueError(f"'duration_ms' must be numeric in log entry at index {idx}")
        # Ensure status_code is int‑compatible
        try:
            int(entry["status_code"])
        except (TypeError, ValueError):
            raise ValueError(f"'status_code' must be an integer in log entry at index {idx}")

    df = pd.DataFrame(log_data)

    # Convert columns to appropriate dtypes for safety
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="raise")
    df["status_code"] = df["status_code"].astype(int)

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
