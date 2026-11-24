import numpy as np
import pandas as pd
from typing import List, Dict, Any


def _validate_log_entry(entry: Dict[str, Any], index: int) -> None:
    """Validate a single log entry.

    Ensures that required keys ``duration_ms`` and ``status_code`` are present and
    that ``duration_ms`` can be interpreted as a numeric value. Raises a ``ValueError``
    with a clear message if validation fails.
    """
    required_keys = ["duration_ms", "status_code"]
    missing = [key for key in required_keys if key not in entry]
    if missing:
        raise ValueError(
            f"Log entry at index {index} is missing required fields: {', '.join(missing)}"
        )
    # ``duration_ms`` should be convertible to a float; ``status_code`` to an int.
    try:
        float(entry["duration_ms"])
    except (TypeError, ValueError):
        raise ValueError(
            f"'duration_ms' in log entry at index {index} must be a numeric value"
        )
    try:
        int(entry["status_code"])
    except (TypeError, ValueError):
        raise ValueError(
            f"'status_code' in log entry at index {index} must be an integer"
        )


def analyze_serverless_logs(log_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze a list of serverless log records.

    The function computes:
    * Total number of requests
    * 95th‑percentile latency (ms)
    * Error rate percentage (HTTP status >= 400)
    * Number of error anomalies detected
    * Overall health status based on error rate

    Parameters
    ----------
    log_data: List[Dict[str, Any]]
        A list where each item represents a single log entry containing at least
        ``duration_ms`` (numeric) and ``status_code`` (int).

    Returns
    -------
    Dict[str, Any]
        A dictionary with the calculated metrics.
    """
    if not log_data:
        return {
            "total_requests": 0,
            "p95_latency_ms": 0.0,
            "error_rate_pct": 0.0,
            "anomalies_detected": 0,
            "status": "No Data",
        }

    # Validate each entry before constructing the DataFrame.
    for idx, entry in enumerate(log_data):
        _validate_log_entry(entry, idx)

    df = pd.DataFrame(log_data)

    # Ensure correct dtypes for calculations.
    df["duration_ms"] = pd.to_numeric(df["duration_ms"], errors="coerce")
    df["status_code"] = pd.to_numeric(df["status_code"], downcast="integer", errors="coerce")

    if df["duration_ms"].isnull().any():
        raise ValueError("One or more 'duration_ms' values could not be converted to numbers.")
    if df["status_code"].isnull().any():
        raise ValueError("One or more 'status_code' values could not be converted to integers.")

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
