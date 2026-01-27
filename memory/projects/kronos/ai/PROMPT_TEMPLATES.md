# Kronos AI - LLM Prompt Templates

**Version:** 1.0  
**Date:** 2026-01-26

---

## Overview

Production-ready prompt templates for GPT-4 and Claude integration. Optimized for accuracy, cost-efficiency, and industry context.

---

## General Prompting Guidelines

### Best Practices

1. **Be specific:** Provide clear context and expected output format
2. **Use examples:** Few-shot prompting improves accuracy
3. **Set constraints:** Limit length, format, tone
4. **Industry context:** Always include industry-specific context
5. **Temperature:** Lower (0.0-0.3) for factual tasks, higher (0.7-1.0) for creative

### Cost Optimization

**GPT-4 Pricing (as of 2024):**
- Input: $0.03 per 1K tokens
- Output: $0.06 per 1K tokens

**Claude 3.5 Sonnet:**
- Input: $0.003 per 1K tokens (10x cheaper)
- Output: $0.015 per 1K tokens

**Strategy:**
- Use Claude for bulk processing (email categorization, summaries)
- Use GPT-4 for high-stakes decisions (borderline leads, retention interventions)
- Cache system prompts when possible

---

## 1. Lead Qualifier - GPT-4

### Basic Classification Prompt

```python
LEAD_QUALIFIER_SYSTEM = """You are an AI assistant helping a tax professional qualify leads.

Your job: Determine if a lead is a good fit based on their responses.

Good leads:
- Serious about hiring a professional (not DIY)
- Value quality over lowest price
- Have realistic expectations
- Ready to move forward (not just researching)

Bad leads:
- Shopping for lowest price
- Not ready to commit
- Unrealistic expectations
- Out of scope (wrong services)

Respond with:
1. QUALIFIED or NOT_QUALIFIED
2. Brief reason (1 sentence)
3. Confidence (Low/Medium/High)
"""

def generate_lead_prompt(lead_responses: dict) -> str:
    """Generate prompt for lead qualification"""
    
    prompt = f"""Evaluate this tax service lead:

Responses:
"""
    
    for question, answer in lead_responses.items():
        prompt += f"- {question}: {answer}\n"
    
    prompt += """
Classification:"""
    
    return prompt
```

**Example:**
```
User: Evaluate this tax service lead:

Responses:
- What services do you need?: Business tax return
- Have you filed professionally before?: Yes
- What matters most to you?: Quality service & expertise
- When do you need this?: Within 2 weeks
- Do you have documents ready?: Yes

Classification:
```

**Expected Output:**
```
QUALIFIED

Reason: Lead values quality, has prior experience, ready timeline, and documents prepared.

Confidence: High
```

### Conversational Lead Qualification

```python
CONVERSATIONAL_QUALIFIER_SYSTEM = """You are a friendly AI assistant for a tax preparation firm.

Your role:
- Ask questions to understand the lead's needs
- Be warm but professional
- Identify if they're a good fit
- Filter out price shoppers politely
- Keep responses under 50 words

Disqualify if:
- They say "just looking for prices" or "cheapest option"
- Not ready to start (just browsing)
- Outside your scope (e.g., international tax)

After 3-4 questions, make a recommendation to connect with a CPA or politely decline.
"""

CONVERSATIONAL_QUALIFIER_USER = """Lead said: "{user_message}"

Previous context:
{conversation_history}

Respond naturally. If you've gathered enough info, make your recommendation.
"""
```

**Example Conversation:**
```
BOT: Hi! I'm here to help you find the right tax professional. What type of tax services are you looking for?

USER: I need help with my business taxes.

BOT: Great! Is this for an LLC, S-Corp, or another business structure? And have you worked with a CPA before?

USER: LLC. I did my own taxes last year but it was too complicated.

BOT: That makes sense—LLCs can get complex! Are you looking for someone to handle your return this year, or also provide ongoing tax planning advice?

USER: Just the return. What's the cheapest option?

BOT: I understand budget is important. Our firm focuses on high-quality service rather than competing on price. If cost is your main priority, you might want to try TurboTax Self-Employed or a local tax prep chain. However, if you'd like expert guidance to maximize deductions and ensure accuracy, I can connect you with one of our CPAs. What sounds better?

USER: I'll try TurboTax. Thanks.

BOT: No problem! Best of luck with your filing. If you change your mind and want expert help, we're here.
```

---

## 2. Email Categorizer - Claude

### Classification Prompt

