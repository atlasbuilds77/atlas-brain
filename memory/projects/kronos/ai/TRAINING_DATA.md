# Kronos AI - Training Data Requirements

**Version:** 1.0  
**Date:** 2026-01-26

---

## Overview

This document specifies the data requirements for training, validating, and improving Kronos AI components. All components use a hybrid approach: rule-based logic (fast, deterministic) enhanced with ML/LLM when needed (adaptive, context-aware).

---

## 1. Lead Qualifier Bot

### Data Requirements

**Minimum Dataset Size:**
- 500 lead responses (200 qualified, 200 disqualified, 100 borderline)
- 50 conversational transcripts (real or simulated)

**Data Fields:**
```json
{
  "lead_id": "string",
  "industry": "tax|law|medical",
  "responses": {
    "question_id": "answer_text"
  },
  "actual_outcome": "qualified|disqualified|converted|no_show",
  "conversion_value": "float (if converted)",
  "time_to_conversion": "days",
  "feedback": "string (optional)"
}
```

**Collection Methods:**
1. **Historical lead data** - Export from existing CRM/forms
2. **Laura's pilot** - Capture all leads for 3 months
3. **Manual labeling** - Laura reviews 100 leads, marks qualified/not
4. **Feedback loop** - Track which "qualified" leads actually convert

**Labeling Guidelines:**
- **Qualified:** Serious buyer, appropriate budget, ready timeline
- **Disqualified:** Price shopper, not ready, out of scope
- **Borderline:** Could go either way, needs human judgment

**Annotation Example:**
```json
{
  "lead_id": "L001",
  "industry": "tax",
  "responses": {
    "tax_services": "Business tax return (1120/1065)",
    "price_sensitivity": "Quality service & expertise",
    "ready_to_start": "yes"
  },
  "actual_outcome": "converted",
  "conversion_value": 2500,
  "time_to_conversion": 7,
  "annotator_notes": "Great lead, referred by existing client"
}
```

### Training Process

**Phase 1: Rule-based baseline (current implementation)**
- No training needed, runs immediately
- Accuracy: ~75% (estimated)

**Phase 2: ML refinement (optional enhancement)**
- Train logistic regression on labeled dataset
- Features: response patterns, timing, channel, referral source
- Target: 85% accuracy on qualification

**Phase 3: LLM enhancement (for edge cases)**
- Use GPT-4 for borderline cases (confidence < 0.6)
- Fine-tune on 200 examples if available
- Reduces manual review by 40%

---

## 2. Email Categorizer

### Data Requirements

**Minimum Dataset Size:**
- 1,000 emails (200 per category minimum)
- Balanced distribution across categories

**Data Fields:**
```json
{
  "email_id": "string",
  "from": "email@example.com",
  "subject": "string",
  "body": "string (full text)",
  "timestamp": "ISO datetime",
  "true_category": "prospective|active_client|office|retention|spam",
  "flags": ["urgent", "needs_response", "has_attachment"],
  "manual_override": "boolean",
  "override_reason": "string"
}
```

**Collection Methods:**
1. **Email export** - Laura's inbox from past 6-12 months
2. **Manual labeling** - Laura tags 500 emails by category
3. **Active learning** - System suggests category, Laura confirms/corrects
4. **Feedback loop** - Track when Laura moves emails between folders

**Labeling Guidelines:**

| Category | Description | Examples |
|----------|-------------|----------|
| **Prospective** | New leads, pricing inquiries | "How much do you charge?" |
| **Active Client** | Ongoing work, documents, questions | "Here's my W-2" |
| **Office** | Admin, billing, scheduling | "Invoice attached" |
| **Retention** | Complaints, dissatisfaction | "Too expensive" |
| **Spam** | Marketing, solicitations | "Grow your business!" |

**Annotation Example:**
```json
{
  "email_id": "E001",
  "from": "client@example.com",
  "subject": "Quick question about my return",
  "body": "Hi Laura, when will my tax return be filed? I need it for a loan application.",
  "true_category": "active_client",
  "flags": ["needs_response", "time_sensitive"],
  "confidence_in_label": 0.95
}
```

