# Kronos AI - API Integration Guide

**Version:** 1.0  
**Date:** 2026-01-26

---

## Overview

This document provides integration points for connecting Kronos AI components to external services (email providers, CRMs, databases, LLM APIs, etc.).

---

## Architecture

```
┌─────────────────┐
│  Kronos Core    │
│  (Flask/FastAPI)│
└────────┬────────┘
         │
    ┌────┴─────┬─────────┬────────────┬──────────┐
    │          │         │            │          │
    v          v         v            v          v
┌────────┐ ┌──────┐ ┌──────┐ ┌────────────┐ ┌────────┐
│ Email  │ │ CRM  │ │ LLM  │ │ Database   │ │ Cron   │
│ (IMAP/ │ │(REST)│ │(API) │ │ (Postgres) │ │(Celery)│
│ Gmail) │ │      │ │      │ │            │ │        │
└────────┘ └──────┘ └──────┘ └────────────┘ └────────┘
```

---

## 1. Email Integration

### Gmail API

**Setup:**
```python
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def connect_gmail(credentials_path: str):
    """Connect to Gmail API"""
    creds = Credentials.from_authorized_user_file(credentials_path)
    service = build('gmail', 'v1', credentials=creds)
    return service
```

**Fetch Unread Emails:**
```python
def fetch_unread_emails(service, max_results: int = 50):
    """Fetch unread emails from inbox"""
    results = service.users().messages().list(
        userId='me',
        labelIds=['INBOX'],
        q='is:unread',
        maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    
    emails = []
    for msg in messages:
        message = service.users().messages().get(
            userId='me', 
            id=msg['id'],
            format='full'
        ).execute()
        
        emails.append(parse_gmail_message(message))
    
    return emails

def parse_gmail_message(message):
    """Parse Gmail API message format"""
    headers = {h['name']: h['value'] for h in message['payload']['headers']}
    
    return {
        "id": message['id'],
        "from": headers.get('From', ''),
        "to": headers.get('To', ''),
        "subject": headers.get('Subject', ''),
        "body": extract_body(message['payload']),
        "timestamp": headers.get('Date', '')
    }
```

**Auto-Tagging:**
```python
def apply_gmail_labels(service, message_id: str, labels: List[str]):
    """Apply labels to Gmail message"""
    # Create labels if they don't exist
    existing_labels = service.users().labels().list(userId='me').execute()
    label_map = {l['name']: l['id'] for l in existing_labels['labels']}
    
    label_ids = []
    for label_name in labels:
        if label_name not in label_map:
            # Create new label
            new_label = service.users().labels().create(
                userId='me',
                body={'name': label_name, 'messageListVisibility': 'show'}
            ).execute()
            label_ids.append(new_label['id'])
        else:
            label_ids.append(label_map[label_name])
    
    # Apply labels
    service.users().messages().modify(
        userId='me',
        id=message_id,
        body={'addLabelIds': label_ids}
    ).execute()
```

**Integration with Email Categorizer:**
```python
from email_categorizer import EmailCategorizer, EmailMessage, integrate_with_email_provider

def process_gmail_inbox(credentials_path: str, industry: str = "tax"):
    """Process Gmail inbox with Kronos AI"""
    service = connect_gmail(credentials_path)
    emails = fetch_unread_emails(service)
    
    categorizer = EmailCategorizer(industry)
    
    for email in emails:
        # Classify
        result = integrate_with_email_provider(email, industry)
        
        # Apply labels
        tags = [result.category] + result.flags
        apply_gmail_labels(service, email['id'], tags)
        
        # Mark as read if spam
        if result.category == "spam":
            service.users().messages().modify(
                userId='me',
                id=email['id'],
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
        
        print(f"Processed: {email['subject']} → {result.category}")
```

### IMAP (Universal Email)

