import numpy as np
import pandas as pd
from typing import List, Dict, Any


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log entries.

    The function expects each log dictionary to contain at least the keys
    ``duration_ms`` (numeric) and ``status_code`` (integer). It returns a summary
    dictionary with total request count, the 95th‑percentile latency, error rate,
    number of anomalies, and an overall status string.

    Args:
        log_data: List of log dictionaries.

    Returns:
        A dictionary with analysis results.

    Raises:
        ValueError: If required fields are missing or cannot be interpreted as
            numeric values.
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

    df = pd.DataFrame(log_data)

    # Validate required columns exist
    required_columns = {"duration_ms", "status_code"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(
            f"Missing required log fields: {', '.join(sorted(missing))}. "
            "Each log entry must contain 'duration_ms' and 'status_code'."
        )

    # Ensure duration_ms is numeric; coerce errors to NaN and drop them
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    if df["duration_ms"].isna().any():
        raise ValueError("'duration_ms' must be numeric for all log entries.")

    # Ensure status_code is integer‑like; coerce errors to NaN and validate
    df["status_code"] = pd.to_numeric(df["status_code"], errors="coerce")
    if df["status_code"].isna().any():
        raise ValueError("'status_code' must be an integer for all log entries.")

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