### Training Process

**Phase 1: Keyword + pattern matching (current)**
- No training needed
- Accuracy: ~80% (estimated)

**Phase 2: Embedding-based classification**
- Use OpenAI `text-embedding-3-small`
- Cosine similarity to category prototypes
- Accuracy: ~90%

**Phase 3: Fine-tuned classifier (optional)**
- Fine-tune small BERT model on 1000 labeled emails
- Deployment: Local inference, no API costs
- Accuracy: ~95%

**Phase 4: LLM fallback**
- For low-confidence cases (< 0.7), ask GPT-4
- Prompt includes email + category definitions
- Reduces misclassification by 50%

---

## 3. Daily Digest Generator

### Data Requirements

**Minimum Dataset Size:**
- 100 daily message sets (10-50 messages each)
- User feedback on 50 digests

**Data Fields:**
```json
{
  "digest_id": "string",
  "date": "YYYY-MM-DD",
  "messages": [
    {
      "message_id": "string",
      "channel": "email|sms|web|phone",
      "from": "contact",
      "subject": "string",
      "category": "string",
      "flags": ["urgent"],
      "priority_assigned": "int (1-10)",
      "human_priority": "int (1-10, if user reordered)"
    }
  ],
  "user_feedback": {
    "rating": "int (1-5)",
    "missed_urgent": "boolean",
    "false_urgent": "boolean",
    "comments": "string"
  }
}
```

**Collection Methods:**
1. **Message logs** - Capture all incoming messages for 30 days
2. **User interaction** - Track which messages Laura opens first
3. **Feedback form** - Daily quick survey: "Was this digest helpful?"
4. **A/B testing** - Try different priority orders, measure engagement

**Training Process:**

**Phase 1: Rule-based priority (current)**
- Industry-specific priority rules
- No training needed

**Phase 2: Learning from user behavior**
- Track which emails user opens first (implicit feedback)
- Adjust priority weights based on user actions
- Personalization: Laura's priorities ≠ another tax pro's

**Phase 3: Contextual prioritization**
- LLM summarizes each message section
- "Here are the 3 IRS letters that need immediate response..."
- Saves 5-10 minutes every morning

---

## 4. Retention Predictor

### Data Requirements

**Minimum Dataset Size:**
- 200 clients with 2+ years history
- 50 churned clients (with churn date)
- 150 retained clients

**Data Fields:**
```json
{
  "client_id": "string",
  "industry": "tax|law",
  "client_since": "date",
  "churned": "boolean",
  "churn_date": "date (if churned)",
  "churn_reason": "string (if known)",
  
  "engagement_metrics": {
    "last_interaction": "date",
    "interaction_frequency": "float (per month)",
    "response_time_hours": "float",
    "messages_sent": "int",
    "messages_received": "int"
  },
  
  "service_metrics": {
    "projects_completed": "int",
    "projects_cancelled": "int",
    "lifetime_value": "float",
    "payment_history_score": "float (0-1)",
    "avg_payment_delay_days": "float"
  },
  
  "sentiment_metrics": {
    "complaint_count": "int",
    "positive_feedback_count": "int",
    "support_tickets": "int",
    "nps_score": "int (-100 to 100, if available)"
  },
  
  "industry_specific": {
    "tax": {
      "years_not_returned": "int",
      "price_complaints": "int",
      "organizer_completion_rate": "float",
      "extensions_filed": "int"
    },
    "law": {
      "case_outcome": "won|lost|settled",
      "billing_disputes": "int",
      "communication_complaints": "int"
    }
  }
}
```

**Collection Methods:**
1. **Client database export** - Pull all historical client data
2. **Churn identification** - Mark clients who haven't returned in 2+ years
3. **Exit interviews** - Ask churned clients why they left
4. **Surveys** - Annual satisfaction surveys for active clients

**Labeling Guidelines:**

