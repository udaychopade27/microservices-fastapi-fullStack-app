from prometheus_client import Counter, Histogram

# HTTP
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

http_request_latency = Histogram(
    "http_request_latency_seconds",
    "HTTP request latency",
    ["endpoint"]
)

# Business KPIs
orders_created = Counter(
    "orders_created_total",
    "Total orders created"
)

orders_paid = Counter(
    "orders_paid_total",
    "Paid orders"
)

orders_failed = Counter(
    "orders_failed_total",
    "Failed orders"
)

order_amount = Counter(
    "order_amount_total",
    "Total order revenue"
)
order_item_count = Histogram(
    "order_item_count",
    "Number of items per order"
)