```python
EMAIL_CATEGORIZER_SYSTEM = """You are an email classification AI for a tax professional.

Classify emails into exactly one category:

1. **PROSPECTIVE** - New leads, pricing inquiries, first-time contacts
2. **ACTIVE_CLIENT** - Existing clients, ongoing work, document submissions
3. **OFFICE** - Admin, billing, scheduling, internal matters
4. **RETENTION** - Complaints, dissatisfaction, considering leaving
5. **SPAM** - Marketing, solicitations, irrelevant

Also detect flags:
- URGENT - Time-sensitive, needs immediate attention
- NEEDS_RESPONSE - Requires a reply
- NEGATIVE - Complaint or dissatisfaction

Respond in this format:
Category: [CATEGORY]
Flags: [FLAG1, FLAG2]
Reason: [1 sentence]
"""

def generate_email_prompt(email: dict) -> str:
    """Generate email classification prompt"""
    
    return f"""Classify this email:

From: {email['from']}
Subject: {email['subject']}
Body: {email['body'][:500]}...

Classification:"""
```

**Example:**
```
User: Classify this email:

From: jane@client.com
Subject: Quick question about my W-2
Body: Hi Laura, I just got my W-2. Should I send it now or wait for all my documents?

Classification:
```

**Expected Output:**
```
Category: ACTIVE_CLIENT
Flags: NEEDS_RESPONSE
Reason: Existing client asking about document submission process.
```

### Batch Classification (Cost-Optimized)

```python
BATCH_EMAIL_PROMPT = """Classify these {count} emails. For each, respond with just: Email [N]: [CATEGORY]

Categories: PROSPECTIVE, ACTIVE_CLIENT, OFFICE, RETENTION, SPAM

Emails:
{email_list}

Classifications:"""

def generate_batch_prompt(emails: List[dict], max_batch=20) -> str:
    """Generate batch classification prompt (lower cost per email)"""
    
    email_list = ""
    for i, email in enumerate(emails[:max_batch], 1):
        email_list += f"\n[{i}] From: {email['from']} | Subject: {email['subject']}"
    
    return BATCH_EMAIL_PROMPT.format(count=len(emails[:max_batch]), email_list=email_list)
```

**Example Output:**
```
Email 1: PROSPECTIVE
Email 2: ACTIVE_CLIENT
Email 3: SPAM
Email 4: ACTIVE_CLIENT
Email 5: OFFICE
...
```

---

## 3. Daily Digest - GPT-4

### Section Summary Prompt

```python
DIGEST_SUMMARY_SYSTEM = """You are summarizing messages for a tax professional's morning digest.

Guidelines:
- Be concise (2-3 sentences max)
- Highlight urgent items first
- Mention action items
- Use professional tone
- Focus on what matters

Example:
"3 urgent client questions about tax deadlines. 2 new leads from website. 1 billing issue needs follow-up."
"""

def generate_summary_prompt(messages: List[dict], section_name: str) -> str:
    """Generate summary for a digest section"""
    
    prompt = f"""Summarize this "{section_name}" section for a tax professional:

Messages ({len(messages)}):
"""
    
    for i, msg in enumerate(messages[:10], 1):
        prompt += f"{i}. {msg['from_name']}: {msg['subject']}\n"
        if msg.get('flags'):
            prompt += f"   Flags: {', '.join(msg['flags'])}\n"
    
    if len(messages) > 10:
        prompt += f"... and {len(messages) - 10} more\n"
    
    prompt += "\nSummary:"
    
    return prompt
```

**Example:**
```
User: Summarize this "Urgent - Action Required" section for a tax professional:

Messages (3):
1. John Smith: IRS audit notice received
   Flags: urgent, needs_response
2. Jane Doe: Missing W-2 from employer
   Flags: urgent, blocking_work
3. Bob Johnson: Extension deadline tomorrow
   Flags: urgent, deadline

Summary:
```

**Expected Output:**
```
3 urgent client matters need immediate attention: 1 IRS audit notice (John Smith), 1 missing W-2 blocking filing (Jane Doe), and 1 extension due tomorrow (Bob Johnson). All require responses today.
```

### Priority Explanation (for edge cases)

```python
PRIORITY_EXPLANATION_PROMPT = """Why should this message be prioritized {priority_level}?

Message:
From: {from_name}
Subject: {subject}
Body: {body_preview}
Category: {category}
Flags: {flags}

Context:
- Today's date: {today}
- Tax season: {is_tax_season}
- Client status: {client_status}

Explain in 1 sentence why this priority is appropriate.
"""
```

---

## 4. Retention Predictor - GPT-4

### Churn Risk Assessment

