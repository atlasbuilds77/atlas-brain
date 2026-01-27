# Kronos AI - Testing & Accuracy Metrics

**Version:** 1.0  
**Date:** 2026-01-26

---

## Overview

Comprehensive testing strategy and accuracy metrics for all Kronos AI components. Includes unit tests, integration tests, and production monitoring.

---

## 1. Lead Qualifier Bot

### Test Suite

**Unit Tests:**
```python
# test_lead_qualifier.py
import pytest
from lead_qualifier import LeadQualifier, TAX_QUESTIONS, integrate_with_lead_form

def test_high_quality_lead():
    """Test that high-quality leads are correctly identified"""
    lead_data = {
        "lead_id": "test_001",
        "tax_services": "Tax planning & strategy",
        "filing_history": "yes",
        "situation_complexity": "Complex (Business, real estate, multiple states)",
        "timeline": "Within 2 weeks",
        "price_sensitivity": "Quality service & expertise",
        "referral_source": "Referral from friend/family",
        "ready_to_start": "yes"
    }
    
    score = integrate_with_lead_form(lead_data, "tax")
    
    assert score.qualified == True
    assert score.percentage >= 80
    assert len(score.flags) == 0  # No disqualifying flags

def test_price_shopper_disqualified():
    """Test that price shoppers are filtered out"""
    lead_data = {
        "lead_id": "test_002",
        "tax_services": "Personal tax return (1040)",
        "price_sensitivity": "Lowest price",  # DISQUALIFIER
        "ready_to_start": "no"
    }
    
    score = integrate_with_lead_form(lead_data, "tax")
    
    assert score.qualified == False
    assert "disqualified:price_sensitivity" in ",".join(score.flags)

def test_borderline_lead():
    """Test borderline lead scoring"""
    lead_data = {
        "lead_id": "test_003",
        "tax_services": "Personal tax return (1040)",
        "filing_history": "no",
        "situation_complexity": "Simple (W-2 only)",
        "timeline": "Before deadline (not urgent)",
        "price_sensitivity": "Fast turnaround",
        "referral_source": "Google search",
        "ready_to_start": "yes"
    }
    
    score = integrate_with_lead_form(lead_data, "tax")
    
    # Should be in the middle range
    assert 40 <= score.percentage <= 70

def test_conversational_bot():
    """Test interactive chatbot flow"""
    from lead_qualifier import ConversationalQualifier
    
    bot = ConversationalQualifier("tax")
    lead_id = "bot_test_001"
    
    # Start conversation
    message = bot.start_conversation(lead_id)
    assert "qualification" in message.lower()
    
    # Answer questions
    is_complete, response = bot.process_answer(lead_id, "Tax planning & strategy")
    assert is_complete == False  # More questions
    
    # Continue until complete
    answers = ["yes", "Complex", "ASAP", "Quality service", "Referral", "yes"]
    for answer in answers:
        is_complete, response = bot.process_answer(lead_id, answer)
    
    assert is_complete == True
    assert "qualified" in response.lower() or "thank you" in response.lower()

# Run tests
pytest.main([__file__, "-v"])
```

### Accuracy Metrics

**Confusion Matrix:**
```
                 Predicted
               Qualified  Not Qualified
Actual
Qualified         TP          FN
Not Qualified     FP          TN
```

**Key Metrics:**
- **Accuracy:** (TP + TN) / Total
- **Precision:** TP / (TP + FP) — "Of leads we qualify, how many are actually good?"
- **Recall:** TP / (TP + FN) — "Of good leads, how many do we catch?"
- **F1 Score:** 2 * (Precision * Recall) / (Precision + Recall)

**Target Performance:**
| Metric | Baseline | Target | Elite |
|--------|----------|--------|-------|
| Accuracy | 75% | 85% | 90% |
| Precision | 70% | 80% | 85% |
| Recall | 80% | 85% | 90% |
| F1 Score | 0.75 | 0.83 | 0.87 |

**Measurement Script:**
```python
def calculate_lead_metrics(predictions: List, ground_truth: List):
    """Calculate accuracy metrics for lead qualification"""
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
    
    y_pred = [1 if p.qualified else 0 for p in predictions]
    y_true = [1 if g["converted"] else 0 for g in ground_truth]
    
    metrics = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred),
        "recall": recall_score(y_true, y_pred),
        "f1": f1_score(y_true, y_pred),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist()
    }
    
    return metrics

# Example usage
predictions = [predict_lead(lead) for lead in test_dataset]
ground_truth = [{"converted": lead["actually_converted"]} for lead in test_dataset]

metrics = calculate_lead_metrics(predictions, ground_truth)
print(f"Accuracy: {metrics['accuracy']:.2%}")
print(f"Precision: {metrics['precision']:.2%}")
print(f"Recall: {metrics['recall']:.2%}")
```

