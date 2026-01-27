# Kronos Core Engine - Backend API

**Version:** 1.0.0  
**Tech Stack:** Python FastAPI, PostgreSQL, Redis, S3  
**Architecture:** Modular, industry-agnostic core engine

---

## 🎯 Overview

Kronos Core Engine is a universal backend platform designed to power industry-specific applications (tax, law, medical, etc.). This is **Layer 1** - the industry-agnostic foundation that handles:

- User authentication & sessions
- Lead and client management
- Message handling and categorization
- File storage with encryption
- Analytics and reporting
- Email ingestion (IMAP)
- AI-powered scoring and risk assessment

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- AWS S3 (or compatible storage)

### Installation

```bash
# Clone repository
cd memory/projects/kronos/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your configuration

# Run database migrations (if using Alembic)
alembic upgrade head

# Start server
python main.py
```

Server will start on `http://localhost:8000`

API documentation available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/      # API endpoints
│   │       │   ├── auth.py     # Authentication
│   │       │   ├── leads.py    # Lead management
│   │       │   ├── clients.py  # Client management
│   │       │   ├── messages.py # Message handling
│   │       │   ├── files.py    # File storage
│   │       │   └── analytics.py # Analytics
│   │       └── router.py       # Main router
│   ├── core/
│   │   ├── config.py          # Configuration
│   │   ├── security.py        # Auth & encryption
│   │   └── logging_config.py  # Logging setup
│   ├── db/
│   │   ├── base.py           # Base model
│   │   └── session.py        # Database session
│   ├── models/               # SQLAlchemy models
│   │   ├── user.py
│   │   ├── lead.py
│   │   ├── client.py
│   │   ├── message.py
│   │   ├── file.py
│   │   ├── task.py
│   │   └── analytics.py
│   ├── schemas/              # Pydantic schemas
│   │   ├── user.py
│   │   ├── lead.py
│   │   ├── client.py
│   │   ├── message.py
│   │   ├── file.py
│   │   └── analytics.py
│   ├── services/             # Business logic
│   │   ├── ai_service.py     # AI scoring/categorization
│   │   ├── storage_service.py # S3 file storage
│   │   └── email_service.py  # IMAP/SMTP
│   ├── tasks/
│   │   └── celery_tasks.py   # Background tasks
│   └── utils/
│       └── helpers.py        # Utility functions
├── main.py                   # Application entry point
├── requirements.txt          # Python dependencies
└── .env.example             # Environment template
```

---

## 🔐 Authentication

Kronos uses JWT (JSON Web Tokens) for authentication.

### Register a new user

```bash
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123",
  "role": "client"
}
```

### Login

```bash
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Using the token

Include the access token in the `Authorization` header:

```bash
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 📋 API Endpoints

### Authentication (`/api/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login user |
| POST | `/auth/refresh` | Refresh access token |
| GET | `/auth/me` | Get current user |

### Leads (`/api/leads`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/leads` | List all leads (paginated) |
| POST | `/leads` | Create new lead |
| GET | `/leads/{id}` | Get lead by ID |
| PUT | `/leads/{id}` | Update lead |
| DELETE | `/leads/{id}` | Delete lead |
| POST | `/leads/{id}/score` | Calculate AI lead score |

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 50, max: 100)
- `status`: Filter by status (new, contacted, qualified, converted, dead)
- `search`: Search by name/email/phone

### Clients (`/api/clients`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/clients` | List all clients (paginated) |
| POST | `/clients` | Create new client |
| GET | `/clients/{id}` | Get client by ID |
| PUT | `/clients/{id}` | Update client |
| DELETE | `/clients/{id}` | Delete client |
| POST | `/clients/{id}/risk` | Assess retention risk |

### Messages (`/api/messages`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/messages` | List all messages (paginated) |
| POST | `/messages` | Create new message |
| GET | `/messages/{id}` | Get message by ID |
| PUT | `/messages/{id}` | Update message |
| DELETE | `/messages/{id}` | Delete message |
| POST | `/messages/categorize` | Categorize message with AI |

### Files (`/api/files`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/files` | List all files (paginated) |
| POST | `/files/upload` | Upload file |
| GET | `/files/{id}` | Get file metadata |
| GET | `/files/{id}/download` | Get download URL |
| PUT | `/files/{id}` | Update file metadata |
| DELETE | `/files/{id}` | Delete file |

### Analytics (`/api/analytics`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/analytics/dashboard` | Get dashboard metrics |

---

## 🤖 AI Features

### Lead Scoring

Automatically scores leads (0-100) based on:
- Contact information completeness
- Source quality (referral > website > other)
- Engagement indicators
- Custom fields

```bash
POST /api/leads/{id}/score

# Response:
{
  "lead_id": 123,
  "score": 85.5,
  "factors": {
    "has_email": 20,
    "has_phone": 20,
    "source_quality": 30,
    "has_notes": 10
  },
  "recommendation": "High priority - contact immediately"
}
```

