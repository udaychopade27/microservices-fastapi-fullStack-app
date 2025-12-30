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
auth_requests = Counter(
    "auth_requests_total",
    "Total auth API calls",
    ["endpoint", "method", "status"]
)

auth_latency = Histogram(
    "auth_request_latency_seconds",
    "Auth request latency",
    ["endpoint"]
)

auth_login_attempts = Counter(
    "auth_login_attempts_total",
    "Total login attempts"
)

auth_login_success = Counter(
    "auth_login_success_total",
    "Successful logins"
)

auth_login_failed = Counter(
    "auth_login_failed_total",
    "Failed logins"
)

auth_signup = Counter(
    "auth_signup_total",
    "User signups"
)
auth_password_resets = Counter(
    "auth_password_resets_total",
    "Password reset requests"   
)