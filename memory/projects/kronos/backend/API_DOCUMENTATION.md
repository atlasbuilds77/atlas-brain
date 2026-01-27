# Kronos Core Engine - API Documentation

## Table of Contents

1. [Authentication](#authentication)
2. [Leads API](#leads-api)
3. [Clients API](#clients-api)
4. [Messages API](#messages-api)
5. [Files API](#files-api)
6. [Analytics API](#analytics-api)
7. [Error Handling](#error-handling)
8. [Rate Limiting](#rate-limiting)

---

## Authentication

All API endpoints (except `/auth/register` and `/auth/login`) require authentication via JWT token.

### Register New User

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepass123",
  "role": "client"
}
```

**Response:** `201 Created`
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "client",
  "created_at": "2024-01-26T12:00:00Z",
  "last_active": null
}
```

### Login

**Endpoint:** `POST /api/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepass123"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

### Refresh Token

**Endpoint:** `POST /api/auth/refresh`

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response:** `200 OK` (same as login response)

### Get Current User

**Endpoint:** `GET /api/auth/me`

**Headers:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

**Response:** `200 OK`
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "role": "client",
  "created_at": "2024-01-26T12:00:00Z",
  "last_active": "2024-01-26T14:30:00Z"
}
```

---

## Leads API

### List Leads

**Endpoint:** `GET /api/leads`

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `page_size` (int): Results per page (default: 50, max: 100)
- `status` (string): Filter by status (new, contacted, qualified, converted, dead)
- `search` (string): Search by name/email/phone

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "user_id": null,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "phone": "+1234567890",
      "company": "Smith Corp",
      "status": "new",
      "source": "website",
      "lead_score": 75.5,
      "assigned_to": null,
      "notes": "Interested in tax services",
      "tags": ["tax", "small-business"],
      "custom_fields": {},
      "created_at": "2024-01-26T10:00:00Z",
      "contacted_at": null,
      "converted_at": null,
      "updated_at": null
    }
  ],
  "total": 245,
  "page": 1,
  "page_size": 50,
  "pages": 5
}
```

### Create Lead

**Endpoint:** `POST /api/leads`

**Request Body:**
```json
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+1234567890",
  "company": "Smith Corp",
  "source": "website",
  "notes": "Interested in tax services",
  "tags": ["tax", "small-business"],
  "custom_fields": {
    "business_type": "llc",
    "annual_revenue": "500k"
  }
}
```

**Response:** `201 Created` (same structure as list items)

### Get Lead

**Endpoint:** `GET /api/leads/{id}`

**Response:** `200 OK` (same structure as list items)

### Update Lead

**Endpoint:** `PUT /api/leads/{id}`

**Request Body:** (all fields optional)
```json
{
  "status": "contacted",
  "notes": "Called and left voicemail",
  "assigned_to": 2
}
```

**Response:** `200 OK` (updated lead)

### Delete Lead

**Endpoint:** `DELETE /api/leads/{id}`

**Response:** `204 No Content`

### Score Lead

**Endpoint:** `POST /api/leads/{id}/score`

**Response:** `200 OK`
```json
{
  "lead_id": 1,
  "score": 85.5,
  "factors": {
    "has_email": 20,
    "has_phone": 20,
    "has_company": 10,
    "source_quality": 30,
    "has_notes": 10
  },
  "recommendation": "High priority - contact immediately"
}
```

---

## Clients API

### List Clients

**Endpoint:** `GET /api/clients`

**Query Parameters:**
- `page`, `page_size`, `status`, `search` (same as leads)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "user_id": 123,
      "lead_id": 45,
      "status": "active",
      "lifetime_value": 5000.00,
      "retention_risk_score": 0.15,
      "last_interaction": "2024-01-25T14:00:00Z",
      "next_followup": "2024-02-01T10:00:00Z",
      "preferred_contact_method": "email",
      "custom_fields": {},
      "tags": ["tax", "priority"],
      "client_since": "2023-01-15T12:00:00Z",
      "updated_at": "2024-01-26T10:00:00Z"
    }
  ],
  "total": 156,
  "page": 1,
  "page_size": 50,
  "pages": 4
}
```

### Create Client

**Endpoint:** `POST /api/clients`

**Request Body:**
```json
{
  "user_id": 123,
  "lead_id": 45,
  "status": "active",
  "preferred_contact_method": "email",
  "custom_fields": {},
  "tags": ["tax"]
}
```

**Response:** `201 Created`

### Get Client

**Endpoint:** `GET /api/clients/{id}`

**Response:** `200 OK`

### Update Client

**Endpoint:** `PUT /api/clients/{id}`

**Request Body:**
```json
{
  "status": "active",
  "lifetime_value": 5500.00,
  "next_followup": "2024-02-15T10:00:00Z"
}
```

**Response:** `200 OK`

### Delete Client

**Endpoint:** `DELETE /api/clients/{id}`

**Response:** `204 No Content`

### Assess Client Risk

**Endpoint:** `POST /api/clients/{id}/risk`

**Response:** `200 OK`
```json
{
  "client_id": 1,
  "risk_score": 0.35,
  "risk_level": "low",
  "factors": {
    "inactive_days": 32,
    "low_ltv": 1200.00
  },
  "recommendations": [
    "Continue normal cadence"
  ]
}
```

---

## Messages API

### List Messages

**Endpoint:** `GET /api/messages`

**Query Parameters:**
- `page`, `page_size` (same as above)
- `status`: Filter by status (unread, read, archived, deleted)
- `category`: Filter by category (prospective, client, office, spam, other)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "from_address": "client@example.com",
      "to_address": "support@mycompany.com",
      "channel": "email",
      "subject": "Question about tax filing",
      "body": "I have a question...",
      "html_body": null,
      "thread_id": "thread-123",
      "in_reply_to": null,
      "status": "unread",
      "category": "client",
      "sentiment_score": 0,
      "priority_score": 4,
      "ai_summary": "Client asking about tax filing deadline",
      "user_id": 123,
      "client_id": 45,
      "lead_id": null,
      "has_attachments": false,
      "attachment_ids": [],
      "metadata": {},
      "sent_at": "2024-01-26T10:30:00Z",
      "received_at": "2024-01-26T10:30:05Z",
      "read_at": null
    }
  ],
  "total": 342,
  "page": 1,
  "page_size": 50,
  "pages": 7
}
```

### Create Message

**Endpoint:** `POST /api/messages`

**Request Body:**
```json
{
  "from_address": "support@mycompany.com",
  "to_address": "client@example.com",
  "channel": "email",
  "subject": "Re: Question about tax filing",
  "body": "Thanks for reaching out...",
  "client_id": 45,
  "sent_at": "2024-01-26T11:00:00Z"
}
```

**Response:** `201 Created`

### Get Message

**Endpoint:** `GET /api/messages/{id}`

**Response:** `200 OK` (marks message as read)

### Update Message

**Endpoint:** `PUT /api/messages/{id}`

**Request Body:**
```json
{
  "status": "archived",
  "category": "client"
}
```

**Response:** `200 OK`

### Delete Message

**Endpoint:** `DELETE /api/messages/{id}`

**Response:** `204 No Content`

### Categorize Message

**Endpoint:** `POST /api/messages/categorize?message_id={id}`

**Response:** `200 OK`
```json
{
  "message_id": 1,
  "category": "client",
  "confidence": 0.85,
  "sentiment_score": 0,
  "priority_score": 4,
  "summary": "Client asking about tax filing deadline"
}
```

---

## Files API

### List Files

**Endpoint:** `GET /api/files`

**Query Parameters:**
- `page`, `page_size`
- `client_id`: Filter by client
- `category`: Filter by category
- `year`: Filter by year

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 1,
      "filename": "2024_tax_return.pdf",
      "original_filename": "2024_tax_return.pdf",
      "content_type": "application/pdf",
      "size_bytes": 524288,
      "storage_path": "20240126/abc123_2024_tax_return.pdf",
      "storage_bucket": "kronos-files",
      "client_id": 45,
      "user_id": 123,
      "message_id": null,
      "category": "tax_return",
      "year": 2024,
      "tags": ["tax", "2024"],
      "encrypted": true,
      "encryption_key_id": "default-key",
      "retention_until": "2031-01-26T12:00:00Z",
      "is_sensitive": true,
      "download_count": 3,
      "last_downloaded_at": "2024-01-26T09:00:00Z",
      "metadata": {},
      "uploaded_at": "2024-01-26T08:00:00Z",
      "updated_at": null
    }
  ],
  "total": 89,
  "page": 1,
  "page_size": 50,
  "pages": 2
}
```

