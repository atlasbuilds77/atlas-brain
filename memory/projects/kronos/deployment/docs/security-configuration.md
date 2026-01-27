# =====================================================
# KRONOS SECURITY CONFIGURATION
# =====================================================
# Security controls and compliance documentation
# =====================================================

## Security Overview

Kronos implements defense-in-depth security aligned with:
- **WISP** (Written Information Security Program) requirements
- **IRS Publication 4557** for tax preparers
- **NIST Cybersecurity Framework**

---

## 1. Network Security

### VPC Configuration
```hcl
# Private subnets for application/database
# Public subnets only for load balancer
# NAT Gateway for outbound from private subnets
```

### Security Groups

**Load Balancer (Public)**
- Inbound: 80/443 from 0.0.0.0/0
- Outbound: All to VPC

**Application (Private)**
- Inbound: 8000/3000 from ALB security group only
- Outbound: All (for external APIs)

**Database (Private)**
- Inbound: 5432 from Application security group only
- Outbound: None

**Redis (Private)**
- Inbound: 6379 from Application security group only
- Outbound: None

### WAF Rules (AWS WAF)
```yaml
Rules:
  - AWSManagedRulesCommonRuleSet
  - AWSManagedRulesKnownBadInputsRuleSet
  - AWSManagedRulesSQLiRuleSet
  - Rate limiting: 2000 requests/5 minutes per IP
```

---

## 2. Authentication & Authorization

### User Authentication
- **Method**: JWT tokens (short-lived access + refresh tokens)
- **Password Requirements**:
  - Minimum 12 characters
  - Must include: uppercase, lowercase, number, special character
  - No common passwords (checked against breach database)
- **MFA**: Required for admin accounts (TOTP)
- **Session Management**:
  - Access token: 30 minutes
  - Refresh token: 7 days
  - Absolute timeout: 24 hours
  - Concurrent session limit: 5

### Role-Based Access Control (RBAC)
```python
ROLES = {
    "super_admin": ["*"],  # Platform admin
    "client_admin": [      # Laura (business owner)
        "leads:*",
        "clients:*",
        "messages:*",
        "files:*",
        "reports:read",
        "settings:write"
    ],
    "client_staff": [      # Future: staff members
        "leads:read",
        "clients:read",
        "messages:read",
        "files:read"
    ],
    "client_user": [       # End clients (taxpayers)
        "own:*",
        "files:upload"
    ]
}
```

---

## 3. Data Encryption

### Encryption at Rest
| Data | Method | Key Management |
|------|--------|----------------|
| Database | RDS encryption (AES-256) | AWS KMS |
| File Storage | S3 SSE-S3 (AES-256) | AWS managed |
| Sensitive Fields | Application-level AES-256-GCM | Secrets Manager |
| Backups | Same as source | Same as source |

### Encryption in Transit
- All external traffic: TLS 1.3 (TLS 1.2 minimum)
- Internal service communication: TLS 1.2+
- Database connections: SSL required
- Redis connections: TLS enabled

### Sensitive Data Fields
The following fields receive additional application-level encryption:
- SSN (Social Security Number)
- EIN (Employer Identification Number)
- Bank account numbers
- Tax return data
- Personal identification documents

```python
# Example: Encrypting SSN
from app.security import encrypt_field, decrypt_field

encrypted_ssn = encrypt_field(ssn, key=ENCRYPTION_KEY)
# Stored as: {"cipher": "AES-256-GCM", "data": "base64...", "iv": "..."}
```

---

## 4. Audit Logging

### What We Log
| Event Type | Details Captured |
|------------|-----------------|
| Authentication | Login, logout, failed attempts, MFA events |
| Authorization | Access denied, privilege escalation attempts |
| Data Access | Read/write to sensitive data (PII, financial) |
| Admin Actions | User management, configuration changes |
| System Events | Deployments, errors, security alerts |

