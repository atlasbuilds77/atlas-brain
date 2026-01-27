"""
Kronos AI - Retention Predictor
================================
ML model to predict client churn risk using industry-specific signals.
Identifies at-risk clients before they leave.

Author: Kronos AI Team
Date: 2026-01-26
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import math


class RiskLevel(Enum):
    """Client retention risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ClientProfile:
    """Client profile for churn prediction"""
    client_id: str
    industry: str
    
    # Demographics
    client_since: datetime
    lifetime_value: float
    service_type: str
    
    # Engagement metrics
    last_interaction: datetime
    interaction_frequency: float  # Per month
    response_time_hours: float
    messages_sent: int
    messages_received: int
    
    # Service metrics
    projects_completed: int
    projects_cancelled: int
    average_project_value: float
    payment_history_score: float  # 0-1, 1=always on time
    
    # Sentiment metrics
    complaint_count: int
    positive_feedback_count: int
    support_tickets: int
    
    # Industry-specific fields
    custom_fields: Dict = field(default_factory=dict)


@dataclass
class ChurnSignal:
    """A signal indicating potential churn"""
    signal_type: str
    severity: float  # 0-1, 1=critical
    description: str
    detected_at: datetime


@dataclass
class RetentionPrediction:
    """Churn prediction result"""
    client_id: str
    risk_level: RiskLevel
    risk_score: float  # 0-100
    confidence: float  # 0-1
    signals: List[ChurnSignal]
    recommended_actions: List[str]
    predicted_at: datetime


# ============================================================================
# INDUSTRY-SPECIFIC SIGNAL DETECTORS
# ============================================================================

class SignalDetector:
    """Base class for detecting churn signals"""
    
    @staticmethod
    def detect_signals(profile: ClientProfile) -> List[ChurnSignal]:
        """Detect churn signals from client profile"""
        signals = []
        
        # Universal signals
        signals.extend(SignalDetector._detect_engagement_drop(profile))
        signals.extend(SignalDetector._detect_payment_issues(profile))
        signals.extend(SignalDetector._detect_complaints(profile))
        signals.extend(SignalDetector._detect_inactivity(profile))
        
        return signals
    
    @staticmethod
    def _detect_engagement_drop(profile: ClientProfile) -> List[ChurnSignal]:
        """Detect drop in engagement"""
        signals = []
        
        # Last interaction recency
        days_since = (datetime.now() - profile.last_interaction).days
        
        if days_since > 180:  # 6 months
            signals.append(ChurnSignal(
                signal_type="no_contact",
                severity=0.8,
                description=f"No contact in {days_since} days",
                detected_at=datetime.now()
            ))
        elif days_since > 90:  # 3 months
            signals.append(ChurnSignal(
                signal_type="low_contact",
                severity=0.5,
                description=f"Limited contact ({days_since} days since last interaction)",
                detected_at=datetime.now()
            ))
        
        # Frequency drop
        if profile.interaction_frequency < 0.5:  # Less than once per 2 months
            signals.append(ChurnSignal(
                signal_type="frequency_drop",
                severity=0.6,
                description=f"Low interaction frequency ({profile.interaction_frequency:.1f}/month)",
                detected_at=datetime.now()
            ))
        
        # One-sided communication
        if profile.messages_received > 0:
            response_ratio = profile.messages_sent / profile.messages_received
            if response_ratio < 0.3:  # Client rarely responds
                signals.append(ChurnSignal(
                    signal_type="unresponsive",
                    severity=0.7,
                    description="Client rarely responds to messages",
                    detected_at=datetime.now()
                ))
        
        return signals
    
    @staticmethod
    def _detect_payment_issues(profile: ClientProfile) -> List[ChurnSignal]:
        """Detect payment-related issues"""
        signals = []
        
        if profile.payment_history_score < 0.7:
            signals.append(ChurnSignal(
                signal_type="payment_issues",
                severity=0.6,
                description=f"Payment history score: {profile.payment_history_score:.0%}",
                detected_at=datetime.now()
            ))
        
        return signals
    
    @staticmethod
    def _detect_complaints(profile: ClientProfile) -> List[ChurnSignal]:
        """Detect complaint patterns"""
        signals = []
        
        if profile.complaint_count > 0:
            severity = min(profile.complaint_count * 0.3, 1.0)
            signals.append(ChurnSignal(
                signal_type="complaints",
                severity=severity,
                description=f"{profile.complaint_count} complaints filed",
                detected_at=datetime.now()
            ))
        
        # Support tickets without resolution
        if profile.support_tickets > 3:
            signals.append(ChurnSignal(
                signal_type="support_issues",
                severity=0.5,
                description=f"{profile.support_tickets} support tickets",
                detected_at=datetime.now()
            ))
        
        return signals
    
    @staticmethod
    def _detect_inactivity(profile: ClientProfile) -> List[ChurnSignal]:
        """Detect overall inactivity"""
        signals = []
        
        # Client age vs activity
        months_active = (datetime.now() - profile.client_since).days / 30
        expected_projects = months_active * 0.5  # Expect 1 project per 2 months
        
        if profile.projects_completed < expected_projects * 0.3:
            signals.append(ChurnSignal(
                signal_type="low_activity",
                severity=0.6,
                description=f"Only {profile.projects_completed} projects completed",
                detected_at=datetime.now()
            ))
        
        return signals