**For non-Gmail providers (Outlook, ProtonMail, etc.):**
```python
import imaplib
import email
from email.header import decode_header

def connect_imap(host: str, username: str, password: str):
    """Connect to IMAP server"""
    imap = imaplib.IMAP4_SSL(host)
    imap.login(username, password)
    return imap

def fetch_imap_emails(imap, folder: str = "INBOX", limit: int = 50):
    """Fetch emails via IMAP"""
    imap.select(folder)
    
    status, messages = imap.search(None, 'UNSEEN')
    email_ids = messages[0].split()
    
    emails = []
    for email_id in email_ids[-limit:]:
        status, msg_data = imap.fetch(email_id, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)
        
        emails.append({
            "id": email_id.decode(),
            "from": msg.get("From"),
            "to": msg.get("To"),
            "subject": decode_header(msg.get("Subject"))[0][0],
            "body": extract_email_body(msg),
            "timestamp": msg.get("Date")
        })
    
    return emails
```

**Example: Outlook.com**
```python
imap = connect_imap(
    host="outlook.office365.com",
    username="laura@domain.com",
    password="app_password"
)
emails = fetch_imap_emails(imap)
```

---

## 2. CRM Integration

### Leads → CRM (e.g., HubSpot, Salesforce)

**HubSpot Example:**
```python
import requests

HUBSPOT_API_KEY = "your_api_key"
HUBSPOT_API_URL = "https://api.hubapi.com"

def create_hubspot_contact(lead_data: dict, lead_score: float):
    """Create or update contact in HubSpot"""
    
    properties = {
        "email": lead_data["email"],
        "firstname": lead_data["first_name"],
        "lastname": lead_data["last_name"],
        "phone": lead_data["phone"],
        "hs_lead_status": "qualified" if lead_score >= 70 else "unqualified",
        "kronos_lead_score": lead_score,
        "kronos_qualified_date": datetime.now().isoformat()
    }
    
    response = requests.post(
        f"{HUBSPOT_API_URL}/crm/v3/objects/contacts",
        headers={
            "Authorization": f"Bearer {HUBSPOT_API_KEY}",
            "Content-Type": "application/json"
        },
        json={"properties": properties}
    )
    
    return response.json()

def sync_lead_to_crm(lead_id: str, qualification_result):
    """Sync qualified lead to CRM"""
    
    # Fetch lead data from database
    lead = database.get_lead(lead_id)
    
    # Create in CRM
    crm_contact = create_hubspot_contact(lead, qualification_result.percentage)
    
    # Store CRM ID for future updates
    database.update_lead(lead_id, crm_id=crm_contact['id'])
    
    return crm_contact
```

**Generic REST API Pattern:**
```python
def sync_to_generic_crm(api_url: str, api_key: str, lead_data: dict):
    """Generic CRM sync (adapt headers/payload per provider)"""
    
    response = requests.post(
        f"{api_url}/leads",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json=lead_data
    )
    
    if response.status_code == 201:
        return response.json()
    else:
        raise Exception(f"CRM sync failed: {response.text}")
```

---

## 3. LLM Integration (OpenAI / Claude)

### OpenAI GPT-4

**Setup:**
```python
import openai

openai.api_key = "your_openai_api_key"

def call_gpt4(prompt: str, max_tokens: int = 500) -> str:
    """Call GPT-4 API"""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant for a tax professional."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.3  # Lower = more deterministic
    )
    
    return response.choices[0].message.content
```

**Integration with Email Categorizer (fallback):**
```python
from email_categorizer import generate_gpt_classification_prompt, parse_gpt_response

def classify_with_gpt_fallback(email: EmailMessage, base_confidence: float):
    """Use GPT-4 for low-confidence classifications"""
    
    if base_confidence < 0.6:
        prompt = generate_gpt_classification_prompt(email)
        gpt_response = call_gpt4(prompt)
        category, reasoning = parse_gpt_response(gpt_response)
        
        return category, 0.85, reasoning  # GPT gets higher confidence
    
    return None  # Use base classification
```

**Text Embeddings (for similarity search):**
```python
def get_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """Get text embedding from OpenAI"""
    response = openai.Embedding.create(
        model=model,
        input=text
    )
    return response['data'][0]['embedding']

def find_similar_emails(query_email: str, email_database: List[dict]):
    """Find similar historical emails"""
    query_embedding = get_embedding(query_email)
    
    similarities = []
    for email in email_database:
        email_embedding = get_embedding(email['body'])
        similarity = cosine_similarity(query_embedding, email_embedding)
        similarities.append((email, similarity))
    
    # Return top 5 most similar
    return sorted(similarities, key=lambda x: -x[1])[:5]
```

### Anthropic Claude

