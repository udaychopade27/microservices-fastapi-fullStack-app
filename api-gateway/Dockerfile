FROM python:3.11-slim

# ---------- install nginx ----------
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ---------- python deps ----------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---------- copy app ----------
COPY . .

# ---------- nginx config ----------
COPY nginx.conf /etc/nginx/conf.d/default.conf

# ---------- start both ----------
CMD ["sh", "-c", "nginx && uvicorn main:app --host 0.0.0.0 --port 8080"]
EXPOSE 8080