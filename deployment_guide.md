# Multi-Service Architecture: React Frontend & Python Backends
This repository contains a full-stack application featuring a Dockerized React frontend and multiple Python microservices running on the host. Traffic is managed via a two-tier Nginx reverse-proxy setup.
---

## 🏗 System Architecture
The project uses a high-performance routing strategy:

1. **Public Gateway (Host Nginx):** Acts as the primary entry point on the server (Port 80). It routes traffic based on the URL path to either the frontend container or the backend services.

2. **Static Server (Internal Nginx):** Runs inside the Docker container to serve React build files and handle client-side routing.

3. **Python Backends:** Multiple services (Auth, Inventory, Orders, etc.) running directly on the host machine.
---

## 📂 Nginx Configuration Breakdown
### 1. Internal Frontend Config (Docker)
This file is used during the Docker build process to serve the React Single Page Application (SPA).

**Location: frontend/nginx.conf**
```bash
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        # Redirects all traffic to index.html for React Router compatibility
        try_files $uri $uri/ /index.html;
    }
}
```
---
### 2. External Reverse Proxy Config (Server Host)
This configuration must be placed on the host server's Nginx directory (e.g., /etc/nginx/sites-available/default).

**Location:** nginx/default.conf
```bash
server {
    listen 80;
    server_name _; # Accessible via Server IP

    # --- FRONTEND: Routes to React Docker Container ---
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # --- BACKEND: Auth Service ---
    location /api/auth/ {
        proxy_pass http://127.0.0.1:8000/api/auth/;
        proxy_set_header Host $host;
        proxy_set_header Authorization ""; # Security: Scrub auth for login
    }

    # --- BACKEND: Inventory Service ---
    location /api/inventory/ {
        proxy_pass http://127.0.0.1:8001/api/inventory/;
        proxy_set_header Host $host;
        proxy_set_header Authorization $http_authorization;
    }

    # --- BACKEND: Order Service ---
    location /api/orders/ {
        proxy_pass http://127.0.0.1:8002/api/orders/;
        proxy_set_header Host $host;
    }
}
```
---
## 🚀 How to Deploy

### Step 1: Build the Frontend and backend services 
Build and run the React application. Ensure you map the internal port 80 to the host port 8004.

```bash
docker-compose -f docker-compose.yml -f docker-compose-db.yml -f docker-compose-dev.yml -f docker-compose-services.yml -f docker-compose-frontend.yml build --no-cache
```
this will build docker images for all the services

---
### Step 2: Start all the Services Ensure your Python backends are running on their respective ports ($8000, 8001$, etc.).
```bash
docker-compose -f docker-compose.yml -f docker-compose-db.yml -f docker-compose-dev.yml -f docker-compose-services.yml -f docker-compose-frontend.yml up -d
```
### Step 3:  verify all the services Running
```bash
docker-compose -f docker-compose.yml -f docker-compose-db.yml -f docker-compose-dev.yml -f docker-compose-services.yml -f docker-compose-frontend.yml ps 
```
---
### Step 4: Configure Host Nginx
Copy the nginx/default.conf content into /etc/nginx/sites-available/default.

Verify the configuration and reload:

```Bash
sudo nginx -t
sudo systemctl reload nginx
```
---

Now you can use this app from server ip or localhost

---
## 🛠 Troubleshooting
| Error           | Cause                      | Solution                                                         |
|-----------------|----------------------------|------------------------------------------------------------------|
| 502 Bad Gateway | Target service is down      | Check `docker ps` or verify the Python process is running.       |
| 405 Not Allowed | Method mismatch             | Ensure your API call uses the correct slash `/` at the end of the URL. |
| 403 Forbidden  | Permissions                 | Ensure Nginx has access to `/etc/nginx` and relevant folders.    |