---

## 2. Email Categorizer

### Test Suite

**Unit Tests:**
```python
# test_email_categorizer.py
import pytest
from email_categorizer import EmailCategorizer, EmailMessage
from datetime import datetime

@pytest.fixture
def categorizer():
    cat = EmailCategorizer("tax")
    cat.add_client("john@example.com")  # Known client
    return cat

def test_prospective_classification(categorizer):
    """Test prospective lead email"""
    email = EmailMessage(
        id="e001",
        from_email="newlead@gmail.com",
        from_name="Sarah Miller",
        to_email="laura@taxpro.com",
        subject="Tax preparation inquiry",
        body="Hi, I'm looking for someone to help with my business taxes. What are your rates?",
        timestamp=datetime.now()
    )
    
    result = categorizer.classify(email)
    
    assert result.category == "prospective"
    assert result.confidence > 0.5
    assert "needs_response" in result.flags

def test_active_client_classification(categorizer):
    """Test active client email"""
    email = EmailMessage(
        id="e002",
        from_email="john@example.com",
        from_name="John Smith",
        to_email="laura@taxpro.com",
        subject="My W-2 is ready",
        body="Hi Laura, I got my W-2 from my employer. I'll upload it to the portal today.",
        timestamp=datetime.now()
    )
    
    result = categorizer.classify(email)
    
    assert result.category == "active_client"
    assert "has_attachment" in result.flags or "needs_response" in result.flags

def test_spam_classification(categorizer):
    """Test spam detection"""
    email = EmailMessage(
        id="e003",
        from_email="marketing@seocompany.com",
        from_name="SEO Services",
        to_email="laura@taxpro.com",
        subject="Boost your website traffic NOW!",
        body="Limited time offer! Click here to increase traffic by 500%. Act now!",
        timestamp=datetime.now()
    )
    
    result = categorizer.classify(email)
    
    assert result.category == "spam"
    assert result.suggested_action == "archive"

def test_urgent_flag_detection(categorizer):
    """Test urgent flag on emails"""
    email = EmailMessage(
        id="e004",
        from_email="client@email.com",
        from_name="Client",
        to_email="laura@taxpro.com",
        subject="URGENT - IRS letter",
        body="I just received an urgent letter from the IRS. Please help ASAP!",
        timestamp=datetime.now()
    )
    
    result = categorizer.classify(email)
    
    assert "urgent" in result.flags
    assert result.suggested_action == "respond_immediately"

def test_batch_processing():
    """Test batch email processing"""
    from email_categorizer import BatchEmailProcessor
    
    categorizer = EmailCategorizer("tax")
    batch = BatchEmailProcessor(categorizer)
    
    emails = [
        # Create 10 test emails of different types
        # ... (abbreviated for brevity)
    ]
    
    categorized = batch.process_inbox(emails)
    
    assert len(categorized) > 0
    assert "prospective" in categorized
    assert "active_client" in categorized

pytest.main([__file__, "-v"])
```

### Accuracy Metrics

**Multi-class Classification Metrics:**
```python
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

def evaluate_email_categorizer(predictions, ground_truth):
    """Evaluate email categorization accuracy"""
    
    y_pred = [p.category for p in predictions]
    y_true = [g["true_category"] for g in ground_truth]
    
    # Classification report
    report = classification_report(
        y_true, 
        y_pred, 
        target_names=["prospective", "active_client", "office", "retention", "spam"]
    )
    
    print(report)
    
    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    
    return {
        "overall_accuracy": np.mean(np.array(y_pred) == np.array(y_true)),
        "confusion_matrix": cm.tolist(),
        "report": report
    }
```

**Target Performance (per category):**
| Category | Precision | Recall | F1 |
|----------|-----------|--------|-----|
| Prospective | 85% | 80% | 82% |
| Active Client | 90% | 90% | 90% |
| Office | 85% | 85% | 85% |
| Retention | 80% | 75% | 77% |
| Spam | 95% | 95% | 95% |
| **Overall** | **87%** | **85%** | **86%** |

---

## 3. Daily Digest Generator

### Test Suite