```python
RETENTION_SYSTEM = """You are a client retention analyst for a tax practice.

Your job: Identify warning signs that a client might leave.

Red flags:
- No contact for 6+ months
- Complained about price
- Mentioned competitor
- Slow to provide documents
- Didn't return last year
- Negative feedback

Respond with:
1. Risk Level: LOW/MEDIUM/HIGH/CRITICAL
2. Main concerns (bullet points)
3. Recommended action (1-2 sentences)
"""

def generate_retention_prompt(client: dict) -> str:
    """Generate retention risk assessment prompt"""
    
    prompt = f"""Assess retention risk for this tax client:

Client Profile:
- Client since: {client['client_since']}
- Last interaction: {client['last_interaction']}
- Lifetime value: ${client['lifetime_value']:,.2f}
- Projects completed: {client['projects_completed']}
- Complaints: {client['complaint_count']}
"""
    
    if client.get('custom_fields'):
        prompt += "\nTax-Specific:\n"
        for key, value in client['custom_fields'].items():
            prompt += f"- {key}: {value}\n"
    
    prompt += "\nAssessment:"
    
    return prompt
```

**Example:**
```
User: Assess retention risk for this tax client:

Client Profile:
- Client since: 2022-03-15
- Last interaction: 2025-06-10 (8 months ago)
- Lifetime value: $3,500
- Projects completed: 2
- Complaints: 1

Tax-Specific:
- years_not_returned: 1
- price_complaints: 1
- mentioned_competitor: True
- avg_document_delay_days: 35

Assessment:
```

**Expected Output:**
```
Risk Level: HIGH

Main concerns:
• Client hasn't returned this tax season (1 year gap)
• Previously complained about pricing
• Mentioned considering another CPA
• Has a pattern of slow document submission

Recommended action: Reach out personally within 48 hours with a win-back offer. Emphasize value over price and ask for feedback on last year's service. Consider a "welcome back" discount if appropriate.
```

### Win-Back Email Generation

```python
WINBACK_EMAIL_SYSTEM = """You are drafting a client win-back email for a tax professional.

Tone: Professional, warm, not desperate
Length: 150-200 words
Goal: Re-engage client who didn't return this year

Structure:
1. Acknowledge the gap ("We noticed...")
2. Express genuine concern
3. Offer value (not just discount)
4. Make it easy to respond
5. Professional sign-off

Do NOT:
- Guilt-trip
- Hard-sell
- Sound generic/automated
- Offer deep discounts immediately
"""

WINBACK_EMAIL_USER = """Draft a win-back email for:

Client: {client_name}
Last year: {last_service_date}
Issue: {main_concern}
Relationship: {relationship_quality}

Email:"""
```

**Example:**
```
User: Draft a win-back email for:

Client: Sarah Johnson
Last year: Filed 2023 return in April 2024
Issue: Mentioned our fees were higher than online services
Relationship: Generally positive, but price-sensitive

Email:
```

**Expected Output:**
```
Subject: Following up, Sarah

Hi Sarah,

I noticed we didn't connect for your 2024 tax return this year, and I wanted to reach out personally.

I remember you mentioned concerns about pricing last year, and I completely understand—tax services are an investment. What I want to emphasize is the value you're getting: proactive tax planning that has saved you thousands, direct access to a CPA (not just a preparer), and audit protection.

That said, I'm always open to finding a package that works for your situation. Would you be open to a quick call to discuss? I'd love to see if there's a way we can work together again.

Either way, I hope your taxes went smoothly this year. If you ever need anything—even just a quick question—I'm here.

Best regards,
Laura

P.S. If you'd like to come back for next year, I'd be happy to offer a loyalty discount for returning clients.
```

---

## 5. Multi-Use Prompts

### General Email Response Generator

```python
EMAIL_RESPONSE_SYSTEM = """You are drafting email responses for a tax professional.

Tone: Professional, friendly, clear
Length: 75-150 words
Goal: Answer question, maintain relationship, prompt next action

Always:
- Address by name
- Answer the specific question
- Provide next steps
- Sign off with name
"""

EMAIL_RESPONSE_USER = """Draft a response to:

From: {client_name}
Question: {client_question}
Context: {context}

Response:"""
```

### FAQ Answerer

```python
FAQ_SYSTEM = """You answer common tax questions for a CPA firm's website.

Guidelines:
- Accurate information (tax law)
- Simple language (non-expert audience)
- Include disclaimer: "This is general info, consult a CPA for your situation"
- 100-200 words
- Link to relevant resources when possible
"""

FAQ_USER = """Question: {question}

Answer:"""
```

**Example:**
```
User: Question: Can I deduct my home office?

Answer:
```