class TaxSignalDetector(SignalDetector):
    """Tax-specific churn signals"""
    
    @staticmethod
    def detect_signals(profile: ClientProfile) -> List[ChurnSignal]:
        """Tax-specific signal detection"""
        signals = SignalDetector.detect_signals(profile)
        
        # Tax-specific signals
        custom = profile.custom_fields
        
        # Non-return after tax season
        years_not_returned = custom.get("years_not_returned", 0)
        if years_not_returned >= 2:
            signals.append(ChurnSignal(
                signal_type="non_return",
                severity=0.9,
                description=f"Client has not returned for {years_not_returned} years",
                detected_at=datetime.now()
            ))
        elif years_not_returned == 1:
            signals.append(ChurnSignal(
                signal_type="missed_season",
                severity=0.7,
                description="Client missed last tax season",
                detected_at=datetime.now()
            ))
        
        # Price complaints
        price_complaints = custom.get("price_complaints", 0)
        if price_complaints > 0:
            signals.append(ChurnSignal(
                signal_type="price_sensitivity",
                severity=0.8,
                description=f"{price_complaints} price-related complaints",
                detected_at=datetime.now()
            ))
        
        # Document submission delays
        avg_delay_days = custom.get("avg_document_delay_days", 0)
        if avg_delay_days > 30:
            signals.append(ChurnSignal(
                signal_type="submission_delays",
                severity=0.5,
                description=f"Average {avg_delay_days}-day delay providing documents",
                detected_at=datetime.now()
            ))
        
        # Organizer not completed
        organizer_sent = custom.get("organizer_sent", False)
        organizer_completed = custom.get("organizer_completed", False)
        if organizer_sent and not organizer_completed:
            days_since_sent = custom.get("organizer_days_since_sent", 0)
            if days_since_sent > 30:
                signals.append(ChurnSignal(
                    signal_type="organizer_incomplete",
                    severity=0.6,
                    description=f"Tax organizer incomplete for {days_since_sent} days",
                    detected_at=datetime.now()
                ))
        
        # Extension filed (procrastination)
        extensions_filed = custom.get("extensions_filed", 0)
        if extensions_filed >= 2:
            signals.append(ChurnSignal(
                signal_type="chronic_extension",
                severity=0.4,
                description=f"{extensions_filed} extensions filed (procrastination pattern)",
                detected_at=datetime.now()
            ))
        
        # Competitor inquiry
        mentioned_competitor = custom.get("mentioned_competitor", False)
        if mentioned_competitor:
            signals.append(ChurnSignal(
                signal_type="shopping_around",
                severity=0.85,
                description="Client mentioned competitor or shopping around",
                detected_at=datetime.now()
            ))
        
        return signals


