from fastapi import FastAPI, Request, Response
import httpx
import os
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI(title="API Gateway")

AUTH_URL = os.getenv("AUTH_URL")
INVENTORY_URL = os.getenv("INVENTORY_URL")
ORDERS_URL = os.getenv("ORDER_URL")
PAYMENT_URL = os.getenv("PAYMENT_URL")

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

# -------------------------
# Reverse proxy engine
# -------------------------
async def proxy(request: Request, target_url: str, service: str):
    start = time.time()

    async with httpx.AsyncClient() as client:
        body = await request.body()
        headers = dict(request.headers)
        headers.pop("host", None)

        resp = await client.request(
            request.method,
            f"{target_url}{request.url.path}",
            params=request.query_params,
            content=body,
            headers=headers,
            timeout=30
        )

    duration = time.time() - start

    gateway_requests.labels(service, request.method, resp.status_code).inc()
    gateway_latency.labels(service).observe(duration)

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=resp.headers
    )

# -------------------------
# Routes
# -------------------------
@app.api_route("/api/auth/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def auth_proxy(request: Request, path: str):
    return await proxy(request, AUTH_URL, "auth")

@app.api_route("/api/inventory/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def inventory_proxy(request: Request, path: str):
    return await proxy(request, INVENTORY_URL, "inventory")

@app.api_route("/api/orders/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def orders_proxy(request: Request, path: str):
    return await proxy(request, ORDERS_URL, "orders")

@app.api_route("/api/payments/{path:path}", methods=["GET","POST","PUT","DELETE"])
async def payments_proxy(request: Request, path: str):
    return await proxy(request, PAYMENT_URL, "payments")

# -------------------------
# Observability
# -------------------------
@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/health")
def health():
    return {"status": "gateway ok"}