**Churned = TRUE if:**
- Tax: Client didn't return for 2+ consecutive years
- Law: Client terminated representation or didn't return for new matter
- All: Explicitly stated switching to competitor

**Not churned despite inactivity:**
- Client communicated they're taking a break
- Circumstantial (moved, retired, etc.)
- One-time project (expected no repeat business)

### Training Process

**Phase 1: Rule-based signals (current)**
- Signal detection based on thresholds
- No training needed
- Accuracy: ~70% (identify most critical cases)

**Phase 2: Logistic regression**
- Train on 200 labeled clients
- Features: all metrics above
- Output: Churn probability
- Accuracy: ~80%

**Phase 3: Random Forest (better for non-linear patterns)**
- Handles interactions between features
- Example: High value + low engagement = different risk than low value + low engagement
- Accuracy: ~85%

**Phase 4: Time-series model (advanced)**
- Track engagement trends over time
- Predict churn 3-6 months in advance
- Requires 1+ year of historical data per client

---

## Data Privacy & Compliance

### WISP Requirements (Tax Industry)

**Email Data:**
- 3-year retention minimum for all client communications
- Encrypted storage (AES-256)
- Access logging (who accessed what, when)
- Secure deletion after retention period

**PII Handling:**
- No PII in training data unless anonymized
- Client names → "Client_001"
- SSNs, account numbers → Redacted
- Email addresses → Hashed (for matching only)

**Anonymization Script:**
```python
def anonymize_email(email: dict) -> dict:
    return {
        "email_id": email["id"],
        "from": hash_email(email["from"]),  # One-way hash
        "subject": redact_pii(email["subject"]),
        "body": redact_pii(email["body"]),
        "category": email["category"],  # Safe
        "flags": email["flags"]  # Safe
    }
```

### HIPAA (Medical Industry)

If expanding to medical:
- All training data must be de-identified (Safe Harbor method)
- No PHI in cloud-based LLM APIs
- Local model training only, or use HIPAA-compliant AI providers

---

## Data Collection Tools

### 1. Email Export Script
```bash
# Export Gmail to JSON (using Google Takeout or API)
python scripts/export_gmail.py --label "Inbox" --since 2024-01-01 --output data/emails.json
```

### 2. Manual Labeling Interface
```
Simple web UI:
- Show email subject + preview
- Buttons: [Prospective] [Client] [Office] [Retention] [Spam]
- Keyboard shortcuts: 1-5
- Progress: 47 / 500 labeled
```

### 3. Feedback Collection
```
Add to daily digest email:
"Was this digest helpful? [👍 Yes] [👎 No]"
Track: clicked_yes, clicked_no, time_to_open, messages_opened
```

---

## Continuous Improvement

**Monthly:**
1. Export last month's data
2. Label any corrections (user moved emails, edited categories)
3. Retrain models with new data
4. A/B test: old model vs new model
5. Deploy if new model is 5%+ better

**Quarterly:**
1. User satisfaction survey
2. Review false positives/negatives
3. Add new categories if needed (e.g., "tax planning" subcategory)
4. Update industry-specific rules based on feedback

**Annually:**
1. Full model retraining with year's data
2. Consider upgrading to newer LLM (GPT-5, Claude 4, etc.)
3. Benchmark against industry standards

---

## Success Metrics

| Component | Baseline | Target | Measurement |
|-----------|----------|--------|-------------|
| Lead Qualifier | 75% accuracy | 85% accuracy | % correctly classified |
| Email Categorizer | 80% accuracy | 90% accuracy | % correctly classified |
| Daily Digest | N/A | 4.5/5 rating | User satisfaction survey |
| Retention Predictor | 70% accuracy | 80% accuracy | % churn correctly predicted |

**Business Metrics:**
- Time saved: 2-3 hours/day (Laura's goal)
- Lead conversion: +20% (filter out bad leads, focus on good ones)
- Client retention: +10% (early intervention on at-risk clients)
- Revenue impact: +15% (more time for billable work)

---

*Data is the foundation. Good data = good AI. Start small, improve continuously.*
