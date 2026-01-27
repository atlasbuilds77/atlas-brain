# =====================================================
# KRONOS MONITORING & ALERTING
# =====================================================
# Sentry, CloudWatch, and alerting configuration
# =====================================================

## Monitoring Stack

| Component | Purpose | Dashboard |
|-----------|---------|-----------|
| **Sentry** | Error tracking, performance | sentry.io/kronos |
| **CloudWatch** | Infrastructure metrics, logs | AWS Console |
| **CloudWatch Alarms** | Automated alerting | PagerDuty/Slack |
| **LogRocket** | Frontend session replay | logrocket.com |

---

## 1. Sentry Configuration

### Backend (Python/FastAPI)
```python
# app/config.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    environment=settings.ENVIRONMENT,
    release=settings.VERSION,
    traces_sample_rate=0.1,  # 10% of transactions for performance
    profiles_sample_rate=0.1,  # 10% for profiling
    integrations=[
        FastApiIntegration(transaction_style="endpoint"),
        SqlalchemyIntegration(),
        CeleryIntegration(),
        RedisIntegration(),
    ],
    # Don't send PII
    send_default_pii=False,
    # Custom before_send to scrub sensitive data
    before_send=scrub_sensitive_data,
)

def scrub_sensitive_data(event, hint):
    """Remove sensitive data before sending to Sentry"""
    if 'request' in event:
        request = event['request']
        # Scrub headers
        if 'headers' in request:
            request['headers'] = {
                k: '[REDACTED]' if k.lower() in ['authorization', 'cookie'] else v
                for k, v in request['headers'].items()
            }
        # Scrub body fields
        if 'data' in request and isinstance(request['data'], dict):
            sensitive_fields = ['password', 'ssn', 'tax_id', 'bank_account']
            for field in sensitive_fields:
                if field in request['data']:
                    request['data'][field] = '[REDACTED]'
    return event
```

### Frontend (Next.js)
```javascript
// sentry.client.config.js
import * as Sentry from "@sentry/nextjs";

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT,
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
  integrations: [
    new Sentry.Replay({
      maskAllText: true,
      blockAllMedia: true,
    }),
  ],
});
```

### Sentry Alert Rules
| Alert | Condition | Action |
|-------|-----------|--------|
| New Issue | First occurrence | Slack notification |
| Issue Spike | 10x normal rate | PagerDuty (P2) |
| Critical Error | 500 errors > 5/min | PagerDuty (P1) |
| Performance | p95 > 2s | Slack notification |

---

## 2. CloudWatch Metrics

### Custom Application Metrics
```python
# app/metrics.py
import boto3
from functools import wraps
import time

cloudwatch = boto3.client('cloudwatch')

def publish_metric(name, value, unit='Count', dimensions=None):
    """Publish custom metric to CloudWatch"""
    cloudwatch.put_metric_data(
        Namespace='Kronos/Application',
        MetricData=[{
            'MetricName': name,
            'Value': value,
            'Unit': unit,
            'Dimensions': dimensions or []
        }]
    )

# Business metrics to track
def track_lead_created():
    publish_metric('LeadsCreated', 1)

def track_email_categorized(category):
    publish_metric('EmailsCategorized', 1, dimensions=[
        {'Name': 'Category', 'Value': category}
    ])

def track_digest_sent():
    publish_metric('DigestsSent', 1)

def track_organizer_sent():
    publish_metric('OrganizersSent', 1)
```

### Key Metrics Dashboard
```yaml
# CloudWatch Dashboard Definition
Widgets:
  - Type: metric
    Title: "API Health"
    Metrics:
      - ALB/TargetResponseTime (p50, p95, p99)
      - ALB/RequestCount
      - ALB/HTTPCode_Target_5XX_Count
      
  - Type: metric
    Title: "ECS Services"
    Metrics:
      - ECS/CPUUtilization (backend, frontend, worker)
      - ECS/MemoryUtilization
      - ECS/RunningTaskCount
      
  - Type: metric
    Title: "Database"
    Metrics:
      - RDS/CPUUtilization
      - RDS/DatabaseConnections
      - RDS/FreeStorageSpace
      - RDS/ReadLatency
      - RDS/WriteLatency
      
  - Type: metric
    Title: "Redis"
    Metrics:
      - ElastiCache/CPUUtilization
      - ElastiCache/CurrConnections
      - ElastiCache/CacheHits
      - ElastiCache/CacheMisses
      
  - Type: metric
    Title: "Business Metrics"
    Metrics:
      - Kronos/Application/LeadsCreated
      - Kronos/Application/EmailsCategorized
      - Kronos/Application/DigestsSent
```

