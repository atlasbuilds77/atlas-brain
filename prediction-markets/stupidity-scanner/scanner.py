#!/usr/bin/env python3
"""
Stupidity Scanner - Find Mispriced Prediction Markets

Based on Semi's "$286 to $1M" strategy of fading folk wisdom.

Key patterns to detect:
1. Multi-candidate markets where top picks sum to > 80% (overconfidence)
2. High conviction on unpredictable events (papal elections, etc)
3. Emotional/tribal betting patterns (post-election MAGA money, etc)
4. "Impossible in timeframe" promises (tax bills in 100 days, etc)
5. Longshot bias (underdogs overpriced, favorites underpriced)

Usage:
    python scanner.py --analyze-kalshi
    python scanner.py --analyze-polymarket
    python scanner.py --check-market <market_url>
"""

import argparse
import json
from datetime import datetime
from typing import List, Dict, Any

# Patterns that indicate potential stupidity
STUPIDITY_PATTERNS = {
    "overconfident_favorites": {
        "description": "Top 3 candidates sum to >75% in multi-candidate race",
        "threshold": 0.75,
        "action": "Consider NO on all favorites"
    },
    "impossible_timeline": {
        "description": "Policy promises with unrealistic deadlines",
        "keywords": ["100 days", "first week", "immediately", "day one"],
        "action": "Fade the YES side"
    },
    "tribal_money": {
        "description": "Politically charged markets with one-sided betting",
        "indicators": ["volume spike after election", "social media hype"],
        "action": "Fade the emotional side"
    },
    "celebrity_prediction": {
        "description": "Markets on unpredictable celebrity/elite behavior",
        "keywords": ["pope", "royal", "billionaire", "celebrity"],
        "action": "Fade high-conviction picks"
    },
    "sports_narrative": {
        "description": "Team handicapped by narrative (too young, can't win big)",
        "keywords": ["experience", "clutch", "pressure", "young team"],
        "action": "Check stats vs narrative, bet stats"
    }
}

