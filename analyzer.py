import numpy as np
import pandas as pd
from typing import List, Dict, Any


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log entries.

    The function computes total request count, the 95th percentile latency,
    error rate, and a simple health status. It gracefully handles missing
    ``duration_ms`` or ``status_code`` fields and empty datasets.

    Parameters
    ----------
    log_data: List[Dict[str, Any]]
        A list where each item represents a log record. Expected keys are
        ``duration_ms`` (numeric) and ``status_code`` (int). Missing keys are
        treated as ``NaN`` and ignored in calculations.

    Returns
    -------
    Dict[str, Any]
        A dictionary containing the computed metrics.
    """
    if not log_data:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Data",
        }

    # Create DataFrame from the payload
    df = pd.DataFrame(log_data)

    # Ensure required columns exist; fill missing with NaN
    if "duration_ms" not in df.columns:
        df["duration_ms"] = np.nan
    if "status_code" not in df.columns:
        df["status_code"] = np.nan

    # Calculate P95 latency, ignoring missing values
    durations = df["duration_ms"].dropna().values
    if durations.size == 0:
        p95_latency = 0.0
    else:
        p95_latency = np.percentile(durations, 95)

    # Detect error anomalies (HTTP status codes >= 400), ignoring NaN
    errors = df[df["status_code"] >= 400]
    total_requests = len(df)
    error_rate = (len(errors) / total_requests) * 100 if total_requests else 0.0

    return {
        "total_requests": int(total_requests),
        "p95_latency_ms": float(round(p95_latency, 2)),
        "error_rate_pct": float(round(error_rate, 2)),
        "anomalies_detected": int(len(errors)),
        "status": "Healthy" if error_rate < 5 else "Warning: High Error Rate",
    }
