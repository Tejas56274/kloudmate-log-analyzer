import numpy as np
import pandas as pd
from typing import List, Dict, Any


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log entries.

    The function expects each log entry to contain at least the following keys:
    - ``duration_ms``: numeric latency of the request in milliseconds.
    - ``status_code``: HTTP status code of the request.

    It returns a dictionary with aggregated metrics such as total request count,
    the 95th‑percentile latency, error rate, and a simple health status.

    The implementation now validates input data, ensures required columns are
    present, and gracefully handles non‑numeric values by coercing them to
    ``NaN`` and dropping invalid rows. Clear ``ValueError`` messages are raised
    for missing fields or completely invalid payloads, which the API layer can
    translate into a 400 response.
    """

    # Basic type check – the API should already enforce a list, but we guard
    # against accidental misuse when the function is called directly.
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

    # Verify required columns exist.
    required_columns = {"duration_ms", "status_code"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required field(s): {', '.join(sorted(missing))}")

    # Convert duration to numeric, coercing errors to NaN.
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    # Drop rows where duration could not be parsed.
    df = df.dropna(subset=["duration_ms"])
    if df.empty:
        raise ValueError("All 'duration_ms' values are non‑numeric or missing.")

    # Ensure status_code is numeric (treat non‑numeric as 0 which is non‑error).
    df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce").fillna(0).astype(int)

    # Calculate P95 latency using NumPy.
    durations = df["duration_ms"].values
    p95_latency = np.percentile(durations, 95)

    # Detect error anomalies (HTTP status codes >= 400).
    errors = df[df["status_code"] >= 400]
    error_rate = (len(errors) / len(df)) * 100

    return {
        "total_requests": int(len(df)),
        "p95_latency_ms": float(round(p95_latency, 2)),
        "error_rate_pct": float(round(error_rate, 2)),
        "anomalies_detected": int(len(errors)),
        "status": "Healthy" if error_rate < 5 else "Warning: High Error Rate",
    }