class LawSignalDetector(SignalDetector):
    """Law-specific churn signals"""
    
    @staticmethod
    def detect_signals(profile: ClientProfile) -> List[ChurnSignal]:
        """Law-specific signal detection"""
        signals = SignalDetector.detect_signals(profile)
        
        custom = profile.custom_fields
        
        # Case outcome dissatisfaction
        case_outcome = custom.get("case_outcome", "")
        if case_outcome in ["lost", "settled_low", "dismissed"]:
            signals.append(ChurnSignal(
                signal_type="poor_outcome",
                severity=0.9,
                description=f"Unhappy with case outcome: {case_outcome}",
                detected_at=datetime.now()
            ))
        
        # Billing disputes
        billing_disputes = custom.get("billing_disputes", 0)
        if billing_disputes > 0:
            signals.append(ChurnSignal(
                signal_type="billing_dispute",
                severity=0.8,
                description=f"{billing_disputes} billing disputes",
                detected_at=datetime.now()
            ))
        
        # Communication dissatisfaction
        response_complaints = custom.get("response_time_complaints", 0)
        if response_complaints > 0:
            signals.append(ChurnSignal(
                signal_type="poor_communication",
                severity=0.7,
                description="Complaints about attorney responsiveness",
                detected_at=datetime.now()
            ))
        
        # Lost motion/hearing
        lost_motions = custom.get("lost_motions", 0)
        if lost_motions > 0:
            signals.append(ChurnSignal(
                signal_type="lost_motion",
                severity=0.6,
                description=f"{lost_motions} motions lost",
                detected_at=datetime.now()
            ))
        
        return signals


# ============================================================================
# CHURN PREDICTION MODEL
# ============================================================================

