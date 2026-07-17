# Skycast

A real-time weather web application built with Python Flask, containerized with Docker, and deployed on AWS using Terraform. Features a fully automated CI/CD pipeline with GitHub Actions that builds, tests, and deploys on every push to main.

---

## Architecture

- **Frontend**: Apple Weather-inspired UI served by Flask
- **Backend**: Python Flask REST API
- **Weather Data**: OpenWeatherMap API
- **Container**: Docker image stored in Amazon ECR
- **Compute**: AWS ECS Fargate (serverless containers)
- **Networking**: VPC with public subnets, Internet Gateway, Route Tables
- **Load Balancer**: Application Load Balancer (ALB)
- **Logging**: CloudWatch Logs for container monitoring
- **State Management**: Terraform remote state on S3 with locking
- **CI/CD**: GitHub Actions — automated test, build and deploy pipeline
- **Infrastructure as Code**: Terraform

---

## CI/CD Pipeline

Every push to the `main` branch automatically triggers:

1. **Test** — runs pytest against the Flask app
2. **Build** — builds a new Docker image tagged with the commit SHA
3. **Push** — pushes the image to Amazon ECR
4. **Deploy** — updates the ECS task definition and deploys to Fargate

No manual steps required after a code push.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Skycast weather UI |
| GET | /api/weather?city={city} | Get weather for a city |
| GET | /health | Health check |

---

## Prerequisites

- AWS CLI installed and configured
- Docker installed and running
- Terraform installed (v1.0+)
- OpenWeatherMap API key (free at openweathermap.org)
- GitHub account with Actions enabled

---

## How to Deploy

### 1. Clone the Repository
```bash
git clone https://github.com/francisegenti/SkyCast.git
cd SkyCast
```

### 2. Create an ECR Repository
**Create the repository on AWS to store your Docker image:**
```bash
aws ecr create-repository --repository-name skycast --region us-east-1
```

### 3. Build the Docker Image
**Build the image locally from the project root:**
```bash
docker build -t skycast .
```

### 4. Authenticate Docker with ECR
**Log in to your Amazon ECR registry:**
```bash
aws ecr get-login-password --region us-east-1 | docker login \
  --username AWS \
  --password-stdin <your-account-id>.dkr.ecr.us-east-1.amazonaws.com
```

### 5. Tag the Docker Image
**Tag the image with your ECR repository URI:**
```bash
docker tag skycast:latest \
  <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/skycast:latest
```

### 6. Push the Image to ECR
**Upload the image to Amazon ECR:**
```bash
docker push <your-account-id>.dkr.ecr.us-east-1.amazonaws.com/skycast:latest
```

### 7. Set Up Terraform Remote State Backend
**Create the S3 bucket:**
```bash
aws s3api create-bucket --bucket skycast-terraform-state --region us-east-1
```

**Create the DynamoDB table for state locking:**
```bash
aws dynamodb create-table \
  --table-name skycast-terraform-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1
```

### 8. Deploy Infrastructure with Terraform
**Initialize Terraform:**
```bash
cd terraform
terraform init
```

**Preview the infrastructure:**
```bash
terraform plan
```

**Deploy to AWS:**
```bash
terraform apply
```

### 9. Add GitHub Secrets
**Go to your repo Settings → Secrets and variables → Actions and add:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `OPENWEATHER_API_KEY`

### 10. Verify Deployment
**After terraform apply copy the ALB URL from the output and test:**
```bash
# Health check
curl http://<alb-url>/health

# Weather API
curl http://<alb-url>/api/weather?city=London
```

Visit the ALB URL in your browser to see the full Skycast UI.

---

## How to Destroy
**Tear down all AWS infrastructure to avoid charges:**
```bash
cd terraform
terraform destroy
```

---

## Tools Used

| Tool | Purpose |
|------|---------|
| Python 3.11 | Application runtime |
| Flask | Web framework |
| Gunicorn | Production WSGI server |
| Docker | Containerization |
| Amazon ECR | Container image registry |
| Amazon ECS Fargate | Serverless container hosting |
| Application Load Balancer | Traffic routing and health checks |
| Amazon CloudWatch | Container logging and monitoring |
| Amazon S3 | Terraform remote state storage |
| Amazon VPC | Network isolation |
| AWS IAM | Permissions and security |
| Terraform | Infrastructure as Code |
| GitHub Actions | CI/CD automation |
| OpenWeatherMap API | Real-time weather data |