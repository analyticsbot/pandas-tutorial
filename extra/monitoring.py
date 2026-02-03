import time
import requests
from prometheus_client import start_http_server, Counter, Summary

# ---------------- Prometheus Metrics ----------------
llm_calls = Counter(
    "llm_calls_total",
    "Total number of LLM calls",
    ["agent"]
)

llm_tokens_in = Counter(
    "llm_tokens_in_total",
    "Approximate tokens input to LLM",
    ["agent"]
)

llm_tokens_out = Counter(
    "llm_tokens_out_total",
    "Approximate tokens output from LLM",
    ["agent"]
)

llm_latency = Summary(
    "llm_call_latency_seconds",
    "Time spent per LLM call",
    ["agent"]
)

# Start Prometheus server once
start_http_server(8000)

# ---------------- Ollama Config ----------------
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3-vl:30b"  # adjust if needed


def call_llm(agent_name, prompt, max_tokens=800, temperature=0.2):
    start = time.time()

    llm_calls.labels(agent=agent_name).inc()
    llm_tokens_in.labels(agent=agent_name).inc(len(prompt))

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_predict": max_tokens,
            "temperature": temperature
        }
    }

    resp = requests.post(OLLAMA_URL, json=payload, timeout=600)
    resp.raise_for_status()

    output = resp.json()["response"]

    llm_tokens_out.labels(agent=agent_name).inc(len(output))
    llm_latency.labels(agent=agent_name).observe(time.time() - start)

    return output