class RetentionPredictor:
    """Predict client churn risk"""
    
    def __init__(self, industry: str = "tax"):
        self.industry = industry
        self.signal_detector = self._load_detector(industry)
        
    def _load_detector(self, industry: str) -> SignalDetector:
        """Load industry-specific signal detector"""
        if industry == "tax":
            return TaxSignalDetector()
        elif industry == "law":
            return LawSignalDetector()
        else:
            return SignalDetector()
    
    def predict(self, profile: ClientProfile) -> RetentionPrediction:
        """
        Predict churn risk for a client.
        
        Args:
            profile: Client profile data
        
        Returns:
            RetentionPrediction with risk score and recommendations
        """
        # Detect signals
        signals = self.signal_detector.detect_signals(profile)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(profile, signals)
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Calculate confidence
        confidence = self._calculate_confidence(profile, signals)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(profile, signals, risk_level)
        
        return RetentionPrediction(
            client_id=profile.client_id,
            risk_level=risk_level,
            risk_score=round(risk_score, 2),
            confidence=round(confidence, 3),
            signals=signals,
            recommended_actions=recommendations,
            predicted_at=datetime.now()
        )
    
    def _calculate_risk_score(
        self,
        profile: ClientProfile,
        signals: List[ChurnSignal]
    ) -> float:
        """Calculate overall risk score (0-100)"""
        if not signals:
            return 0.0
        
        # Weighted signal severity
        signal_score = sum(s.severity for s in signals) / len(signals) * 100
        
        # Tenure adjustment (newer clients more volatile)
        months_active = (datetime.now() - profile.client_since).days / 30
        tenure_factor = 1.0 if months_active < 12 else 0.8
        
        # Value adjustment (high-value clients get attention even with low signals)
        value_factor = 1.0
        if profile.lifetime_value < 1000:
            value_factor = 1.2  # Higher risk if low value
        elif profile.lifetime_value > 10000:
            value_factor = 0.9  # Lower threshold for high-value
        
        final_score = signal_score * tenure_factor * value_factor
        
        return min(max(final_score, 0), 100)
    
    def _determine_risk_level(self, risk_score: float) -> RiskLevel:
        """Map risk score to risk level"""
        if risk_score >= 75:
            return RiskLevel.CRITICAL
        elif risk_score >= 50:
            return RiskLevel.HIGH
        elif risk_score >= 25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _calculate_confidence(
        self,
        profile: ClientProfile,
        signals: List[ChurnSignal]
    ) -> float:
        """Calculate confidence in prediction (0-1)"""
        # More signals = higher confidence
        signal_confidence = min(len(signals) / 5, 1.0)
        
        # More data = higher confidence
        data_points = (
            profile.messages_sent +
            profile.messages_received +
            profile.projects_completed +
            profile.complaint_count
        )
        data_confidence = min(data_points / 20, 1.0)
        
        # Newer clients = lower confidence
        months_active = (datetime.now() - profile.client_since).days / 30
        tenure_confidence = min(months_active / 12, 1.0)
        
        # Average the factors
        return (signal_confidence + data_confidence + tenure_confidence) / 3
    
    def _generate_recommendations(
        self,
        profile: ClientProfile,
        signals: List[ChurnSignal],
        risk_level: RiskLevel
    ) -> List[str]:
        """Generate action recommendations based on risk"""
        recommendations = []
        
        if risk_level == RiskLevel.LOW:
            recommendations.append("Continue normal communication")
            recommendations.append("Send satisfaction survey quarterly")
            return recommendations
        
        # Group signals by type
        signal_types = {s.signal_type for s in signals}
        
        # Engagement issues
        if "no_contact" in signal_types or "low_contact" in signal_types:
            recommendations.append("⚠️ URGENT: Reach out personally within 48 hours")
            recommendations.append("Schedule check-in call or meeting")
        
        if "frequency_drop" in signal_types:
            recommendations.append("Send value-add content (newsletter, tips)")
            recommendations.append("Invite to client appreciation event")
        
        if "unresponsive" in signal_types:
            recommendations.append("Try different communication channel (phone vs email)")
            recommendations.append("Ask if communication preferences have changed")
        
        # Complaint/satisfaction issues
        if "complaints" in signal_types or "support_issues" in signal_types:
            recommendations.append("⚠️ CRITICAL: Schedule manager/owner call")
            recommendations.append("Investigate and resolve outstanding issues")
            recommendations.append("Consider service recovery (discount, free consultation)")
        
        # Payment issues
        if "payment_issues" in signal_types:
            recommendations.append("Review billing/payment plan options")
            recommendations.append("Discuss value vs cost")
        
        # Industry-specific recommendations
        if self.industry == "tax":
            if "non_return" in signal_types:
                recommendations.append("🎯 Send win-back campaign")
                recommendations.append("Offer first consultation free")
                recommendations.append("Highlight new services or improvements")
            
            if "price_sensitivity" in signal_types:
                recommendations.append("Emphasize value and expertise over price")
                recommendations.append("Offer payment plans or package discounts")
            
            if "organizer_incomplete" in signal_types:
                recommendations.append("Send friendly reminder about tax organizer")
                recommendations.append("Offer to walk through organizer together")
            
            if "shopping_around" in signal_types:
                recommendations.append("🚨 IMMEDIATE ACTION REQUIRED")
                recommendations.append("Personal call from owner/manager")
                recommendations.append("Highlight unique value proposition")
                recommendations.append("Consider retention offer")
        
        elif self.industry == "law":
            if "poor_outcome" in signal_types:
                recommendations.append("⚠️ Schedule expectation-setting meeting")
                recommendations.append("Explain legal process and realistic outcomes")
                recommendations.append("Consider pro bono follow-up work if appropriate")
            
            if "billing_dispute" in signal_types:
                recommendations.append("Review billing with client line by line")
                recommendations.append("Offer payment plan or adjustment if warranted")
            
            if "poor_communication" in signal_types:
                recommendations.append("Set up regular update schedule")
                recommendations.append("Assign dedicated paralegal for communication")
        
        # Default critical actions
        if risk_level == RiskLevel.CRITICAL:
            if not any("URGENT" in r or "CRITICAL" in r for r in recommendations):
                recommendations.insert(0, "🚨 CRITICAL: Personal outreach within 24 hours")
        
        return recommendations


# ============================================================================
# BATCH ANALYSIS
# ============================================================================

