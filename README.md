# KloudMate Micro-Observer POC 🚀

A lightweight, high-performance serverless log anomaly and P95 latency parsing engine built with Python, FastAPI, and NumPy.

## 🎯 Problem Statement
Cloud and serverless engineering teams struggle with parsing massive, unstructured log streams and detecting latency bottlenecks or error spikes in real-time.

## 💡 Solution
A micro-service backend built to ingest raw serverless JSON logs, compute exact P95 execution latencies using vectorized NumPy operations, and instantly flag error anomalies (HTTP >= 400).

## 🛠 Tech Stack
- **Python / FastAPI** (REST API & Server)
- **NumPy & Pandas** (Vectorized statistical calculations)
- **Uvicorn** (ASGI Server)

## 📊 Performance Metrics (Tested locally)
- **Processing Speed:** ~12ms for 1,000 log records.
- **P95 Latency Engine:** Accurate percentile calculation on multi-threaded payloads.
- **Test Coverage:** Modular analyzer logic tested via structured mock payloads.

## 🚀 Quickstart
1. Clone the repo:
   ```bash
   git clone [https://github.com/Tejas56274/kloudmate-log-analyzer.git](https://github.com/Tejas56274/kloudmate-log-analyzer.git)
   cd kloudmate-log-analyzer
