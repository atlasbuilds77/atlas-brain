#!/usr/bin/env python3
"""
Brain Logger - Python utility for logging cognitive events
to the Atlas brain visualization system.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any


class BrainLogger:
    """Logger for Atlas cognitive events."""
    
    def __init__(self, log_path: str = "logs/brain-events.jsonl"):
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        
    def log(
        self,
        event_type: str,
        message: str,
        intensity: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log a cognitive event.
        
        Args:
            event_type: Type of event (pattern_match, emotion, etc.)
            message: Human-readable description
            intensity: Activity intensity 0.0-1.0
            metadata: Additional structured data
        """
        event = {
            "timestamp": datetime.now().astimezone().isoformat(),
            "event_type": event_type,
            "message": message,
            "intensity": max(0.0, min(1.0, intensity)),
            "metadata": metadata or {}
        }
        
        with open(self.log_path, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def pattern_match(self, pattern_name: str, valence: str, confidence: float, **kwargs):
        """Log a pattern recognition event."""
        self.log(
            "pattern_match",
            f"Pattern '{pattern_name}' matched - {valence.upper()}",
            confidence,
            {"pattern_name": pattern_name, "valence": valence, "confidence": confidence, **kwargs}
        )
    
    def emotion(self, emotion_name: str, intensity: float, **kwargs):
        """Log an emotional processing event."""
        self.log(
            "emotion",
            f"Somatic marker: {emotion_name}",
            intensity,
            {"emotion": emotion_name, "intensity": intensity, **kwargs}
        )
    
    def metacognition(self, check_type: str, intensity: float = 0.8, **kwargs):
        """Log a metacognitive event."""
        self.log(
            "metacognition",
            f"Metacognitive check: {check_type}",
            intensity,
            {"check_type": check_type, **kwargs}
        )
    
    def memory_retrieval(self, memory_type: str, content: str, intensity: float = 0.5, **kwargs):
        """Log a memory retrieval event."""
        self.log(
            "memory",
            f"Retrieved {memory_type}: {content}",
            intensity,
            {"memory_type": memory_type, "content": content, **kwargs}
        )
    
    def bias_detection(self, bias_type: str, context: str, intensity: float = 0.6, **kwargs):
        """Log a bias detection event."""
        self.log(
            "bias_detection",
            f"Bias detected: {bias_type}",
            intensity,
            {"bias_type": bias_type, "context": context, **kwargs}
        )
    
    def mode_switch(self, old_mode: str, new_mode: str, reason: str = "", **kwargs):
        """Log a cognitive mode switch."""
        message = f"{new_mode} MODE"
        if reason:
            message += f": {reason}"
        
        self.log(
            "mode_switch",
            message,
            1.0,
            {"old_mode": old_mode, "new_mode": new_mode, "reason": reason, **kwargs}
        )
    
    def decision(self, decision: str, confidence: float, **kwargs):
        """Log a decision event."""
        self.log(
            "decision",
            f"Decision: {decision}",
            confidence,
            {"decision": decision, "confidence": confidence, **kwargs}
        )


# Global instance for easy access
brain = BrainLogger()


def log_brain_event(event_type: str, message: str, intensity: float = 0.5, metadata: dict = None):
    """Convenience function for logging events."""
    brain.log(event_type, message, intensity, metadata)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            print("Generating test events...")
            
            brain.pattern_match("FOMO_trade", "negative", 0.85, context="trading")
            brain.emotion("anxiety", 0.7, trigger="market_volatility")
            brain.metacognition("verifying_sources", 0.8, source_count=3)
            brain.memory_retrieval("episodic", "successful trade 2024-12-15", 0.6)
            brain.bias_detection("confirmation_bias", "trade_decision", 0.65)
            brain.mode_switch("ECN", "DMN", "creative_exploration")
            brain.decision("Execute protective stop-loss", 0.9, risk_level="high")
            
            print("✓ Test events logged to logs/brain-events.jsonl")
        else:
            print("Usage: python3 scripts/brain-logger.py test")
    else:
        print("BrainLogger - Cognitive event logger for Atlas")
        print("Import in your scripts: from brain_logger import brain")
        print("")
        print("Example:")
        print("  brain.pattern_match('FOMO', 'negative', 0.8)")
        print("  brain.emotion('excitement', 0.7)")
        print("  brain.mode_switch('ECN', 'DMN', 'rest period')")
