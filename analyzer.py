import numpy as np
import pandas as pd


def analyze_serverless_logs(log_data: list):
  if not log_data:
    return {
        'total_requests': 0,
        'p95_latency_ms': 0.0,
        'error_rate_pct': 0.0,
        'anomalies_detected': 0,
        'status': 'No Data',
    }

  df = pd.DataFrame(log_data)

  # Calculate P95 latency using NumPy
  durations = df['duration_ms'].values
  p95_latency = np.percentile(durations, 95)

  # Detect error anomalies (HTTP status codes >= 400)
  errors = df[df['status_code'] >= 400]
  error_rate = (len(errors) / len(df)) * 100

  return {
      'total_requests': int(len(df)),
      'p95_latency_ms': float(round(p95_latency, 2)),
      'error_rate_pct': float(round(error_rate, 2)),
      'anomalies_detected': int(len(errors)),
      'status': 'Healthy' if error_rate < 5 else 'Warning: High Error Rate',
  }