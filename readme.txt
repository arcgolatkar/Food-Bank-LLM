# AWS ECS Deployment Documentation: Food Bank Chatbot

This document outlines detailed instructions to deploy the Food Bank Chatbot system using Amazon ECS with Fargate, ECR, Application Load Balancer (ALB), and CodeCatalyst CI/CD.

---

## 1. Project Structure Overview

Organize the repository as follows:

```
foodbank-project/
├── .aws/
│   └── workflows/
│       └── frontend-backend-pipeline.yaml
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
├── frontend/
│   ├── streamlit_app.py
│   ├── requirements.txt
│   ├── Dockerfile
└── README.md
```

---

## 2. Docker Image Creation and Push

### 2.1 Authenticate Docker with ECR
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
```

### 2.2 Backend
```bash
cd backend
docker build -t foodbank-backend .
docker tag foodbank-backend:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/foodbank-backend:latest
docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/foodbank-backend:latest
```

### 2.3 Frontend
```bash
cd frontend
docker build -t foodbank-frontend .
docker tag foodbank-frontend:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/foodbank-frontend:latest
docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/foodbank-frontend:latest
```

---

## 3. ECS Configuration

### 3.1 Create Backend ECS Task Definition
- Use Fargate launch type
- Define container with port 5000
- Assign `OPENAI_API_KEY` as an environment variable
- Enable awslogs logging

### 3.2 Create Frontend ECS Task Definition
- Define container with port 8501
- Add backend ALB URL as `BACKEND_URL` in code
- Enable awslogs logging

---

## 4. Security Groups Setup

### 4.1 ALB Security Group
- Inbound: TCP 80 from 0.0.0.0/0

### 4.2 Backend Task Security Group
- Inbound: TCP 5000 from ALB SG

### 4.3 Frontend Task Security Group
- Inbound: TCP 8501 from ALB SG

All SGs should allow all outbound traffic.

---

## 5. Load Balancer Setup

### 5.1 Create Backend Target Group
- Type: IP
- Protocol: HTTP
- Port: 5000
- Health Check Path: `/api/health`

### 5.2 Create Backend ALB
- Scheme: internet-facing
- Listener: HTTP 80 → forward to backend TG

### 5.3 Create Frontend Target Group
- Type: IP
- Protocol: HTTP
- Port: 8501
- Health Check Path: `/`

### 5.4 Create Frontend ALB
- Listener: HTTP 80 → forward to frontend TG

---

## 6. ECS Service Deployment

### 6.1 Deploy Backend Service
- Use backend task definition
- Associate backend ALB + target group
- Assign public IP

### 6.2 Deploy Frontend Service
- Use frontend task definition
- Associate frontend ALB + target group
- Assign public IP

---

## 7. Validate Services

### 7.1 Backend
```bash
curl http://<backend-alb-dns>/api/health
```
Expected output:
```json
{"status":"healthy"}
```

### 7.2 Frontend
```bash
curl http://<frontend-alb-dns>
```
Expected: Streamlit HTML content

---

## 8. Automate with CodeCatalyst (Optional)

### 8.1 YAML File Location
```
.aws/workflows/frontend-backend-pipeline.yaml
```

### 8.2 Workflow Highlights
- Trigger: push to `main`
- Build and push Docker images
- Deploy updated ECS services

---

## 9. Shutdown and Cost Saving

### 9.1 Reduce Running Tasks
- Go to ECS → Services → Update → Set desired count to 0

### 9.2 Delete ALBs
- ALBs incur ~$16/month
- Remove unused load balancers to stop billing

### 9.3 Release EIPs / NAT Gateways
- Check if any are allocated and unused

### 9.4 Retain Task Definitions / ECR
- No cost for keeping ECS configuration or pushed images

---

## 10. Optional Enhancements

- Use Route 53 to map ALB DNS to custom domains
- Use AWS Certificate Manager for HTTPS
- Configure auto-scaling based on CPU or memory

---

This documentation enables any team member to reproduce the full ECS deployment with confidence. Store it alongside your repository or publish to internal docs as needed.