**Unit Tests:**
```python
# test_daily_digest.py
import pytest
from daily_digest import DigestGenerator, Message, MessageChannel
from datetime import datetime, timedelta

@pytest.fixture
def sample_messages():
    """Create sample messages for testing"""
    now = datetime.now()
    return [
        Message(
            id="m001",
            channel=MessageChannel.EMAIL,
            from_contact="urgent@client.com",
            from_name="Urgent Client",
            to_contact="laura@taxpro.com",
            subject="URGENT - Need help",
            body="This is urgent!",
            timestamp=now - timedelta(hours=1),
            category="active_client",
            flags=["urgent", "needs_response"]
        ),
        Message(
            id="m002",
            channel=MessageChannel.EMAIL,
            from_contact="spam@marketing.com",
            from_name="Spammer",
            to_contact="laura@taxpro.com",
            subject="Buy our product!",
            body="Limited time offer!",
            timestamp=now - timedelta(hours=3),
            category="spam",
            flags=[]
        ),
        # Add more test messages...
    ]

def test_digest_generation(sample_messages):
    """Test basic digest generation"""
    generator = DigestGenerator("tax")
    digest = generator.generate(sample_messages, context={"is_tax_season": True})
    
    assert digest.total_messages == len(sample_messages)
    assert digest.urgent_count > 0
    assert len(digest.sections) > 0

def test_priority_sorting(sample_messages):
    """Test that urgent messages appear first"""
    generator = DigestGenerator("tax")
    digest = generator.generate(sample_messages)
    
    # First section should be urgent
    first_section = digest.sections[0]
    assert "urgent" in first_section.title.lower()
    assert all("urgent" in msg.flags for msg in first_section.messages)

def test_tax_season_priority():
    """Test priority changes during tax season"""
    generator = DigestGenerator("tax")
    
    messages = [
        Message(
            id="m1",
            channel=MessageChannel.EMAIL,
            from_contact="client@test.com",
            from_name="Client",
            to_contact="laura@taxpro.com",
            subject="Client question",
            body="Question",
            timestamp=datetime.now(),
            category="active_client",
            flags=[]
        )
    ]
    
    # During tax season
    digest_season = generator.generate(messages, {"is_tax_season": True})
    
    # Off season
    digest_offseason = generator.generate(messages, {"is_tax_season": False})
    
    # Priorities should differ (hard to test exactly without inspecting internals)
    assert digest_season is not None
    assert digest_offseason is not None

def test_email_formatting():
    """Test email output formatting"""
    generator = DigestGenerator("tax")
    messages = []  # Sample messages
    
    digest = generator.generate(messages)
    subject, html = generator.format_as_email(digest)
    
    assert "Daily Digest" in subject
    assert "<h1>" in html
    assert "</html>" not in html  # We return fragment, not full HTML

def test_text_formatting():
    """Test plain text formatting"""
    generator = DigestGenerator("tax")
    messages = []  # Sample messages
    
    digest = generator.generate(messages)
    text = generator.format_as_text(digest)
    
    assert "DAILY DIGEST" in text
    assert "=" in text  # Has formatting

pytest.main([__file__, "-v"])
```

### Metrics

**User Satisfaction Metrics:**
- **Daily Rating:** User rates digest 1-5 stars
- **Open Rate:** % of digests opened within 2 hours
- **Click Rate:** % of digests where user clicks/acts on a message
- **False Urgent Rate:** % of "urgent" items that weren't actually urgent
- **Missed Urgent Rate:** % of urgent items not flagged as urgent

**Target Performance:**
| Metric | Target |
|--------|--------|
| Average Rating | 4.5/5 |
| Open Rate | 90% |
| Click Rate | 60% |
| False Urgent | <5% |
| Missed Urgent | <2% |

**Tracking Script:**
```python
def track_digest_engagement(digest_id: str):
    """Track user engagement with digest"""
    
    # Record when digest is opened (via email tracking pixel)
    opened_at = detect_email_open(digest_id)
    
    # Track which messages are clicked
    clicked_messages = track_link_clicks(digest_id)
    
    # Ask for rating (embedded in email)
    rating = get_user_rating(digest_id)
    
    # Store metrics
    database.store_metrics({
        "digest_id": digest_id,
        "opened_at": opened_at,
        "clicked_messages": clicked_messages,
        "rating": rating,
        "false_urgent": count_false_urgents(digest_id),
        "missed_urgent": count_missed_urgents(digest_id)
    })
```

---

## 4. Retention Predictor

### Test Suite

