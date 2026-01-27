"""
Kronos AI - Lead Qualifier Bot
===============================
Industry-agnostic lead qualification with pluggable question sets.
Filters price shoppers and scores lead quality.

Author: Kronos AI Team
Date: 2026-01-26
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class Question:
    """A qualification question"""
    id: str
    text: str
    type: str  # 'multiple_choice', 'text', 'yes_no', 'scale'
    options: Optional[List[str]] = None
    weight: float = 1.0  # Importance multiplier
    disqualify_on: Optional[List[str]] = None  # Auto-disqualify answers


@dataclass
class QuestionSet:
    """Industry-specific question set"""
    industry: str
    questions: List[Question]
    passing_score: float = 70.0  # Minimum score to qualify
    

@dataclass
class LeadResponse:
    """A lead's response to qualification"""
    lead_id: str
    question_id: str
    answer: str
    timestamp: datetime


@dataclass
class LeadScore:
    """Calculated lead quality score"""
    lead_id: str
    total_score: float
    max_score: float
    percentage: float
    qualified: bool
    flags: List[str]  # Warning flags (e.g., 'price_shopper', 'not_ready')
    responses: Dict[str, str]
    timestamp: datetime


# ============================================================================
# INDUSTRY MODULES - Pluggable Question Sets
# ============================================================================

TAX_QUESTIONS = QuestionSet(
    industry="tax",
    questions=[
        Question(
            id="tax_services",
            text="What tax services do you need?",
            type="multiple_choice",
            options=[
                "Personal tax return (1040)",
                "Business tax return (1120/1065)",
                "Tax planning & strategy",
                "Amended return or IRS issue",
                "Just shopping for prices"
            ],
            weight=1.5,
            disqualify_on=["Just shopping for prices"]
        ),
        Question(
            id="filing_history",
            text="Have you filed taxes professionally before?",
            type="yes_no",
            weight=1.0
        ),
        Question(
            id="situation_complexity",
            text="How complex is your tax situation?",
            type="multiple_choice",
            options=[
                "Simple (W-2 only)",
                "Moderate (W-2 + investments)",
                "Complex (Business, real estate, multiple states)",
                "Very complex (International, trusts, etc.)"
            ],
            weight=1.5
        ),
        Question(
            id="timeline",
            text="When do you need this completed?",
            type="multiple_choice",
            options=[
                "ASAP (urgent)",
                "Within 2 weeks",
                "Before deadline (not urgent)",
                "Just researching"
            ],
            weight=1.2,
            disqualify_on=["Just researching"]
        ),
        Question(
            id="price_sensitivity",
            text="What matters most to you?",
            type="multiple_choice",
            options=[
                "Quality service & expertise",
                "Fast turnaround",
                "Lowest price",
                "Relationship & trust"
            ],
            weight=2.0,
            disqualify_on=["Lowest price"]
        ),
        Question(
            id="referral_source",
            text="How did you hear about us?",
            type="multiple_choice",
            options=[
                "Referral from friend/family",
                "Google search",
                "Social media",
                "Flyer/mailer",
                "Previous client"
            ],
            weight=1.3
        ),
        Question(
            id="ready_to_start",
            text="Do you have your tax documents ready to provide?",
            type="yes_no",
            weight=1.5
        )
    ],
    passing_score=65.0
)


LAW_QUESTIONS = QuestionSet(
    industry="law",
    questions=[
        Question(
            id="legal_issue",
            text="What type of legal issue do you have?",
            type="multiple_choice",
            options=[
                "Business formation/contracts",
                "Real estate",
                "Family law",
                "Criminal defense",
                "Personal injury",
                "Just browsing"
            ],
            weight=1.5,
            disqualify_on=["Just browsing"]
        ),
        Question(
            id="prior_attorney",
            text="Have you consulted with an attorney about this before?",
            type="yes_no",
            weight=1.0
        ),
        Question(
            id="urgency",
            text="What's your timeline?",
            type="multiple_choice",
            options=[
                "Emergency (court date/deadline imminent)",
                "Urgent (next 1-2 weeks)",
                "Moderate (next month)",
                "No rush (just exploring)"
            ],
            weight=1.8,
            disqualify_on=["No rush (just exploring)"]
        ),
        Question(
            id="budget_awareness",
            text="Are you aware legal services require a retainer?",
            type="yes_no",
            weight=1.5
        )
    ],
    passing_score=60.0
)


# ============================================================================
# SCORING ENGINE - Universal Logic
# ============================================================================