### Upload File

**Endpoint:** `POST /api/files/upload`

**Request:** `multipart/form-data`
```
file: [binary file data]
client_id: 45
category: tax_return
year: 2024
is_sensitive: true
retention_years: 7
```

**Response:** `201 Created` (same structure as list items)

### Get File Metadata

**Endpoint:** `GET /api/files/{id}`

**Response:** `200 OK`

### Get Download URL

**Endpoint:** `GET /api/files/{id}/download`

**Response:** `200 OK`
```json
{
  "file_id": 1,
  "filename": "2024_tax_return.pdf",
  "download_url": "https://s3.amazonaws.com/kronos-files/...",
  "expires_in": 3600
}
```

### Update File

**Endpoint:** `PUT /api/files/{id}`

**Request Body:**
```json
{
  "filename": "2024_tax_return_final.pdf",
  "category": "tax_return",
  "tags": ["tax", "2024", "final"]
}
```

**Response:** `200 OK`

### Delete File

**Endpoint:** `DELETE /api/files/{id}`

**Response:** `204 No Content`

---

## Analytics API

### Get Dashboard Metrics

**Endpoint:** `GET /api/analytics/dashboard`

**Response:** `200 OK`
```json
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

---

## Error Handling

All errors follow this format:

```json
{
  "detail": "Error message here"
}
```

### HTTP Status Codes

- `200 OK`: Success
- `201 Created`: Resource created
- `204 No Content`: Success with no response body
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid token
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Validation Errors

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ],
  "message": "Validation error in request data"
}
```

---

## Rate Limiting

Default rate limit: **60 requests per minute** per IP address.

When rate limit is exceeded, you'll receive:

**Status:** `429 Too Many Requests`

**Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1706274000
Retry-After: 60
```

---

## Pagination

All list endpoints support pagination:

**Request:**
```
GET /api/leads?page=2&page_size=25
```

**Response:**
```json
{
  "items": [...],
  "total": 245,
  "page": 2,
  "page_size": 25,
  "pages": 10
}
```

---

## OpenAPI Specification

Full OpenAPI 3.0 specification available at:
- JSON: `GET /api/openapi.json`
- Swagger UI: `GET /docs`
- ReDoc: `GET /redoc`

---

**For more information, see the main README.md**