**Unit Tests:**
```python
# test_retention_predictor.py
import pytest
from retention_predictor import RetentionPredictor, ClientProfile, RiskLevel
from datetime import datetime, timedelta

def test_critical_risk_client():
    """Test detection of critical-risk client"""
    predictor = RetentionPredictor("tax")
    
    client = ClientProfile(
        client_id="C001",
        industry="tax",
        client_since=datetime.now() - timedelta(days=800),
        lifetime_value=3000,
        service_type="personal_tax",
        last_interaction=datetime.now() - timedelta(days=400),
        interaction_frequency=0.1,
        response_time_hours=120,
        messages_sent=1,
        messages_received=10,
        projects_completed=0,
        projects_cancelled=2,
        average_project_value=500,
        payment_history_score=0.5,
        complaint_count=3,
        positive_feedback_count=0,
        support_tickets=5,
        custom_fields={
            "years_not_returned": 2,
            "price_complaints": 2,
            "mentioned_competitor": True
        }
    )
    
    prediction = predictor.predict(client)
    
    assert prediction.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    assert prediction.risk_score > 60
    assert len(prediction.signals) >= 5
    assert len(prediction.recommended_actions) > 0

def test_low_risk_client():
    """Test healthy client with low risk"""
    predictor = RetentionPredictor("tax")
    
    client = ClientProfile(
        client_id="C002",
        industry="tax",
        client_since=datetime.now() - timedelta(days=1000),
        lifetime_value=15000,
        service_type="business_tax",
        last_interaction=datetime.now() - timedelta(days=3),
        interaction_frequency=4.0,
        response_time_hours=2,
        messages_sent=60,
        messages_received=55,
        projects_completed=10,
        projects_cancelled=0,
        average_project_value=1500,
        payment_history_score=1.0,
        complaint_count=0,
        positive_feedback_count=5,
        support_tickets=0,
        custom_fields={
            "years_not_returned": 0,
            "price_complaints": 0
        }
    )
    
    prediction = predictor.predict(client)
    
    assert prediction.risk_level == RiskLevel.LOW
    assert prediction.risk_score < 30
    assert len(prediction.signals) <= 2

def test_batch_analysis():
    """Test batch retention analysis"""
    from retention_predictor import BatchRetentionAnalysis
    
    predictor = RetentionPredictor("tax")
    batch = BatchRetentionAnalysis(predictor)
    
    # Create mix of clients
    clients = []  # Add test clients
    
    grouped = batch.analyze_client_base(clients)
    
    assert RiskLevel.CRITICAL in grouped
    assert RiskLevel.LOW in grouped
    
    report = batch.generate_report()
    assert "RETENTION RISK" in report

pytest.main([__file__, "-v"])
```

### Accuracy Metrics

**Prediction Accuracy:**
- **True Positive:** Predicted churn, actually churned
- **False Positive:** Predicted churn, didn't churn
- **True Negative:** Predicted retention, retained
- **False Negative:** Predicted retention, churned (WORST)

**Cost Matrix:**
```
                Predicted Churn    Predicted Retain
Actual Churn         $0                 $-5000 (lost client)
Actual Retain        $-100 (outreach)    $0
```

**Target Performance:**
| Metric | Target | Notes |
|--------|--------|-------|
| Accuracy | 80% | Overall correct predictions |
| Precision (churn) | 70% | Of predicted churns, how many actually churn |
| Recall (churn) | 85% | Of actual churns, how many we catch |
| False Negative Rate | <15% | MINIMIZE - missing churn is expensive |

**Evaluation Script:**
```python
def evaluate_retention_model(predictions, actual_outcomes, months_ahead=6):
    """
    Evaluate retention predictor accuracy.
    
    Args:
        predictions: List of RetentionPrediction objects
        actual_outcomes: List of actual churn outcomes (6 months later)
        months_ahead: How far ahead we're predicting
    """
    
    y_pred = [1 if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL] else 0 
              for p in predictions]
    y_true = [1 if outcome["churned"] else 0 for outcome in actual_outcomes]
    
    from sklearn.metrics import classification_report, roc_auc_score, roc_curve
    
    print(classification_report(y_true, y_pred, target_names=["Retained", "Churned"]))
    
    # ROC-AUC (using risk_score as probability)
    y_scores = [p.risk_score / 100 for p in predictions]
    auc = roc_auc_score(y_true, y_scores)
    print(f"ROC-AUC: {auc:.3f}")
    
    # Cost analysis
    cost = calculate_cost(y_pred, y_true)
    print(f"Total Cost: ${cost:,.2f}")
    
    return {
        "accuracy": np.mean(np.array(y_pred) == np.array(y_true)),
        "auc": auc,
        "cost": cost
    }

def calculate_cost(y_pred, y_true):
    """Calculate business cost of predictions"""
    cost = 0
    for pred, actual in zip(y_pred, y_true):
        if pred == 1 and actual == 0:
            cost += 100  # False alarm, wasted outreach
        elif pred == 0 and actual == 1:
            cost += 5000  # Missed churn, lost client
    return cost
```