class LeadQualifier:
    """Universal lead qualification engine with industry modules"""
    
    def __init__(self, question_set: QuestionSet):
        self.question_set = question_set
        self.responses: Dict[str, Dict[str, str]] = {}  # lead_id -> {q_id: answer}
        
    def get_next_question(self, lead_id: str) -> Optional[Question]:
        """Get the next unanswered question for a lead"""
        if lead_id not in self.responses:
            self.responses[lead_id] = {}
        
        answered = set(self.responses[lead_id].keys())
        
        for q in self.question_set.questions:
            if q.id not in answered:
                return q
        
        return None  # All questions answered
    
    def record_response(self, lead_id: str, question_id: str, answer: str) -> bool:
        """Record a lead's answer. Returns False if disqualified."""
        if lead_id not in self.responses:
            self.responses[lead_id] = {}
        
        self.responses[lead_id][question_id] = answer
        
        # Check for auto-disqualification
        question = next((q for q in self.question_set.questions if q.id == question_id), None)
        if question and question.disqualify_on and answer in question.disqualify_on:
            return False  # Disqualified
        
        return True
    
    def calculate_score(self, lead_id: str) -> LeadScore:
        """Calculate final lead quality score"""
        if lead_id not in self.responses:
            raise ValueError(f"No responses found for lead {lead_id}")
        
        responses = self.responses[lead_id]
        total_score = 0.0
        max_score = 0.0
        flags = []
        
        for question in self.question_set.questions:
            q_id = question.id
            max_score += 100 * question.weight
            
            if q_id not in responses:
                flags.append(f"incomplete:{q_id}")
                continue
            
            answer = responses[q_id]
            
            # Check disqualifiers
            if question.disqualify_on and answer in question.disqualify_on:
                flags.append(f"disqualified:{q_id}:{answer}")
                continue  # No points for disqualifying answers
            
            # Score the answer
            score = self._score_answer(question, answer)
            total_score += score * question.weight
        
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        qualified = percentage >= self.question_set.passing_score and len([f for f in flags if f.startswith("disqualified")]) == 0
        
        return LeadScore(
            lead_id=lead_id,
            total_score=total_score,
            max_score=max_score,
            percentage=round(percentage, 2),
            qualified=qualified,
            flags=flags,
            responses=responses.copy(),
            timestamp=datetime.now()
        )
    
    def _score_answer(self, question: Question, answer: str) -> float:
        """Score an individual answer (0-100 points)"""
        if question.type == "yes_no":
            # Industry-specific scoring rules
            if self.question_set.industry == "tax":
                return self._score_tax_yes_no(question.id, answer)
            elif self.question_set.industry == "law":
                return self._score_law_yes_no(question.id, answer)
        
        elif question.type == "multiple_choice":
            if self.question_set.industry == "tax":
                return self._score_tax_multiple_choice(question.id, answer)
            elif self.question_set.industry == "law":
                return self._score_law_multiple_choice(question.id, answer)
        
        # Default: any answer = 50 points
        return 50.0
    
    # ========================================================================
    # TAX SCORING RULES
    # ========================================================================
    
    def _score_tax_yes_no(self, question_id: str, answer: str) -> float:
        """Score yes/no questions for tax industry"""
        scoring = {
            "filing_history": {"yes": 80, "no": 40},  # Previous clients better
            "ready_to_start": {"yes": 100, "no": 30}  # Documents ready = serious
        }
        return scoring.get(question_id, {}).get(answer.lower(), 50.0)
    
    def _score_tax_multiple_choice(self, question_id: str, answer: str) -> float:
        """Score multiple choice for tax industry"""
        scoring = {
            "tax_services": {
                "Personal tax return (1040)": 70,
                "Business tax return (1120/1065)": 90,
                "Tax planning & strategy": 100,
                "Amended return or IRS issue": 85,
                "Just shopping for prices": 0
            },
            "situation_complexity": {
                "Simple (W-2 only)": 50,
                "Moderate (W-2 + investments)": 70,
                "Complex (Business, real estate, multiple states)": 90,
                "Very complex (International, trusts, etc.)": 100
            },
            "timeline": {
                "ASAP (urgent)": 90,
                "Within 2 weeks": 80,
                "Before deadline (not urgent)": 60,
                "Just researching": 0
            },
            "price_sensitivity": {
                "Quality service & expertise": 100,
                "Fast turnaround": 80,
                "Lowest price": 0,
                "Relationship & trust": 100
            },
            "referral_source": {
                "Referral from friend/family": 100,
                "Google search": 60,
                "Social media": 50,
                "Flyer/mailer": 40,
                "Previous client": 100
            }
        }
        return scoring.get(question_id, {}).get(answer, 50.0)
    
    # ========================================================================
    # LAW SCORING RULES
    # ========================================================================
    
    def _score_law_yes_no(self, question_id: str, answer: str) -> float:
        """Score yes/no questions for law industry"""
        scoring = {
            "prior_attorney": {"yes": 70, "no": 80},  # New clients = fresh start
            "budget_awareness": {"yes": 100, "no": 20}  # Must understand costs
        }
        return scoring.get(question_id, {}).get(answer.lower(), 50.0)
    
    def _score_law_multiple_choice(self, question_id: str, answer: str) -> float:
        """Score multiple choice for law industry"""
        scoring = {
            "legal_issue": {
                "Business formation/contracts": 90,
                "Real estate": 85,
                "Family law": 80,
                "Criminal defense": 95,
                "Personal injury": 90,
                "Just browsing": 0
            },
            "urgency": {
                "Emergency (court date/deadline imminent)": 100,
                "Urgent (next 1-2 weeks)": 90,
                "Moderate (next month)": 70,
                "No rush (just exploring)": 0
            }
        }
        return scoring.get(question_id, {}).get(answer, 50.0)


