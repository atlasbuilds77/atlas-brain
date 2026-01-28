#!/usr/bin/env python3
"""
ATLAS CONFIDENCE CALIBRATION SYSTEM

Tracks predicted confidence vs actual outcomes to build realistic self-assessment.
The goal is intuition that KNOWS ITS LIMITS.

Key insight from research:
- Overconfident patterns should have reduced weight
- Underconfident patterns should have increased weight  
- Well-calibrated = predicted probability matches actual outcome rate

Usage:
  confidence-calibrator.py predict "description" --confidence 0.75 --domain trading
  confidence-calibrator.py resolve <prediction_id> --outcome success/failure
  confidence-calibrator.py calibration [--domain trading]
  confidence-calibrator.py analyze
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
import uuid

CLAWD_DIR = Path.home() / "clawd"
CALIBRATION_FILE = CLAWD_DIR / "memory" / "calibration" / "confidence-history.json"

def load_data():
    if not CALIBRATION_FILE.exists():
        return {
            "meta": {"version": "1.0.0"},
            "calibration_bins": {
                "0-20": {"predictions": 0, "correct": 0, "accuracy": None},
                "20-40": {"predictions": 0, "correct": 0, "accuracy": None},
                "40-60": {"predictions": 0, "correct": 0, "accuracy": None},
                "60-80": {"predictions": 0, "correct": 0, "accuracy": None},
                "80-100": {"predictions": 0, "correct": 0, "accuracy": None}
            },
            "overall_calibration": {},
            "predictions": [],
            "domain_calibration": {},
            "transfer_learning": {}
        }
    with open(CALIBRATION_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    CALIBRATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CALIBRATION_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_bin(confidence: float) -> str:
    """Get calibration bin for a confidence level."""
    pct = confidence * 100
    if pct < 20: return "0-20"
    if pct < 40: return "20-40"
    if pct < 60: return "40-60"
    if pct < 80: return "60-80"
    return "80-100"

def record_prediction(description: str, confidence: float, domain: str = "general"):
    """Record a new prediction with confidence level."""
    data = load_data()
    
    pred_id = f"pred-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4]}"
    
    prediction = {
        "id": pred_id,
        "description": description,
        "confidence": confidence,
        "domain": domain,
        "timestamp": datetime.now().isoformat(),
        "outcome": None,
        "resolved": False
    }
    
    data["predictions"].append(prediction)
    save_data(data)
    
    print(f"✅ Recorded prediction: {pred_id}")
    print(f"   Description: {description}")
    print(f"   Confidence: {confidence:.0%}")
    print(f"   Domain: {domain}")
    print(f"\n💡 Remember to resolve with: confidence-calibrator.py resolve {pred_id} --outcome success/failure")
    
    return pred_id

def resolve_prediction(pred_id: str, outcome: str):
    """Resolve a prediction and update calibration."""
    data = load_data()
    
    found = False
    for pred in data["predictions"]:
        if pred["id"] == pred_id:
            found = True
            pred["outcome"] = outcome
            pred["resolved"] = True
            pred["resolved_at"] = datetime.now().isoformat()
            
            # Update calibration bin
            confidence = pred["confidence"]
            bin_name = get_bin(confidence)
            is_correct = outcome in ["success", "win", "correct"]
            
            data["calibration_bins"][bin_name]["predictions"] += 1
            if is_correct:
                data["calibration_bins"][bin_name]["correct"] += 1
            
            # Update bin accuracy
            bin_data = data["calibration_bins"][bin_name]
            if bin_data["predictions"] > 0:
                bin_data["accuracy"] = bin_data["correct"] / bin_data["predictions"]
            
            # Update domain calibration
            domain = pred.get("domain", "general")
            if domain not in data["domain_calibration"]:
                data["domain_calibration"][domain] = {
                    "predictions": 0, "correct": 0, 
                    "total_confidence": 0, "accuracy": None
                }
            
            data["domain_calibration"][domain]["predictions"] += 1
            data["domain_calibration"][domain]["total_confidence"] += confidence
            if is_correct:
                data["domain_calibration"][domain]["correct"] += 1
            
            dom = data["domain_calibration"][domain]
            if dom["predictions"] > 0:
                dom["accuracy"] = dom["correct"] / dom["predictions"]
                dom["mean_confidence"] = dom["total_confidence"] / dom["predictions"]
            
            save_data(data)
            print(f"✅ Resolved {pred_id}: {outcome}")
            print(f"   Confidence was: {confidence:.0%}")
            print(f"   Outcome: {'Correct ✓' if is_correct else 'Incorrect ✗'}")
            
            # Show calibration feedback
            if is_correct and confidence < 0.5:
                print("   📈 You were underconfident! Consider trusting intuition more in similar cases.")
            elif not is_correct and confidence > 0.7:
                print("   📉 You were overconfident. Be more cautious with high-confidence predictions here.")
            
            break
    
    if not found:
        print(f"❌ Prediction {pred_id} not found")
    
    update_overall_calibration(data)
    save_data(data)

def update_overall_calibration(data):
    """Update overall calibration metrics."""
    resolved = [p for p in data["predictions"] if p.get("resolved")]
    
    if not resolved:
        return
    
    total = len(resolved)
    correct = sum(1 for p in resolved if p["outcome"] in ["success", "win", "correct"])
    
    total_conf = sum(p["confidence"] for p in resolved)
    mean_conf = total_conf / total
    mean_acc = correct / total
    
    # Calibration error: |mean_confidence - mean_accuracy|
    # Perfect calibration = 0
    calibration_error = abs(mean_conf - mean_acc)
    
    data["overall_calibration"] = {
        "total_predictions": total,
        "correct_predictions": correct,
        "mean_confidence": round(mean_conf, 3),
        "mean_accuracy": round(mean_acc, 3),
        "calibration_error": round(calibration_error, 3),
        "is_overconfident": mean_conf > mean_acc
    }

def show_calibration(domain: str = None):
    """Display calibration analysis."""
    data = load_data()
    
    print("=" * 60)
    print("📊 ATLAS CONFIDENCE CALIBRATION")
    print("=" * 60)
    
    overall = data.get("overall_calibration", {})
    
    if overall.get("total_predictions", 0) > 0:
        print(f"\n📈 OVERALL CALIBRATION")
        print(f"   Total predictions: {overall['total_predictions']}")
        print(f"   Mean confidence: {overall['mean_confidence']:.0%}")
        print(f"   Mean accuracy: {overall['mean_accuracy']:.0%}")
        print(f"   Calibration error: {overall['calibration_error']:.0%}")
        
        if overall.get("is_overconfident"):
            print("   ⚠️ OVERCONFIDENT: Reduce confidence in predictions")
        else:
            print("   📉 UNDERCONFIDENT: Can trust intuition more")
    else:
        print("\n⚠️ No resolved predictions yet. Make some predictions!")
    
    print(f"\n📊 CALIBRATION BY CONFIDENCE BIN")
    for bin_name, bin_data in data.get("calibration_bins", {}).items():
        if bin_data["predictions"] > 0:
            expected = int(bin_name.split("-")[0]) / 100 + 0.1  # midpoint
            actual = bin_data["accuracy"] or 0
            diff = actual - expected
            symbol = "✓" if abs(diff) < 0.15 else ("↑" if diff > 0 else "↓")
            print(f"   {bin_name}%: {bin_data['predictions']} predictions, {actual:.0%} accurate {symbol}")
    
    if domain:
        dom_data = data.get("domain_calibration", {}).get(domain)
        if dom_data:
            print(f"\n📂 DOMAIN: {domain.upper()}")
            print(f"   Predictions: {dom_data['predictions']}")
            print(f"   Accuracy: {dom_data['accuracy']:.0%}")
            print(f"   Mean confidence: {dom_data.get('mean_confidence', 0):.0%}")
    else:
        print(f"\n📂 DOMAIN CALIBRATION")
        for dom, dom_data in data.get("domain_calibration", {}).items():
            if dom_data["predictions"] > 0:
                over_under = ""
                if dom_data.get("mean_confidence") and dom_data.get("accuracy"):
                    diff = dom_data["mean_confidence"] - dom_data["accuracy"]
                    if diff > 0.1:
                        over_under = " (overconfident)"
                    elif diff < -0.1:
                        over_under = " (underconfident)"
                print(f"   {dom}: {dom_data['accuracy']:.0%} accurate ({dom_data['predictions']} pred){over_under}")
    
    # Show pending predictions
    pending = [p for p in data.get("predictions", []) if not p.get("resolved")]
    if pending:
        print(f"\n⏳ PENDING PREDICTIONS ({len(pending)})")
        for p in pending[-5:]:  # Last 5
            print(f"   [{p['id']}] {p['description'][:50]}... ({p['confidence']:.0%})")
    
    print("\n" + "=" * 60)

def analyze_patterns():
    """Deep analysis of calibration patterns."""
    data = load_data()
    resolved = [p for p in data["predictions"] if p.get("resolved")]
    
    print("=" * 60)
    print("🔬 CALIBRATION PATTERN ANALYSIS")
    print("=" * 60)
    
    if len(resolved) < 5:
        print("\n⚠️ Need at least 5 resolved predictions for analysis.")
        return
    
    # Find overconfident and underconfident patterns
    overconfident = [p for p in resolved 
                     if p["confidence"] > 0.7 and p["outcome"] not in ["success", "win", "correct"]]
    underconfident = [p for p in resolved 
                      if p["confidence"] < 0.4 and p["outcome"] in ["success", "win", "correct"]]
    
    print(f"\n📈 HIGH CONFIDENCE FAILURES ({len(overconfident)})")
    for p in overconfident[-3:]:
        print(f"   • {p['description'][:60]}...")
        print(f"     Confidence: {p['confidence']:.0%}, Domain: {p.get('domain', 'general')}")
    
    print(f"\n📉 LOW CONFIDENCE SUCCESSES ({len(underconfident)})")
    for p in underconfident[-3:]:
        print(f"   • {p['description'][:60]}...")
        print(f"     Confidence: {p['confidence']:.0%}, Domain: {p.get('domain', 'general')}")
    
    # Domain-specific insights
    print("\n🎯 DOMAIN INSIGHTS")
    for domain, dom_data in data.get("domain_calibration", {}).items():
        if dom_data["predictions"] >= 3:
            mean_conf = dom_data.get("mean_confidence", 0)
            accuracy = dom_data.get("accuracy", 0)
            
            if accuracy > mean_conf + 0.15:
                print(f"   {domain}: UNDERCONFIDENT (+{(accuracy-mean_conf)*100:.0f}% room to trust more)")
            elif accuracy < mean_conf - 0.15:
                print(f"   {domain}: OVERCONFIDENT ({(mean_conf-accuracy)*100:.0f}% too aggressive)")
            else:
                print(f"   {domain}: WELL CALIBRATED ✓")
    
    print("\n" + "=" * 60)

def main():
    parser = argparse.ArgumentParser(description="ATLAS Confidence Calibration")
    subparsers = parser.add_subparsers(dest="command")
    
    # Predict command
    pred_parser = subparsers.add_parser("predict", help="Record a prediction")
    pred_parser.add_argument("description", help="What you're predicting")
    pred_parser.add_argument("--confidence", "-c", type=float, required=True, 
                            help="Confidence level 0.0-1.0")
    pred_parser.add_argument("--domain", "-d", default="general", help="Domain")
    
    # Resolve command
    resolve_parser = subparsers.add_parser("resolve", help="Resolve a prediction")
    resolve_parser.add_argument("pred_id", help="Prediction ID")
    resolve_parser.add_argument("--outcome", "-o", required=True, 
                               help="success/failure/win/loss")
    
    # Calibration command
    cal_parser = subparsers.add_parser("calibration", help="Show calibration stats")
    cal_parser.add_argument("--domain", "-d", help="Filter by domain")
    
    # Analyze command
    subparsers.add_parser("analyze", help="Deep pattern analysis")
    
    args = parser.parse_args()
    
    if args.command == "predict":
        record_prediction(args.description, args.confidence, args.domain)
    elif args.command == "resolve":
        resolve_prediction(args.pred_id, args.outcome)
    elif args.command == "calibration":
        show_calibration(args.domain)
    elif args.command == "analyze":
        analyze_patterns()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
