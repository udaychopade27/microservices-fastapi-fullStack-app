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

payments_total = Counter(
    "payments_total",
    "Total payment attempts"
)

payments_success = Counter(
    "payments_success_total",
    "Successful payments"
)

payments_failed = Counter(
    "payments_failed_total",
    "Failed payments"
)

payment_amount = Counter(
    "payment_amount_total",
    "Total processed payment amount"
)

payment_latency = Histogram(
    "payment_latency_seconds",
    "Payment processing latency"
)
refunds_total = Counter(
    "refunds_total",
    "Total refund attempts"
)