# ============================================================================
# API INTEGRATION
# ============================================================================

def integrate_with_lead_form(form_data: Dict, industry: str = "tax") -> LeadScore:
    """
    Integration point for website lead capture forms.
    
    Args:
        form_data: Dictionary with lead responses
        industry: Which industry module to use
    
    Returns:
        LeadScore object with qualification result
    """
    question_sets = {
        "tax": TAX_QUESTIONS,
        "law": LAW_QUESTIONS
    }
    
    if industry not in question_sets:
        raise ValueError(f"Unknown industry: {industry}")
    
    qualifier = LeadQualifier(question_sets[industry])
    lead_id = form_data.get("lead_id", f"lead_{datetime.now().timestamp()}")
    
    # Record all responses
    for question in qualifier.question_set.questions:
        if question.id in form_data:
            is_qualified = qualifier.record_response(
                lead_id, 
                question.id, 
                form_data[question.id]
            )
            if not is_qualified:
                # Early exit on disqualification
                break
    
    # Calculate final score
    return qualifier.calculate_score(lead_id)


def generate_followup_message(score: LeadScore, industry: str = "tax") -> str:
    """Generate automated response based on qualification result"""
    if score.qualified:
        if industry == "tax":
            return f"""Thank you for reaching out! Based on your responses, you're a great fit for our services.

Your qualification score: {score.percentage}%

Next steps:
1. We'll review your information within 24 hours
2. A team member will reach out to schedule a consultation
3. Please have your tax documents ready

Looking forward to working with you!"""
        elif industry == "law":
            return f"""Thank you for contacting us. Your matter appears to be a good fit for our practice.

Qualification score: {score.percentage}%

Next steps:
1. We'll review your case details within 24 hours
2. A attorney will reach out to discuss next steps
3. Please gather any relevant documents

We appreciate your interest."""
    
    else:
        # Polite decline
        if industry == "tax":
            return """Thank you for your interest in our tax services.

Based on your current needs, we may not be the best fit at this time. We recommend:
- TurboTax or H&R Block for simple returns
- IRS Free File if you qualify
- Local tax prep services for price-focused needs

We wish you the best with your tax filing!"""
        elif industry == "law":
            return """Thank you for reaching out.

Based on your situation, we may not be the ideal fit at this time. We recommend:
- Your local bar association's referral service
- Legal aid societies for budget-conscious needs
- Online legal services for exploratory questions

We wish you the best with your legal matter."""


# ============================================================================
# CHATBOT INTERFACE
# ============================================================================