class BatchRetentionAnalysis:
    """Analyze retention risk across multiple clients"""
    
    def __init__(self, predictor: RetentionPredictor):
        self.predictor = predictor
        self.predictions: List[RetentionPrediction] = []
    
    def analyze_client_base(
        self,
        clients: List[ClientProfile]
    ) -> Dict[RiskLevel, List[RetentionPrediction]]:
        """
        Analyze all clients and group by risk level.
        
        Returns:
            Dictionary mapping risk level -> predictions
        """
        self.predictions = []
        grouped = {level: [] for level in RiskLevel}
        
        for client in clients:
            prediction = self.predictor.predict(client)
            self.predictions.append(prediction)
            grouped[prediction.risk_level].append(prediction)
        
        return grouped
    
    def generate_report(self) -> str:
        """Generate text report of retention analysis"""
        if not self.predictions:
            return "No predictions to report."
        
        # Count by risk level
        risk_counts = {level: 0 for level in RiskLevel}
        for pred in self.predictions:
            risk_counts[pred.risk_level] += 1
        
        total = len(self.predictions)
        
        lines = [
            "=" * 60,
            "RETENTION RISK ANALYSIS REPORT",
            "=" * 60,
            f"\nTotal Clients Analyzed: {total}",
            "",
            "Risk Distribution:",
            f"  🔴 CRITICAL: {risk_counts[RiskLevel.CRITICAL]} ({risk_counts[RiskLevel.CRITICAL]/total:.1%})",
            f"  🟠 HIGH:     {risk_counts[RiskLevel.HIGH]} ({risk_counts[RiskLevel.HIGH]/total:.1%})",
            f"  🟡 MEDIUM:   {risk_counts[RiskLevel.MEDIUM]} ({risk_counts[RiskLevel.MEDIUM]/total:.1%})",
            f"  🟢 LOW:      {risk_counts[RiskLevel.LOW]} ({risk_counts[RiskLevel.LOW]/total:.1%})",
            "",
            "-" * 60,
            "TOP 10 AT-RISK CLIENTS",
            "-" * 60
        ]
        
        # Sort by risk score
        sorted_preds = sorted(self.predictions, key=lambda p: -p.risk_score)
        
        for i, pred in enumerate(sorted_preds[:10], 1):
            lines.append(f"\n{i}. Client {pred.client_id}")
            lines.append(f"   Risk: {pred.risk_level.value.upper()} ({pred.risk_score:.1f}/100)")
            lines.append(f"   Confidence: {pred.confidence:.0%}")
            lines.append(f"   Signals: {len(pred.signals)}")
            
            # Top signals
            if pred.signals:
                top_signal = max(pred.signals, key=lambda s: s.severity)
                lines.append(f"   Main Issue: {top_signal.description}")
            
            # Top recommendation
            if pred.recommended_actions:
                lines.append(f"   Action: {pred.recommended_actions[0]}")
        
        lines.append("\n" + "=" * 60)
        
        return "\n".join(lines)
    
    def get_action_queue(self) -> List[Tuple[ClientProfile, RetentionPrediction]]:
        """Get prioritized action queue (critical clients first)"""
        # Filter to actionable risk levels
        actionable = [
            p for p in self.predictions
            if p.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]
        ]
        
        # Sort by risk score
        return sorted(actionable, key=lambda p: -p.risk_score)


# ============================================================================
# TESTING & METRICS
# ============================================================================

