from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
import os
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="API Gateway")
# -----------------------------
# CORS (VERY IMPORTANT)
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ok for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# AUTH_URL = os.getenv("AUTH_URL")
# INVENTORY_URL = os.getenv("INVENTORY_URL")
# ORDERS_URL = os.getenv("ORDER_URL")
# PAYMENT_URL = os.getenv("PAYMENT_URL")

# -------------------------
# Prometheus
# -------------------------
gateway_requests = Counter(
    "gateway_requests_total",
    "API Gateway requests",
    ["service", "method", "status"]
)

gateway_latency = Histogram(
    "gateway_latency_seconds",
    "Gateway latency",
    ["service"]
)

# -----------------------------
# Service map
# -----------------------------
SERVICES = {
    "auth": "http://auth:8000",
    "inventory": "http://inventory:8001",
    "orders": "http://orders:8002",
    "payments": "http://payment:8003",
}

# -----------------------------
# Generic Proxy
# -----------------------------
@app.api_route("/api/{service}/{path:path}",
               methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        return {"error": "Unknown service"}

    url = f"{SERVICES[service]}/api/{service}/{path}"

    async with httpx.AsyncClient() as client:
        resp = await client.request(
            method=request.method,
            url=url,
            headers=dict(request.headers),
            content=await request.body(),
        )

    return resp.json()
# -------------------------
# Observability
# -------------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    return {"status": "gateway ok"}
