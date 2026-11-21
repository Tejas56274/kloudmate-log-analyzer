import numpy as np
import pandas as pd
from typing import List, Dict


def analyze_serverless_logs(log_data: List[Dict]) -> Dict:
    """Analyze a list of serverless log entries.

    The function expects each log entry to contain at least the following keys:
    - ``duration_ms``: numeric execution duration in milliseconds
    - ``status_code``: HTTP status code (int)

    It returns a dictionary with aggregated metrics such as total requests,
    95th‑percentile latency, error rate, and a simple health status.

    The implementation now validates input data, gracefully handles missing or
    non‑numeric fields, and avoids ``NaN`` propagation that could cause runtime
    errors.
    """
    # Early return for empty payloads
    if not log_data:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Data",
        }

    df = pd.DataFrame(log_data)

    # Verify required columns are present
    required_columns = ["duration_ms", "status_code"]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    # Remove rows where required fields are missing or not convertible
    df = df.dropna(subset=required_columns)
    if df.empty:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Valid Data",
        }

    # Ensure duration is numeric; coerce errors to NaN and drop them
    durations = pd.to_numeric(df["duration_ms"], errors="coerce").dropna()
    if durations.empty:
        p95_latency = 0.0
    else:
        p95_latency = np.percentile(durations.values, 95)

    # Detect error anomalies (HTTP status codes >= 400)
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
