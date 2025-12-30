from prometheus_client import Counter, Histogram
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_latency_seconds = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["endpoint"]
)

inventory_requests = Counter(
    "inventory_requests_total",
    "Inventory API calls",
    ["endpoint", "method", "status"]
)

stock_reserved = Counter(
    "stock_reserved_total",
    "Number of items reserved",
    ["product_id"]
)

stock_released = Counter(
    "stock_released_total",
    "Number of items released",
    ["product_id"]
)

inventory_latency = Histogram(
    "inventory_request_latency_seconds",
    "Inventory API latency",
    ["endpoint"]
)