### Log Format
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "event_type": "data.access",
  "action": "read",
  "resource": "client",
  "resource_id": "client_123",
  "actor": {
    "user_id": "user_456",
    "ip": "192.168.1.1",
    "user_agent": "Mozilla/5.0..."
  },
  "result": "success",
  "metadata": {
    "fields_accessed": ["name", "email", "ssn"]
  }
}
```

### Log Retention
- Application logs: 90 days (CloudWatch)
- Audit logs: 3 years (S3 Glacier) - WISP compliance
- Security events: 1 year (SIEM)

---

## 5. Data Retention & Disposal

### Retention Schedule (WISP/IRS Compliant)
| Data Type | Retention Period | Disposal Method |
|-----------|------------------|-----------------|
| Tax returns | 7 years | Secure delete |
| Client records | 7 years after last service | Secure delete |
| Lead data | 2 years if not converted | Soft delete |
| Audit logs | 3 years | Archive to Glacier |
| Session data | 30 days | Auto-expire (Redis) |
| Temporary files | 24 hours | Auto-delete |

### Secure Disposal
```bash
# S3 objects: Delete with MFA required
aws s3api delete-object --bucket kronos-files --key path/to/file \
  --mfa "arn:aws:iam::ACCOUNT:mfa/admin 123456"

# Database: Soft delete first, hard delete after retention
UPDATE clients SET deleted_at = NOW() WHERE id = ?;
-- After retention period:
DELETE FROM clients WHERE deleted_at < NOW() - INTERVAL '7 years';
```

---

## 6. Secrets Management

### Secrets Stored in AWS Secrets Manager
- Database credentials
- API keys (SendGrid, Twilio, OpenAI)
- Encryption keys
- OAuth client secrets
- JWT signing keys

### Secret Rotation
| Secret Type | Rotation Frequency |
|-------------|-------------------|
| Database password | 90 days |
| API keys | 180 days |
| JWT signing key | 30 days |
| Encryption keys | Annually |

### Accessing Secrets in Application
```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
secrets = get_secret('kronos/production/app-secrets')
db_password = secrets['DB_PASSWORD']
```

---

## 7. Rate Limiting & DDoS Protection

### Application Rate Limits
```python
RATE_LIMITS = {
    "login": "5/minute",           # Prevent brute force
    "password_reset": "3/hour",    # Prevent enumeration
    "api_general": "100/minute",   # General API calls
    "file_upload": "10/minute",    # Prevent abuse
    "lead_form": "20/hour",        # Public form
}
```

### Infrastructure Protection
- **CloudFlare**: DDoS protection, bot management
- **AWS Shield Standard**: Network layer protection
- **WAF**: Application layer filtering

---

## 8. Vulnerability Management

### Automated Scanning
- **Trivy**: Container image scanning (CI/CD)
- **Snyk**: Dependency vulnerability scanning
- **CodeQL**: Static analysis (GitHub)

### Patch Management
| Component | Update Frequency | Method |
|-----------|-----------------|--------|
| OS packages | Weekly | Container rebuild |
| Dependencies | Weekly | Dependabot PRs |
| Runtime (Python/Node) | Monthly | Container rebuild |
| Database | Quarterly | RDS maintenance |

### Penetration Testing
- **Frequency**: Annually (or after major changes)
- **Scope**: External + internal
- **Provider**: TBD

---

## 9. Incident Response

### Security Incident Classification
| Severity | Examples | Response Time |
|----------|----------|---------------|
| Critical | Data breach, ransomware | Immediate |
| High | Auth bypass, injection attack | 1 hour |
| Medium | Unusual access patterns | 4 hours |
| Low | Failed login attempts | Next business day |

### Response Contacts
| Role | Contact |
|------|---------|
| Security Lead | TBD |
| Legal/Compliance | TBD |
| AWS Support | AWS Console |

---

## 10. Compliance Checklist (WISP)

### IRS Publication 4557 Requirements
- [x] Written security plan (this document)
- [x] Employee training program
- [x] Data encryption at rest and in transit
- [x] Access controls (RBAC)
- [x] Audit logging
- [x] Incident response plan
- [x] Data retention policy
- [x] Secure disposal procedures
- [x] Regular security assessments
- [x] Backup and recovery procedures

### Annual Review Schedule
- **January**: Security policy review
- **April**: Post-tax-season review
- **July**: Penetration test
- **October**: DR test and policy update

---

*Document Version: 1.0*
*Last Updated: 2024-01-26*
*Next Review: 2024-04-01*
