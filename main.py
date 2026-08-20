from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from analyzer import analyze_serverless_logs

app = FastAPI(
    title="KloudMate Micro-Observer POC",
    description=(
        "Lightweight serverless log analyzer for P95 latency and anomalies."
    ),
    version="1.0.0",
)


@app.get("/")
def home():
  return {
      "message": "Log Analyzer API is running. Send POST request to /analyze"
  }


@app.post("/analyze")
def analyze_logs(payload: List[Dict[str, Any]]):
  try:
    result = analyze_serverless_logs(payload)
    return {"success": True, "metrics": result}
  except Exception as e:
    raise HTTPException(status_code=400, detail=str(e))