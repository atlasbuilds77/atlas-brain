# =====================================================
# KRONOS DEPLOYMENT DOCUMENTATION
# =====================================================
# Complete reference for Kronos infrastructure
# =====================================================

## Overview

This directory contains all deployment configuration and documentation for Kronos:

```
deployment/
├── docker/                    # Docker configurations
│   ├── Dockerfile.backend     # Backend API container
│   ├── Dockerfile.frontend    # Frontend Next.js container
│   ├── Dockerfile.worker      # Celery worker container
│   └── nginx/                 # Nginx reverse proxy
│       └── nginx.conf
├── terraform/                 # Infrastructure as Code
│   ├── main.tf               # Main AWS infrastructure
│   └── variables.tf          # Configurable variables
├── scripts/                   # Deployment scripts
│   ├── deploy.sh             # Production deployment
│   ├── rollback.sh           # Rollback procedure
│   └── smoke-test.sh         # Post-deployment tests
├── runbooks/                  # Operational guides
│   ├── deployment-runbook.md # Day-to-day operations
│   └── disaster-recovery.md  # DR procedures
├── docs/                      # Documentation
│   ├── launch-checklist.md   # Go-live checklist
│   ├── security-configuration.md  # Security controls
│   └── monitoring-alerting.md     # Observability
├── .github/workflows/         # CI/CD pipelines
│   └── ci-cd.yml             # GitHub Actions
├── docker-compose.yml         # Local development stack
├── .env.template             # Environment variables
└── README.md                 # This file
```

---

## Quick Start (Local Development)

### Prerequisites
- Docker Desktop
- Git
- AWS CLI (for deployment)

### Setup
```bash
# Clone repository
git clone https://github.com/yourorg/kronos.git
cd kronos

# Copy environment template
cp deployment/.env.template deployment/.env
# Edit .env with your values

# Start all services
cd deployment
docker-compose up -d

# View logs
docker-compose logs -f

# Access services
# - Frontend: http://localhost:3000
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - MinIO Console: http://localhost:9001
```

### Stopping Services
```bash
docker-compose down

# Remove volumes (clean slate)
docker-compose down -v
```

---

## Production Deployment

### First-Time Setup
1. Configure AWS credentials
2. Initialize Terraform
3. Deploy infrastructure
4. Configure secrets
5. Run initial deployment

```bash
# Initialize Terraform
cd terraform
terraform init
terraform workspace new production
terraform plan -var="environment=production"
terraform apply

# Configure secrets in AWS Secrets Manager
# (See security-configuration.md)

# Deploy application
cd ../scripts
./deploy.sh production
```

### Subsequent Deployments
Handled automatically via CI/CD on merge to `main`:
1. Tests run
2. Security scan
3. Docker images built
4. Images pushed to ECR
5. ECS services updated
6. Smoke tests verify

---

## Environment Configuration

### Required Secrets (AWS Secrets Manager)
- `kronos/production/app-secrets`
  - `DB_PASSWORD`
  - `SECRET_KEY`
  - `ENCRYPTION_KEY`
  - `SENDGRID_API_KEY`
  - `TWILIO_AUTH_TOKEN`
  - `OPENAI_API_KEY`

### Environment Variables
See `.env.template` for all configuration options.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        CloudFlare                            │
│                    (CDN + DDoS Protection)                   │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────┐
│                  Application Load Balancer                   │
│                      (SSL Termination)                       │
└──────────┬─────────────────────────────────────┬────────────┘
           │                                     │
┌──────────▼──────────┐             ┌───────────▼───────────┐
│   Frontend (ECS)    │             │    Backend (ECS)      │
│   Next.js           │◄───────────►│    FastAPI            │
│   Port 3000         │             │    Port 8000          │
└─────────────────────┘             └───────────┬───────────┘
                                                │
           ┌────────────────────────────────────┼────────────────┐
           │                                    │                │
┌──────────▼──────────┐             ┌───────────▼───────────┐   │
│   PostgreSQL (RDS)  │             │    Redis (ElastiCache)│   │
│   Primary Database  │             │    Cache + Queue      │   │
└─────────────────────┘             └───────────────────────┘   │
                                                                │
                                    ┌───────────────────────────▼─┐
                                    │   Celery Workers (ECS)       │
                                    │   - Email processing         │
                                    │   - Daily digest             │
                                    │   - AI tasks                 │
                                    └──────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                         S3                                   │
│   - File storage (encrypted)                                 │
│   - Terraform state                                          │
│   - Deployment artifacts                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Documents

| Document | Purpose |
|----------|---------|
| [Launch Checklist](docs/launch-checklist.md) | Go-live preparation |
| [Security Configuration](docs/security-configuration.md) | Security controls |
| [Monitoring & Alerting](docs/monitoring-alerting.md) | Observability setup |
| [Deployment Runbook](runbooks/deployment-runbook.md) | Day-to-day operations |
| [Disaster Recovery](runbooks/disaster-recovery.md) | DR procedures |

---

## Support

- **Issues**: GitHub Issues
- **Slack**: #kronos-support
- **On-Call**: PagerDuty

---

*Last Updated: 2024-01-26*