**Expected Output:**
```
Yes, you may be able to deduct your home office if you meet IRS requirements:

1. **Regular and exclusive use** - The space must be used only for business, regularly (not occasionally).
2. **Principal place of business** - It's your primary work location, or where you meet clients.

Common deductions include:
- Portion of rent/mortgage
- Utilities (electricity, internet)
- Home insurance
- Repairs and maintenance

You can use either the **simplified method** ($5/sq ft, up to 300 sq ft) or the **actual expense method** (calculating exact costs).

**Important:** Keep detailed records and photos. The IRS scrutinizes home office deductions, so documentation is critical.

*This is general information. Consult with a CPA to determine your specific eligibility and maximize your deduction.*

Want help? [Schedule a consultation →]
```

---

## 6. Industry-Specific Prompt Enhancements

### Tax Industry Context

```python
TAX_CONTEXT = """
Industry: Tax preparation & planning

Key dates:
- Tax season: February - April (peak workload)
- Extension deadline: October 15
- Quarterly estimates: April 15, June 15, Sept 15, Jan 15

Client types:
- Personal (1040): W-2 employees, simple returns
- Business (1120/1065): Complex, higher value
- Tax planning: High-value, strategic

Common pain points:
- Price shoppers (low value)
- Document delays (frustrating)
- Extension procrastinators
- Non-returning clients (churn)

Compliance:
- WISP (Written Information Security Plan)
- 3-year email retention
- IRS audit protocols
"""
```

### Law Industry Context

```python
LAW_CONTEXT = """
Industry: Law practice

Key factors:
- Court deadlines (CRITICAL - never miss)
- Attorney-client privilege (confidentiality)
- Retainer agreements (payment upfront)
- Billing disputes (common pain point)

Client types:
- Litigation: High-stakes, emotional
- Business law: Transactional, ongoing
- Family law: Sensitive, emotional
- Criminal defense: Urgent, complex

Communication:
- Formal tone for legal matters
- Detailed documentation (CYA)
- Clear billing explanations
- Expectation management (outcomes)
"""
```

---

## 7. Prompt Testing & Iteration

### A/B Testing Prompts

```python
def test_prompts(prompt_a: str, prompt_b: str, test_cases: List[dict]):
    """Compare two prompts on same test cases"""
    
    results_a = []
    results_b = []
    
    for case in test_cases:
        # Test prompt A
        response_a = call_gpt4(prompt_a.format(**case))
        results_a.append(evaluate_response(response_a, case['expected']))
        
        # Test prompt B
        response_b = call_gpt4(prompt_b.format(**case))
        results_b.append(evaluate_response(response_b, case['expected']))
    
    accuracy_a = sum(results_a) / len(results_a)
    accuracy_b = sum(results_b) / len(results_b)
    
    print(f"Prompt A: {accuracy_a:.1%} accuracy")
    print(f"Prompt B: {accuracy_b:.1%} accuracy")
    print(f"Winner: {'A' if accuracy_a > accuracy_b else 'B'}")
```

### Prompt Versioning

```python
PROMPT_VERSIONS = {
    "lead_qualifier": {
        "v1.0": "Original prompt...",
        "v1.1": "Improved with examples...",
        "v2.0": "Complete rewrite...",
        "current": "v2.0"
    }
}

def get_prompt(name: str, version: str = "current") -> str:
    """Get prompt by name and version"""
    if version == "current":
        version = PROMPT_VERSIONS[name]["current"]
    return PROMPT_VERSIONS[name][version]
```

---

## Cost Estimation

**Example: 1000 emails/day**
- Avg email: 300 tokens (input) + 50 tokens (output)
- Claude cost: (300 * 0.003 + 50 * 0.015) / 1000 = $0.0016 per email
- **Daily cost: $1.60**
- **Monthly cost: ~$48**

**Example: 100 leads/month**
- Avg lead: 200 tokens (input) + 100 tokens (output)
- GPT-4 cost: (200 * 0.03 + 100 * 0.06) / 1000 = $0.012 per lead
- **Monthly cost: $1.20**

**Total monthly LLM cost (Laura's practice): ~$50**

---

## Best Practices Summary

1. **Use system prompts** - Set context once, reuse
2. **Provide examples** - Few-shot learning improves accuracy
3. **Limit output length** - Saves tokens and forces conciseness
4. **Cache aggressively** - Don't re-classify the same email
5. **Batch when possible** - Lower cost per item
6. **Monitor costs** - Set alerts at $100/month
7. **Version prompts** - Track what works, iterate
8. **Test thoroughly** - Human review first 100 outputs
9. **Fail gracefully** - Have fallback rules if API fails
10. **User feedback** - Let Laura correct mistakes, improve prompts

---

*Prompts are code. Version, test, and optimize them like you would any other code.*