class ConversationalQualifier:
    """Interactive chatbot for lead qualification"""
    
    def __init__(self, industry: str = "tax"):
        question_sets = {
            "tax": TAX_QUESTIONS,
            "law": LAW_QUESTIONS
        }
        self.qualifier = LeadQualifier(question_sets[industry])
        self.industry = industry
    
    def start_conversation(self, lead_id: str) -> str:
        """Begin qualification conversation"""
        greeting = {
            "tax": "Hi! I'm the Kronos qualification assistant. I'll ask a few quick questions to understand your tax needs better.",
            "law": "Hello! I'm here to learn more about your legal needs. I'll ask a few questions to see how we can help."
        }
        
        first_question = self.qualifier.get_next_question(lead_id)
        if first_question:
            return f"{greeting[self.industry]}\n\n{self._format_question(first_question)}"
        
        return greeting[self.industry]
    
    def process_answer(self, lead_id: str, answer: str) -> Tuple[bool, str]:
        """
        Process an answer and return next question or result.
        
        Returns:
            (is_complete, message)
        """
        # Get current question
        current_q = self.qualifier.get_next_question(lead_id)
        if not current_q:
            # Already complete
            score = self.qualifier.calculate_score(lead_id)
            return (True, generate_followup_message(score, self.industry))
        
        # Record the response
        is_qualified = self.qualifier.record_response(lead_id, current_q.id, answer)
        
        if not is_qualified:
            # Disqualified early
            score = self.qualifier.calculate_score(lead_id)
            return (True, generate_followup_message(score, self.industry))
        
        # Get next question
        next_q = self.qualifier.get_next_question(lead_id)
        
        if next_q:
            return (False, self._format_question(next_q))
        else:
            # All questions answered
            score = self.qualifier.calculate_score(lead_id)
            return (True, generate_followup_message(score, self.industry))
    
    def _format_question(self, question: Question) -> str:
        """Format a question for display"""
        text = question.text
        
        if question.type == "multiple_choice" and question.options:
            options_text = "\n".join([f"  {i+1}. {opt}" for i, opt in enumerate(question.options)])
            text += f"\n\n{options_text}\n\nPlease reply with the number or text of your choice."
        elif question.type == "yes_no":
            text += "\n\nPlease reply: Yes or No"
        
        return text


# ============================================================================
# TESTING & METRICS
# ============================================================================

def test_qualifier():
    """Test the lead qualifier with sample data"""
    print("=" * 60)
    print("KRONOS LEAD QUALIFIER - TEST SUITE")
    print("=" * 60)
    
    # Test 1: High-quality tax lead
    print("\n[TEST 1] High-quality tax lead (should PASS)")
    print("-" * 60)
    
    good_lead = {
        "lead_id": "test_001",
        "tax_services": "Tax planning & strategy",
        "filing_history": "yes",
        "situation_complexity": "Complex (Business, real estate, multiple states)",
        "timeline": "Within 2 weeks",
        "price_sensitivity": "Quality service & expertise",
        "referral_source": "Referral from friend/family",
        "ready_to_start": "yes"
    }
    
    score = integrate_with_lead_form(good_lead, "tax")
    print(f"Score: {score.percentage}% (Qualified: {score.qualified})")
    print(f"Flags: {score.flags}")
    print(f"\nResponse message:\n{generate_followup_message(score, 'tax')}")
    
    # Test 2: Price shopper (should FAIL)
    print("\n\n[TEST 2] Price shopper (should FAIL)")
    print("-" * 60)
    
    price_shopper = {
        "lead_id": "test_002",
        "tax_services": "Personal tax return (1040)",
        "filing_history": "no",
        "situation_complexity": "Simple (W-2 only)",
        "timeline": "Before deadline (not urgent)",
        "price_sensitivity": "Lowest price",  # DISQUALIFIER
        "referral_source": "Google search",
        "ready_to_start": "no"
    }
    
    score = integrate_with_lead_form(price_shopper, "tax")
    print(f"Score: {score.percentage}% (Qualified: {score.qualified})")
    print(f"Flags: {score.flags}")
    print(f"\nResponse message:\n{generate_followup_message(score, 'tax')}")
    
    # Test 3: Moderate lead (borderline)
    print("\n\n[TEST 3] Moderate lead (borderline)")
    print("-" * 60)
    
    moderate_lead = {
        "lead_id": "test_003",
        "tax_services": "Personal tax return (1040)",
        "filing_history": "yes",
        "situation_complexity": "Moderate (W-2 + investments)",
        "timeline": "Within 2 weeks",
        "price_sensitivity": "Fast turnaround",
        "referral_source": "Social media",
        "ready_to_start": "yes"
    }
    
    score = integrate_with_lead_form(moderate_lead, "tax")
    print(f"Score: {score.percentage}% (Qualified: {score.qualified})")
    print(f"Flags: {score.flags}")
    
    # Test 4: Conversational bot
    print("\n\n[TEST 4] Conversational Bot Interface")
    print("-" * 60)
    
    bot = ConversationalQualifier("tax")
    lead_id = "test_bot_001"
    
    # Start conversation
    message = bot.start_conversation(lead_id)
    print(f"BOT: {message}")
    
    # Simulate answers
    answers = [
        "Tax planning & strategy",
        "yes",
        "Complex (Business, real estate, multiple states)",
        "ASAP (urgent)",
        "Quality service & expertise",
        "Referral from friend/family",
        "yes"
    ]
    
    for i, answer in enumerate(answers):
        print(f"\nUSER: {answer}")
        is_complete, response = bot.process_answer(lead_id, answer)
        print(f"BOT: {response}")
        
        if is_complete:
            print("\n✅ Qualification complete!")
            break
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_qualifier()
