import numpy as np
import pandas as pd
from typing import List, Dict, Any


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log entries.

    The function expects each log entry to contain at least the following keys:
    - ``duration_ms``: numeric latency of the request in milliseconds.
    - ``status_code``: HTTP status code of the request.

    It returns a dictionary with aggregated metrics such as total request count,
    95th‑percentile latency, error rate, and a simple health status.

    The implementation is defensive: it validates the input, gracefully handles
    missing or non‑numeric fields, and avoids crashes caused by ``NaN`` values.
    """

    # Basic sanity check – ensure we received an iterable of mappings
    if not isinstance(log_data, list) or any(not isinstance(item, dict) for item in log_data):
        raise ValueError("log_data must be a list of dictionaries representing log entries.")

    if not log_data:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Data",
        }

    df = pd.DataFrame(log_data)

    # Verify required columns exist
    required_cols = {"duration_ms", "status_code"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required log fields: {', '.join(sorted(missing))}")

    # Coerce types – non‑numeric values become NaN
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce")

    # Drop rows where either field is missing/invalid
    df_clean = df.dropna(subset=["duration_ms", "status_code"])
    if df_clean.empty:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Valid Data",
        }

    # Calculate P95 latency using NumPy
    durations = df_clean["duration_ms"].values
    p95_latency = np.percentile(durations, 95)

    # Detect error anomalies (HTTP status codes >= 400)
    errors = df_clean[df_clean["status_code"] >= 400]
    error_rate = (len(errors) / len(df_clean)) * 100

    return {
        "total_requests": int(len(df_clean)),
        "p95_latency_ms": float(round(p95_latency, 2)),
        "error_rate_pct": float(round(error_rate, 2)),
        "anomalies_detected": int(len(errors)),
        "status": "Healthy" if error_rate < 5 else "Warning: High Error Rate",
    }