class StupidityScanner:
    def __init__(self):
        self.opportunities = []
    
    def analyze_multi_candidate_market(self, candidates: List[Dict]) -> Dict[str, Any]:
        """
        Analyze a multi-candidate market for overconfidence.
        
        Semi's Pope trade: Top 3 at 75% but 150 cardinals could win.
        """
        if not candidates:
            return {"stupidity_score": 0, "recommendation": None}
        
        # Sort by probability
        sorted_candidates = sorted(candidates, key=lambda x: x.get('probability', 0), reverse=True)
        
        # Sum of top 3
        top_3_sum = sum(c.get('probability', 0) for c in sorted_candidates[:3])
        total_candidates = len(candidates)
        
        stupidity_score = 0
        recommendations = []
        
        # Check for overconfidence
        if top_3_sum > 0.75 and total_candidates > 10:
            stupidity_score = (top_3_sum - 0.75) * 100  # Higher = more overconfident
            recommendations.append({
                "pattern": "overconfident_favorites",
                "finding": f"Top 3 candidates at {top_3_sum*100:.1f}% but {total_candidates} candidates exist",
                "action": "Buy NO on all top candidates",
                "confidence": min(stupidity_score / 25, 1.0)  # Max confidence at 25% overconfidence
            })
        
        return {
            "stupidity_score": stupidity_score,
            "top_3_sum": top_3_sum,
            "total_candidates": total_candidates,
            "recommendations": recommendations
        }
    
    def analyze_timeline_feasibility(self, market_title: str, deadline_days: int) -> Dict[str, Any]:
        """
        Check if a policy/event promise is feasible in the given timeline.
        
        Semi's trade: "Tax on tips in 100 days" when Congress was in recess.
        """
        impossible_patterns = [
            {"keyword": "tax", "min_days": 180, "reason": "Complex tax bills take 6-8 months minimum"},
            {"keyword": "legislation", "min_days": 120, "reason": "Congressional process takes months"},
            {"keyword": "amendment", "min_days": 365, "reason": "Constitutional amendments take years"},
            {"keyword": "treaty", "min_days": 180, "reason": "Treaties require Senate ratification"},
        ]
        
        title_lower = market_title.lower()
        stupidity_score = 0
        recommendations = []
        
        for pattern in impossible_patterns:
            if pattern["keyword"] in title_lower and deadline_days < pattern["min_days"]:
                stupidity_score = (pattern["min_days"] - deadline_days) / pattern["min_days"] * 100
                recommendations.append({
                    "pattern": "impossible_timeline",
                    "finding": f"'{pattern['keyword']}' unlikely in {deadline_days} days",
                    "reason": pattern["reason"],
                    "action": "Fade YES, this is likely impossible",
                    "confidence": min(stupidity_score / 50, 1.0)
                })
        
        return {
            "stupidity_score": stupidity_score,
            "recommendations": recommendations
        }
    
    def analyze_longshot_bias(self, yes_price: float, category: str) -> Dict[str, Any]:
        """
        Check for longshot bias - underdogs are typically overpriced.
        
        Research shows: Betting favorites = -3.64% loss, betting underdogs = -26% loss
        Favorites are UNDERPRICED.
        """
        stupidity_score = 0
        recommendations = []
        
        # Heavy underdog (YES < 20%) - likely overpriced
        if yes_price < 0.20:
            stupidity_score = (0.20 - yes_price) * 200  # More underdog = more overpriced
            recommendations.append({
                "pattern": "longshot_bias",
                "finding": f"Heavy underdog at {yes_price*100:.1f}% - likely overpriced",
                "action": "Consider NO position (fade the longshot)",
                "confidence": min(stupidity_score / 30, 1.0)
            })
        
        # Heavy favorite (YES > 80%) - likely underpriced, good value
        elif yes_price > 0.80:
            recommendations.append({
                "pattern": "longshot_bias",
                "finding": f"Heavy favorite at {yes_price*100:.1f}% - likely underpriced",
                "action": "Consider YES position (bet the favorite)",
                "confidence": 0.6  # Lower confidence on favorites
            })
        
        return {
            "stupidity_score": stupidity_score,
            "recommendations": recommendations
        }
    
    def generate_report(self, analyses: List[Dict]) -> str:
        """Generate a readable report of all findings."""
        report = []
        report.append("=" * 60)
        report.append("STUPIDITY SCANNER REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 60)
        
        total_opportunities = 0
        
        for analysis in analyses:
            if analysis.get('recommendations'):
                for rec in analysis['recommendations']:
                    total_opportunities += 1
                    report.append(f"\n🎯 OPPORTUNITY #{total_opportunities}")
                    report.append(f"   Pattern: {rec['pattern']}")
                    report.append(f"   Finding: {rec['finding']}")
                    report.append(f"   Action: {rec['action']}")
                    report.append(f"   Confidence: {rec['confidence']*100:.0f}%")
        
        if total_opportunities == 0:
            report.append("\nNo obvious stupidity detected. Markets may be efficient.")
        else:
            report.append(f"\n{'=' * 60}")
            report.append(f"TOTAL OPPORTUNITIES: {total_opportunities}")
        
        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(description="Scan prediction markets for stupidity")
    parser.add_argument('--demo', action='store_true', help="Run demo analysis")
    args = parser.parse_args()
    
    scanner = StupidityScanner()
    
    if args.demo:
        print("Running demo analysis...")
        
        # Demo: Pope election (Semi's actual trade)
        pope_candidates = [
            {"name": "Cardinal A", "probability": 0.35},
            {"name": "Cardinal B", "probability": 0.25},
            {"name": "Cardinal C", "probability": 0.15},
            # ... 147 more cardinals
        ] + [{"name": f"Cardinal {i}", "probability": 0.002} for i in range(4, 151)]
        
        analyses = []
        
        # Analyze multi-candidate market
        result = scanner.analyze_multi_candidate_market(pope_candidates)
        result['market'] = "Next Pope Election"
        analyses.append(result)
        
        # Analyze impossible timeline
        result = scanner.analyze_timeline_feasibility("Will tax on tips be eliminated in first 100 days?", 100)
        result['market'] = "Tax on Tips - 100 Days"
        analyses.append(result)
        
        # Analyze longshot bias
        result = scanner.analyze_longshot_bias(0.08, "sports")
        result['market'] = "Underdog Team to Win Championship"
        analyses.append(result)
        
        print(scanner.generate_report(analyses))
    else:
        print("Usage: python scanner.py --demo")
        print("       (Full Kalshi/Polymarket integration coming soon)")


if __name__ == "__main__":
    main()