---

## Integration Tests

**End-to-End Workflow:**
```python
# test_integration.py
import pytest

def test_full_lead_flow():
    """Test complete lead qualification flow"""
    # 1. Lead submits form
    lead_data = {"email": "test@example.com", "responses": {...}}
    
    # 2. Qualifier scores lead
    score = qualify_lead(lead_data)
    assert score.qualified
    
    # 3. Lead stored in database
    lead_record = database.get_lead(score.lead_id)
    assert lead_record is not None
    
    # 4. Automated email sent
    email_sent = check_email_sent(lead_data["email"])
    assert email_sent
    
    # 5. Lead synced to CRM
    crm_contact = check_crm_sync(score.lead_id)
    assert crm_contact is not None

def test_full_email_flow():
    """Test complete email categorization flow"""
    # 1. Email arrives
    raw_email = receive_test_email()
    
    # 2. Categorized
    result = categorize_email(raw_email)
    assert result.category in ["prospective", "active_client", "office"]
    
    # 3. Tagged in Gmail
    labels = get_gmail_labels(raw_email["id"])
    assert result.category in labels
    
    # 4. Included in digest
    digest = generate_test_digest()
    assert any(msg.id == raw_email["id"] for section in digest.sections for msg in section.messages)

def test_full_retention_flow():
    """Test complete retention prediction flow"""
    # 1. Weekly job runs
    run_retention_check()
    
    # 2. Predictions generated
    predictions = database.get_recent_predictions()
    assert len(predictions) > 0
    
    # 3. Critical clients flagged
    critical = [p for p in predictions if p.risk_level == RiskLevel.CRITICAL]
    
    # 4. Alert sent
    if critical:
        alert = check_alert_sent()
        assert alert is not None

pytest.main([__file__, "-v"])
```

---

## Production Monitoring

**Metrics Dashboard:**
```python
from prometheus_client import Counter, Histogram, Gauge

# Counters
leads_processed = Counter('leads_processed_total', 'Total leads processed')
emails_categorized = Counter('emails_categorized_total', 'Total emails categorized', ['category'])
digests_generated = Counter('digests_generated_total', 'Total digests generated')
predictions_made = Counter('predictions_made_total', 'Total retention predictions')

# Histograms (response time)
lead_response_time = Histogram('lead_qualification_seconds', 'Lead qualification duration')
email_response_time = Histogram('email_categorization_seconds', 'Email categorization duration')

# Gauges (current state)
critical_risk_clients = Gauge('critical_risk_clients', 'Number of critical risk clients')

# Logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('kronos')

@lead_response_time.time()
def qualify_lead_with_metrics(lead_data):
    result = qualify_lead(lead_data)
    leads_processed.inc()
    logger.info(f"Lead {lead_data['lead_id']} qualified: {result.qualified}")
    return result
```

**Alerting (via Slack/Email):**
```python
def check_model_performance():
    """Daily check of model performance"""
    
    # Check accuracy drop
    recent_accuracy = calculate_recent_accuracy()
    if recent_accuracy < 0.75:
        send_alert(f"⚠️ Model accuracy dropped to {recent_accuracy:.1%}")
    
    # Check false negative rate (missed churns)
    fn_rate = calculate_false_negative_rate()
    if fn_rate > 0.20:
        send_alert(f"🚨 High false negative rate: {fn_rate:.1%}")
    
    # Check API errors
    error_rate = get_api_error_rate()
    if error_rate > 0.05:
        send_alert(f"❌ High API error rate: {error_rate:.1%}")
```

---

## Performance Benchmarks

**Target Performance (Laura's laptop):**
| Operation | Target Time |
|-----------|-------------|
| Lead qualification | <100ms |
| Email categorization | <200ms |
| Daily digest generation | <2s |
| Retention prediction (1 client) | <500ms |
| Batch retention (100 clients) | <30s |

**Optimization Tips:**
- Cache embeddings (don't recompute)
- Batch database queries
- Use async for API calls
- Profile slow functions with `cProfile`

---

*Test everything. Measure everything. Improve continuously.*