---

## 3. CloudWatch Alarms

### Infrastructure Alarms
```hcl
# terraform/alarms.tf

# Backend High CPU
resource "aws_cloudwatch_metric_alarm" "backend_cpu_high" {
  alarm_name          = "kronos-backend-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/ECS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Backend CPU > 80%"
  
  dimensions = {
    ClusterName = "kronos-production"
    ServiceName = "kronos-backend"
  }
  
  alarm_actions = [aws_sns_topic.alerts.arn]
  ok_actions    = [aws_sns_topic.alerts.arn]
}

# Database Connection Limit
resource "aws_cloudwatch_metric_alarm" "db_connections_high" {
  alarm_name          = "kronos-db-connections-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80  # Assuming 100 max connections
  alarm_description   = "Database connections > 80%"
  
  dimensions = {
    DBInstanceIdentifier = "kronos-production"
  }
  
  alarm_actions = [aws_sns_topic.alerts.arn]
}

# Error Rate
resource "aws_cloudwatch_metric_alarm" "error_rate_high" {
  alarm_name          = "kronos-error-rate-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "HTTPCode_Target_5XX_Count"
  namespace           = "AWS/ApplicationELB"
  period              = 300
  statistic           = "Sum"
  threshold           = 10
  alarm_description   = "5XX errors > 10 in 5 minutes"
  
  dimensions = {
    LoadBalancer = aws_lb.main.arn_suffix
  }
  
  alarm_actions = [aws_sns_topic.alerts_critical.arn]
}
```

### Application Alarms
```hcl
# Daily digest not sent (critical for Laura)
resource "aws_cloudwatch_metric_alarm" "digest_missing" {
  alarm_name          = "kronos-digest-missing"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "DigestsSent"
  namespace           = "Kronos/Application"
  period              = 86400  # 24 hours
  statistic           = "Sum"
  threshold           = 1
  alarm_description   = "No daily digest sent in 24 hours"
  treat_missing_data  = "breaching"
  
  alarm_actions = [aws_sns_topic.alerts.arn]
}
```

---

## 4. Log Aggregation

### Structured Logging
```python
# app/logging.py
import json
import logging
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'duration_ms'):
            log_data['duration_ms'] = record.duration_ms
            
        # Add exception info
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

# Configure logging
def setup_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    logging.root.handlers = [handler]
    logging.root.setLevel(logging.INFO)
```

### CloudWatch Logs Insights Queries

**Error Analysis**
```
fields @timestamp, @message
| filter level = "ERROR"
| stats count() by module
| sort count desc
| limit 20
```

**Slow API Requests**
```
fields @timestamp, message, duration_ms, function
| filter duration_ms > 1000
| sort duration_ms desc
| limit 50
```

**User Activity**
```
fields @timestamp, user_id, message
| filter user_id = "user_123"
| sort @timestamp desc
| limit 100
```

**Daily Digest Status**
```
fields @timestamp, @message
| filter @message like /daily_digest/
| sort @timestamp desc
| limit 20
```

---

## 5. Alert Routing

### SNS Topics
```hcl
resource "aws_sns_topic" "alerts" {
  name = "kronos-alerts"
}

resource "aws_sns_topic" "alerts_critical" {
  name = "kronos-alerts-critical"
}

# Slack integration
resource "aws_sns_topic_subscription" "slack" {
  topic_arn = aws_sns_topic.alerts.arn
  protocol  = "https"
  endpoint  = var.slack_webhook_url
}

# PagerDuty for critical
resource "aws_sns_topic_subscription" "pagerduty" {
  topic_arn = aws_sns_topic.alerts_critical.arn
  protocol  = "https"
  endpoint  = var.pagerduty_endpoint
}
```

### Alert Escalation Matrix
| Severity | Initial | 15 min | 30 min | 1 hour |
|----------|---------|--------|--------|--------|
| P1 (Critical) | PagerDuty + Slack | Call on-call | Escalate to lead | All-hands |
| P2 (High) | Slack + Email | PagerDuty | Escalate to lead | - |
| P3 (Medium) | Slack | Email reminder | - | - |
| P4 (Low) | Email | - | - | - |

---

## 6. Dashboard URLs

| Dashboard | URL | Purpose |
|-----------|-----|---------|
| Sentry | https://sentry.io/kronos | Error tracking |
| CloudWatch | AWS Console | Infrastructure |
| Grafana (optional) | TBD | Custom dashboards |
| Status Page | https://status.kronos.app | Public status |

---

*Last Updated: 2024-01-26*