**Setup:**
```python
import anthropic

client = anthropic.Anthropic(api_key="your_anthropic_api_key")

def call_claude(prompt: str, max_tokens: int = 1000) -> str:
    """Call Claude API"""
    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=max_tokens,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text
```

**Use Case: Generate Daily Digest Summaries**
```python
def generate_section_summary(messages: List[Message]) -> str:
    """Use Claude to summarize a section of messages"""
    
    prompt = f"""Summarize these {len(messages)} messages for a tax professional's morning digest.
Be concise (2-3 sentences). Highlight urgent items and action needed.

Messages:
"""
    
    for msg in messages[:10]:  # Limit to avoid token limits
        prompt += f"\n- From {msg.from_name}: {msg.subject} - {msg.body[:100]}..."
    
    prompt += "\n\nSummary:"
    
    return call_claude(prompt, max_tokens=200)
```

---

## 4. Database Integration

### PostgreSQL Schema

**Core Tables:**
```sql
-- Leads
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    phone VARCHAR(50),
    source VARCHAR(100),
    status VARCHAR(50) DEFAULT 'new',
    lead_score FLOAT,
    qualified BOOLEAN DEFAULT FALSE,
    responses JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Clients
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    lead_id UUID REFERENCES leads(id),
    client_since DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    lifetime_value DECIMAL(10,2) DEFAULT 0,
    retention_risk_score FLOAT,
    last_interaction TIMESTAMP,
    custom_fields JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Messages
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    channel VARCHAR(50) NOT NULL,
    from_contact VARCHAR(255),
    to_contact VARCHAR(255),
    subject TEXT,
    body TEXT,
    category VARCHAR(100),
    flags TEXT[],
    is_read BOOLEAN DEFAULT FALSE,
    thread_id UUID,
    client_id UUID REFERENCES clients(id),
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Retention predictions
CREATE TABLE retention_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID REFERENCES clients(id),
    risk_level VARCHAR(50),
    risk_score FLOAT,
    confidence FLOAT,
    signals JSONB,
    recommended_actions TEXT[],
    predicted_at TIMESTAMP DEFAULT NOW()
);

-- Daily digests
CREATE TABLE digests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    date DATE NOT NULL,
    total_messages INT,
    urgent_count INT,
    sections JSONB,
    delivered_at TIMESTAMP,
    opened_at TIMESTAMP,
    user_rating INT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

**ORM Integration (SQLAlchemy):**
```python
from sqlalchemy import create_engine, Column, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

Base = declarative_base()

class Lead(Base):
    __tablename__ = 'leads'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, nullable=False)
    name = Column(String)
    lead_score = Column(Float)
    qualified = Column(Boolean, default=False)
    responses = Column(JSON)
    created_at = Column(DateTime, default=datetime.now)

# Create engine
engine = create_engine('postgresql://user:password@localhost/kronos')
Base.metadata.create_all(engine)

# Session
Session = sessionmaker(bind=engine)
session = Session()

# Create lead
lead = Lead(email="client@example.com", name="John Doe", lead_score=85.0)
session.add(lead)
session.commit()

# Query leads
qualified_leads = session.query(Lead).filter(Lead.qualified == True).all()
```

---

## 5. Scheduled Tasks (Celery)

**Setup:**
```python
from celery import Celery
from celery.schedules import crontab

app = Celery('kronos', broker='redis://localhost:6379/0')

# Configure periodic tasks
app.conf.beat_schedule = {
    'generate-daily-digest': {
        'task': 'tasks.generate_daily_digest',
        'schedule': crontab(hour=6, minute=0),  # 6am daily
    },
    'check-retention-risk': {
        'task': 'tasks.check_retention_risk',
        'schedule': crontab(day_of_week=1, hour=8),  # Monday 8am
    },
    'process-inbox': {
        'task': 'tasks.process_inbox',
        'schedule': 300.0,  # Every 5 minutes
    }
}

@app.task
def generate_daily_digest(user_id: str):
    """Generate and send daily digest"""
    from daily_digest import DigestGenerator
    
    # Fetch messages
    messages = fetch_user_messages_since_yesterday(user_id)
    
    # Generate digest
    generator = DigestGenerator(industry="tax")
    digest = generator.generate(messages)
    
    # Send email
    send_digest_email(user_id, digest)

