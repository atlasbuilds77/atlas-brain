# Kronos Core Engine - Development Guide

## Quick Start for Developers

### 1. First-Time Setup

```bash
cd memory/projects/kronos/backend

# Easy start (runs setup automatically)
./start.sh

# Or manual setup:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
python main.py
```

### 2. Environment Setup

**Minimum .env configuration for local development:**

```env
# Database (install PostgreSQL first)
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/kronos

# Security (generate random strings)
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# Optional for full features:
# - AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY (for file uploads)
# - IMAP credentials (for email ingestion)
# - OPENAI_API_KEY (for enhanced AI features)
```

### 3. Database Setup

**Install PostgreSQL:**

```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt install postgresql
sudo service postgresql start

# Create database
createdb kronos
```

**Database is auto-initialized** on first run (tables created automatically).

### 4. Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app

# Specific test file
pytest tests/test_main.py -v
```

### 5. API Testing

**Using curl:**

```bash
# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"test123","role":"client"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Use token (replace TOKEN with actual token)
curl -X GET http://localhost:8000/api/leads \
  -H "Authorization: Bearer TOKEN"
```

**Using Swagger UI (recommended):**
- Open http://localhost:8000/docs
- Click "Authorize" button
- Login to get token
- Paste token in authorization dialog
- Test all endpoints interactively

### 6. Running Background Tasks

**Start Celery worker (for email ingestion, etc.):**

```bash
# Start Redis (required for Celery)
redis-server

# In another terminal:
celery -A app.tasks.celery_tasks worker --loglevel=info

# In another terminal (for scheduled tasks):
celery -A app.tasks.celery_tasks beat --loglevel=info
```

### 7. Development Workflow

```bash
# 1. Make changes to code
# 2. Server auto-reloads (if DEBUG=true)
# 3. Test endpoint in /docs
# 4. Check logs
# 5. Commit changes

git add .
git commit -m "Add feature X"
```

### 8. Code Structure

**Adding a new endpoint:**

```python
# 1. Create model (app/models/mymodel.py)
from app.db.session import Base
from sqlalchemy import Column, Integer, String

class MyModel(Base):
    __tablename__ = "mymodel"
    id = Column(Integer, primary_key=True)
    name = Column(String)

# 2. Create schema (app/schemas/mymodel.py)
from pydantic import BaseModel

class MyModelCreate(BaseModel):
    name: str

# 3. Create endpoint (app/api/v1/endpoints/mymodel.py)
from fastapi import APIRouter
router = APIRouter()

@router.post("")
async def create_mymodel(data: MyModelCreate):
    # Implementation
    pass

# 4. Register in router (app/api/v1/router.py)
from app.api.v1.endpoints import mymodel
api_router.include_router(mymodel.router, prefix="/mymodel", tags=["MyModel"])
```

### 9. Common Issues

**Issue: Database connection error**
```
Solution: Ensure PostgreSQL is running and DATABASE_URL is correct
Check: psql -U postgres -d kronos
```

**Issue: Import errors**
```
Solution: Activate virtual environment
source venv/bin/activate
```

**Issue: "Module not found"**
```
Solution: Install dependencies
pip install -r requirements.txt
```

**Issue: Redis connection error (Celery)**
```
Solution: Start Redis server
redis-server
```

### 10. Useful Commands

```bash
# View logs (if using Docker)
docker-compose logs -f api

# Access database
psql -U postgres -d kronos

# Clear Redis cache
redis-cli FLUSHALL

# Check running processes
ps aux | grep python

# Stop all Python processes
pkill -f python
```

### 11. Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | PostgreSQL connection string |
| SECRET_KEY | Yes | Auto-generated | App secret key |
| JWT_SECRET_KEY | Yes | Auto-generated | JWT signing key |
| REDIS_URL | No | redis://localhost:6379/0 | Redis connection |
| AWS_ACCESS_KEY_ID | No | - | AWS S3 access key |
| IMAP_USERNAME | No | - | Email ingestion username |
| OPENAI_API_KEY | No | - | OpenAI API key |

### 12. Production Deployment

**Docker (recommended):**
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Manual deployment:**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment
export ENVIRONMENT=production
export DATABASE_URL=postgresql+asyncpg://...

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### 13. Debugging

**Enable debug logging:**
```env
LOG_LEVEL=DEBUG
DEBUG=true
```

**Use IPython for interactive debugging:**
```bash
pip install ipython
ipython

from app.models.lead import Lead
from app.db.session import AsyncSessionLocal
# ... test code
```

**Check health:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/health/ready
```

### 14. Performance Tips

- Use pagination on all list endpoints
- Add database indexes for frequently queried fields
- Enable Redis caching for repeated queries
- Use connection pooling (already configured)
- Monitor with Sentry in production

### 15. Security Best Practices

- Never commit `.env` file
- Use strong, unique SECRET_KEY and JWT_SECRET_KEY
- Enable HTTPS in production
- Set proper CORS_ORIGINS
- Use rate limiting (already enabled)
- Regularly update dependencies: `pip install -U -r requirements.txt`

---

## Quick Reference

**Start server:** `python main.py` or `./start.sh`  
**API docs:** http://localhost:8000/docs  
**Health check:** http://localhost:8000/health  
**Run tests:** `pytest`  
**Format code:** `black app/`  
**Lint code:** `flake8 app/`  

---

For more details, see:
- README.md - Full documentation
- API_DOCUMENTATION.md - Endpoint reference
- BUILD_SUMMARY.md - What was built
