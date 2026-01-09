from prometheus_client import Counter, Gauge, Histogram

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"]
)

http_request_latency = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["path"]
)

orders_created = Counter("orders_created_total", "Orders created")
orders_paid = Counter("orders_paid_total", "Orders paid")
orders_failed = Counter("orders_failed_total", "Orders failed")

# ✅ Revenue can go UP & DOWN
revenue_total = Gauge("revenue_total", "Current total revenue")

# ✅ Refund is cumulative
refund_total = Counter("refund_total", "Total refunded amount")