@app.task
def check_retention_risk():
    """Check all clients for retention risk"""
    from retention_predictor import RetentionPredictor, BatchRetentionAnalysis
    
    predictor = RetentionPredictor("tax")
    batch = BatchRetentionAnalysis(predictor)
    
    # Fetch all clients
    clients = fetch_all_clients()
    
    # Analyze
    predictions = batch.analyze_client_base(clients)
    
    # Alert on critical cases
    critical = [p for p in batch.predictions if p.risk_level == RiskLevel.CRITICAL]
    if critical:
        send_alert_email(f"{len(critical)} clients at CRITICAL retention risk")

@app.task
def process_inbox():
    """Process email inbox"""
    process_gmail_inbox("credentials.json")
```

**Start Celery:**
```bash
# Worker
celery -A tasks worker --loglevel=info

# Beat scheduler
celery -A tasks beat --loglevel=info
```

---

## 6. REST API (FastAPI)

**Expose AI components as REST API:**

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from lead_qualifier import integrate_with_lead_form
from email_categorizer import integrate_with_email_provider
from retention_predictor import RetentionPredictor

app = FastAPI(title="Kronos AI API")

# Lead Qualification Endpoint
class LeadRequest(BaseModel):
    lead_id: str
    industry: str
    responses: dict

@app.post("/api/qualify-lead")
def qualify_lead(request: LeadRequest):
    """Qualify a lead"""
    try:
        score = integrate_with_lead_form(request.responses, request.industry)
        return {
            "lead_id": score.lead_id,
            "qualified": score.qualified,
            "score": score.percentage,
            "flags": score.flags
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Email Classification Endpoint
class EmailRequest(BaseModel):
    email_id: str
    from_email: str
    subject: str
    body: str
    industry: str = "tax"

@app.post("/api/categorize-email")
def categorize_email(request: EmailRequest):
    """Categorize an email"""
    try:
        raw_email = {
            "id": request.email_id,
            "from": request.from_email,
            "subject": request.subject,
            "body": request.body,
            "timestamp": datetime.now().isoformat()
        }
        
        result = integrate_with_email_provider(raw_email, request.industry)
        
        return {
            "category": result.category,
            "confidence": result.confidence,
            "flags": result.flags,
            "suggested_action": result.suggested_action
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Retention Risk Endpoint
@app.get("/api/retention-risk/{client_id}")
def get_retention_risk(client_id: str, industry: str = "tax"):
    """Get retention risk for a client"""
    try:
        # Fetch client profile from database
        profile = fetch_client_profile(client_id)
        
        predictor = RetentionPredictor(industry)
        prediction = predictor.predict(profile)
        
        return {
            "client_id": prediction.client_id,
            "risk_level": prediction.risk_level.value,
            "risk_score": prediction.risk_score,
            "recommended_actions": prediction.recommended_actions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

**Run API:**
```bash
uvicorn api:app --reload --port 8000
```

**Example API Call:**
```bash
curl -X POST http://localhost:8000/api/qualify-lead \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "L001",
    "industry": "tax",
    "responses": {
      "tax_services": "Business tax return",
      "price_sensitivity": "Quality service & expertise"
    }
  }'
```

---

## 7. Webhooks (for real-time integrations)

**Receive webhook from website form:**
```python
@app.post("/webhook/lead-form")
async def handle_lead_form(request: Request):
    """Handle website form submission"""
    data = await request.json()
    
    # Qualify lead
    score = integrate_with_lead_form(data, industry="tax")
    
    # Send automated response
    if score.qualified:
        send_email(
            to=data["email"],
            subject="Thank you for your inquiry",
            body=generate_followup_message(score, "tax")
        )
    
    # Store in database
    save_lead(data, score)
    
    return {"status": "processed", "qualified": score.qualified}
```

---

## Environment Variables

**`.env` file:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/kronos

# Email
GMAIL_CREDENTIALS_PATH=/path/to/credentials.json
IMAP_HOST=outlook.office365.com
IMAP_USER=laura@domain.com
IMAP_PASSWORD=app_password

# LLM APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# CRM
HUBSPOT_API_KEY=your_hubspot_key

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0

# App
INDUSTRY=tax
DEBUG=False
```

---

*Integration is key. Start with one provider, expand as needed.*