### Message Categorization

Automatically categorizes incoming messages:
- **PROSPECTIVE**: New lead inquiries
- **CLIENT**: Active client communication
- **OFFICE**: Internal/admin
- **SPAM**: Spam/marketing
- **OTHER**: Unknown

Also provides:
- Sentiment analysis (-1 to 1)
- Priority score (1-5)
- Auto-generated summary

### Client Risk Assessment

Predicts client churn risk (0-1) based on:
- Time since last interaction
- Missed followups
- Lifetime value
- Client status

---

## 📦 File Storage

Files are stored in S3-compatible storage with:
- Automatic encryption for sensitive files
- Retention policies (auto-delete after X years)
- Pre-signed download URLs (expire after 1 hour)
- Download tracking

**Upload Example:**

```bash
POST /api/files/upload
Content-Type: multipart/form-data

file: [binary file data]
client_id: 123
category: tax_return
year: 2024
is_sensitive: true
retention_years: 7
```

---

## 📧 Email Integration

### IMAP Ingestion

Kronos automatically fetches emails from your inbox:

1. Configure IMAP settings in `.env`:
```env
IMAP_HOST=imap.gmail.com
IMAP_PORT=993
IMAP_USERNAME=your-email@example.com
IMAP_PASSWORD=your-app-password
```

2. Start Celery worker:
```bash
celery -A app.tasks.celery_tasks worker --loglevel=info
```

3. Start Celery beat (scheduler):
```bash
celery -A app.tasks.celery_tasks beat --loglevel=info
```

Emails are fetched every 5 minutes and automatically:
- Saved to database
- Categorized using AI
- Linked to clients/leads (if possible)

### SMTP Sending

Send emails programmatically:

```python
from app.services.email_service import EmailService

email_service = EmailService()
await email_service.send_email(
    to_address="client@example.com",
    subject="Welcome to Kronos",
    body="Plain text body",
    html_body="<p>HTML body</p>"
)
```

---

## 🔒 Security Features

### JWT Authentication
- Access tokens (30 min expiry)
- Refresh tokens (7 day expiry)
- Role-based access control (admin, client, lead)

### Encryption
- File encryption at rest
- Sensitive data encryption (uses Fernet)
- HTTPS/TLS for transit

### WISP Compliance
- Audit logging
- Data retention policies
- Secure password hashing (bcrypt)

### Rate Limiting
- 60 requests per minute (configurable)
- Per-IP tracking

---

## 📊 Analytics & Monitoring

### Dashboard Metrics

```bash
GET /api/analytics/dashboard

# Response:
{
  "total_leads": 245,
  "new_leads_this_month": 42,
  "lead_conversion_rate": 18.5,
  "avg_lead_score": 67.3,
  "total_clients": 156,
  "active_clients": 142,
  "churned_clients": 8,
  "avg_lifetime_value": 3250.00,
  "unread_messages": 12,
  "avg_response_time_hours": 2.5,
  "messages_today": 34,
  "high_risk_clients": 5,
  "clients_needing_followup": 8,
  "generated_at": "2024-01-26T12:00:00Z"
}
```

### Logging

Structured logging with `structlog`:
- JSON format in production
- Console format in development
- Integrates with Sentry (if configured)

---

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis

  db:
    image: postgres:14
    environment:
      POSTGRES_DB: kronos
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

  worker:
    build: .
    command: celery -A app.tasks.celery_tasks worker --loglevel=info
    env_file:
      - .env
    depends_on:
      - db
      - redis

  beat:
    build: .
    command: celery -A app.tasks.celery_tasks beat --loglevel=info
    env_file:
      - .env
    depends_on:
      - redis

volumes:
  postgres_data:
  redis_data:
```

### Production Checklist

- [ ] Set strong `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Configure production database
- [ ] Set up S3 bucket and credentials
- [ ] Configure email (IMAP/SMTP)
- [ ] Set `ENVIRONMENT=production`
- [ ] Enable HTTPS/TLS
- [ ] Configure Sentry for error tracking
- [ ] Set up backups (database, files)
- [ ] Configure CORS for your domain
- [ ] Set up monitoring (health checks)

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx

# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

---

## 📚 Additional Documentation

- **Architecture**: See `memory/projects/kronos-architecture.md`
- **API Spec**: OpenAPI spec at `/api/openapi.json`
- **Swagger UI**: Interactive API docs at `/docs`

---

## 🤝 Contributing

This is a pilot project for Laura's tax business. Future enhancements:

1. Industry modules (tax, law, medical)
2. Multi-tenant support
3. Advanced AI features (GPT-4 integration)
4. Webhooks and integrations
5. Mobile app support

---

## 📄 License

Proprietary - Kronos Platform © 2024

---

## 🆘 Support

For issues or questions:
- Check logs: `tail -f logs/app.log`
- Health check: `GET /health`
- Readiness check: `GET /health/ready`

---

**Built with ❤️ for scalable, modular industry platforms**
