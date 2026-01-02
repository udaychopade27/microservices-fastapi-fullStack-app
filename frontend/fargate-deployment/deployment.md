# 🚀 Deploying Application to AWS ECS Fargate

This document describes how to deploy a containerized application (frontend + microservices) on **AWS ECS Fargate** using **Application Load Balancer (ALB)**, **Cloud Map**, **Secrets Manager**, and **RDS**.

This setup follows **AWS best practices**:
- No EC2 instances
- Containers run in private subnets
- ALB is the only public entry point
- Secure service-to-service communication

---

## 🏗️ Architecture Overview
```mermaid
flowchart TB

    %% USERS
    U[Internet Users]

    %% NETWORK LAYER
    U -->|HTTPS| ALB[Application Load Balancer<br>(Public Subnets)]

    %% FRONTEND
    ALB --> FE[Frontend Service<br>ECS Fargate<br>Private Subnets]

    %% BACKEND SERVICES
    FE --> AUTH[Auth Service<br>ECS Fargate]
    FE --> ORDER[Order Service<br>ECS Fargate]
    FE --> INVENTORY[Inventory Service<br>ECS Fargate]
    FE --> PAYMENT[Payment Service<br>ECS Fargate]

    %% DATABASE
    AUTH --> RDS[(Amazon RDS<br>PostgreSQL)]
    ORDER --> RDS
    INVENTORY --> RDS
    PAYMENT --> RDS

    %% STYLES
    classDef public fill:#cce5ff,stroke:#004085,stroke-width:2px;
    classDef private fill:#d4edda,stroke:#155724,stroke-width:2px;
    classDef data fill:#fff3cd,stroke:#856404,stroke-width:2px;

    class ALB public;
    class FE,AUTH,ORDER,INVENTORY,PAYMENT private;
    class RDS data;


```
## 🔐 Security & Network Flow
| Layer              | Security                  |
| ------------------ | ------------------------- |
| Internet → ALB     | HTTPS (443)               |
| ALB → Frontend     | HTTP (80) or HTTPS        |
| Frontend → Backend | Private VPC only          |
| Backend → RDS      | Security Group restricted |

---

## 📋 Prerequisites

- AWS Account
- Docker installed locally
- AWS CLI configured
- VPC with:
  - 2 Public subnets (different AZs)
  - 2 Private subnets (different AZs)
- Internet Gateway attached to VPC
- NAT Gateway in public subnet
- Amazon ECR repositories for images

---

## 🔐 IAM Roles

### 1️⃣ ECS Task Execution Role
Used by ECS to:
- Pull images from ECR
- Write logs to CloudWatch
- Read secrets from Secrets Manager

Attach policy:
- AmazonECSTaskExecutionRolePolicy
Role name:
- ecsTaskExecutionRole

Attach permissions only if the application needs AWS services (S3, SQS, etc).

---

## 🔑 Secrets Management

Use **AWS Secrets Manager** to store sensitive data.

Example:
- RDS credentials (username, password, host, port, dbname)
- JWT secrets
- API keys

Secrets are injected into ECS tasks as environment variables.

---

## 🐳 Build & Push Docker Images

Authenticate Docker to ECR:
```bash
aws ecr get-login-password --region us-east-1 \
| docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
```
Build and Push:
```bash
docker build -t frontend .
docker tag frontend:latest <ecr-repo-url>:latest
docker push <ecr-repo-url>:latest
```
Repeat for each microservice.

---

## 📦 ECS Task Definitions
Create **one task definition per service.**
**Common Settings**
- Launch type: **Fargate**
- Network mode: awsvpc
- CPU: 0.25 vCPU
- Memory: 0.5 GB
- Execution role: ecsTaskExecutionRole
- Task role: ecsTaskRole
- Logging: awslogs
---

### Frontend Task Defination:
- Container port: 80
- Environment variables:
```bash
AUTH_SVC=auth.microservices.local
ORDER_SVC=order.microservices.local
INVENTORY_SVC=inventory.microservices.local
PAYMENT_SVC=payment.microservices.local
```
---
### Backend Task Definitions

- Each service exposes its own port (e.g. 8000, 8001, 8002)

- Use Secrets Manager for DB credentials

- Use Cloud Map DNS names for service communication
---
## 🌐 Service Discovery (Cloud Map)

Create a private namespace:
```ini
microservices.local
```

Each backend service registers itself:
| Service   | DNS Name                      |
| --------- | ----------------------------- |
| auth      | auth.microservices.local      |
| inventory | inventory.microservices.local |
| order     | order.microservices.local     |
| payment   | payment.microservices.local   |

---

## 🚢 ECS Services
### Backend Services

Launch type: Fargate
Subnets: Private
Public IP: ❌ Disabled
Service discovery: ✅ Enabled
Load balancer: ❌ None


### Frontend Service
Launch type: Fargate
Subnets: Private
Public IP: ❌ Disabled
Load balancer: ✅ Application Load Balancer
Target group type: IP
Target port: 80

## 🌍 Application Load Balancer
ALB Configuration
Scheme: Internet-facing
Subnets: Public (2 AZs)
Security group:
HTTP 80 → 0.0.0.0/0
HTTPS 443 → 0.0.0.0/0

Listener
HTTP :80 → Forward → frontend target group
(Optional) HTTPS using ACM.

## 🔒 Networking & Security
Security Groups
ALB SG: Allows 80/443 from internet
ECS SG: Allows traffic from ALB SG
RDS SG: Allows port 5432 from ECS SG
Network ACLs
Public NACL for ALB subnets
Private NACL for ECS & RDS subnets
Allow ephemeral ports (1024–65535)

## 🧪 Validation Checklist

ECS services are RUNNING
Target groups are healthy
ALB DNS opens frontend
Backend services communicate via Cloud Map
CloudWatch logs show no errors

## 🔄 Scaling (Optional)

Enable ECS service auto-scaling:
Min tasks: 1
Max tasks: 4
CPU target: 60%

## 🔐 HTTPS (Recommended)

Request certificate via AWS ACM
Attach to ALB HTTPS listener
Redirect HTTP → HTTPS

## 🏁 Cleanup (Important)

To avoid extra costs:
- Delete ECS services and cluster
- Delete ALB and target groups
- Delete NAT Gateway and Elastic IP
- Delete RDS instance
- Delete Secrets Manager secrets
- Delete Cloud Map namespace

## ✅ Conclusion

This deployment provides:
- Fully managed containers
- Secure networking
- Scalable microservices
- Production-ready AWS architecture
- Happy deploying 🚀


---

## ✅ What you can do next
- Add **CI/CD (GitHub Actions → ECR → ECS)**
- Convert this to **Terraform**
- Add architecture diagram
- Create a shorter README version