def test_retention_predictor():
    """Test the retention predictor with sample data"""
    print("=" * 60)
    print("KRONOS RETENTION PREDICTOR - TEST SUITE")
    print("=" * 60)
    
    predictor = RetentionPredictor("tax")
    
    # Test client 1: Critical risk - non-return + price complaints
    print("\n[TEST 1] Critical Risk Client")
    print("-" * 60)
    
    critical_client = ClientProfile(
        client_id="C001",
        industry="tax",
        client_since=datetime.now() - timedelta(days=800),
        lifetime_value=3500,
        service_type="personal_tax",
        last_interaction=datetime.now() - timedelta(days=400),
        interaction_frequency=0.2,
        response_time_hours=120,
        messages_sent=2,
        messages_received=15,
        projects_completed=1,
        projects_cancelled=1,
        average_project_value=500,
        payment_history_score=0.6,
        complaint_count=2,
        positive_feedback_count=0,
        support_tickets=3,
        custom_fields={
            "years_not_returned": 2,
            "price_complaints": 2,
            "mentioned_competitor": True,
            "avg_document_delay_days": 45
        }
    )
    
    prediction = predictor.predict(critical_client)
    print(f"Client ID: {prediction.client_id}")
    print(f"Risk Level: {prediction.risk_level.value.upper()}")
    print(f"Risk Score: {prediction.risk_score}/100")
    print(f"Confidence: {prediction.confidence:.0%}")
    print(f"\nSignals Detected ({len(prediction.signals)}):")
    for signal in prediction.signals:
        print(f"  • [{signal.severity:.0%}] {signal.description}")
    print(f"\nRecommended Actions:")
    for action in prediction.recommended_actions:
        print(f"  → {action}")
    
    # Test client 2: Low risk - happy, engaged
    print("\n\n[TEST 2] Low Risk Client")
    print("-" * 60)
    
    good_client = ClientProfile(
        client_id="C002",
        industry="tax",
        client_since=datetime.now() - timedelta(days=1200),
        lifetime_value=12000,
        service_type="business_tax",
        last_interaction=datetime.now() - timedelta(days=5),
        interaction_frequency=3.0,
        response_time_hours=4,
        messages_sent=50,
        messages_received=45,
        projects_completed=8,
        projects_cancelled=0,
        average_project_value=1500,
        payment_history_score=1.0,
        complaint_count=0,
        positive_feedback_count=3,
        support_tickets=0,
        custom_fields={
            "years_not_returned": 0,
            "price_complaints": 0,
            "avg_document_delay_days": 5
        }
    )
    
    prediction = predictor.predict(good_client)
    print(f"Client ID: {prediction.client_id}")
    print(f"Risk Level: {prediction.risk_level.value.upper()}")
    print(f"Risk Score: {prediction.risk_score}/100")
    print(f"Confidence: {prediction.confidence:.0%}")
    print(f"\nSignals: {len(prediction.signals)} (minimal concerns)")
    print(f"\nRecommended Actions:")
    for action in prediction.recommended_actions:
        print(f"  → {action}")
    
    # Test client 3: Medium risk - slipping engagement
    print("\n\n[TEST 3] Medium Risk Client")
    print("-" * 60)
    
    medium_client = ClientProfile(
        client_id="C003",
        industry="tax",
        client_since=datetime.now() - timedelta(days=600),
        lifetime_value=5000,
        service_type="personal_tax",
        last_interaction=datetime.now() - timedelta(days=120),
        interaction_frequency=0.8,
        response_time_hours=48,
        messages_sent=8,
        messages_received=12,
        projects_completed=2,
        projects_cancelled=0,
        average_project_value=800,
        payment_history_score=0.9,
        complaint_count=0,
        positive_feedback_count=1,
        support_tickets=1,
        custom_fields={
            "years_not_returned": 1,
            "price_complaints": 0,
            "organizer_sent": True,
            "organizer_completed": False,
            "organizer_days_since_sent": 45
        }
    )
    
    prediction = predictor.predict(medium_client)
    print(f"Client ID: {prediction.client_id}")
    print(f"Risk Level: {prediction.risk_level.value.upper()}")
    print(f"Risk Score: {prediction.risk_score}/100")
    print(f"Confidence: {prediction.confidence:.0%}")
    print(f"\nSignals Detected ({len(prediction.signals)}):")
    for signal in prediction.signals:
        print(f"  • [{signal.severity:.0%}] {signal.description}")
    print(f"\nRecommended Actions:")
    for action in prediction.recommended_actions:
        print(f"  → {action}")
    
    # Test batch analysis
    print("\n\n[TEST 4] Batch Analysis")
    print("=" * 60)
    
    all_clients = [critical_client, good_client, medium_client]
    
    batch = BatchRetentionAnalysis(predictor)
    grouped = batch.analyze_client_base(all_clients)
    
    print(batch.generate_report())
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    test_retention_predictor()
