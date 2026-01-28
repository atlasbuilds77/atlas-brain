#!/usr/bin/env python3
"""
Position Monitor with Visual Analysis
Monitors open positions and provides ICT-based exit signals
"""

import json
import time
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import argparse
import subprocess

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {
    "check_interval_seconds": 60,  # How often to analyze
    "timeframes": ["1m", "5m"],    # Timeframes to capture
    "confidence_notify": 6,        # Notify at this confidence
    "confidence_recommend": 8,     # Strong recommendation at this confidence
    "telegram_notify": True,       # Send Telegram alerts
    "log_file": Path(__file__).parent / "monitor_log.json",
}

# ============================================================
# POSITION STATE
# ============================================================

class PositionState:
    """Track current position state"""
    
    def __init__(self, symbol: str, side: str, entry_price: float):
        self.symbol = symbol
        self.side = side  # LONG or SHORT
        self.entry_price = entry_price
        self.entry_time = datetime.now()
        self.last_check = None
        self.signals = []
        self.current_price = None
        self.pnl_percent = 0.0
        
    def update_price(self, price: float):
        self.current_price = price
        if self.side == "LONG":
            self.pnl_percent = (price - self.entry_price) / self.entry_price * 100
        else:
            self.pnl_percent = (self.entry_price - price) / self.entry_price * 100
    
    def add_signal(self, signal: Dict[str, Any]):
        signal["timestamp"] = datetime.now().isoformat()
        self.signals.append(signal)
        
    def get_state(self) -> Dict[str, Any]:
        return {
            "symbol": self.symbol,
            "side": self.side,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time.isoformat(),
            "current_price": self.current_price,
            "pnl_percent": f"{self.pnl_percent:+.2f}%",
            "time_in_position": str(datetime.now() - self.entry_time).split('.')[0],
            "signal_count": len(self.signals),
            "last_signal": self.signals[-1] if self.signals else None
        }

# ============================================================
# TELEGRAM NOTIFICATION
# ============================================================

def notify_telegram(message: str, priority: str = "normal"):
    """Send notification via Telegram using Clawdbot"""
    
    emoji = {
        "normal": "📊",
        "warning": "⚠️",
        "critical": "🚨",
        "success": "✅"
    }
    
    full_message = f"{emoji.get(priority, '📊')} {message}"
    
    try:
        # Use Clawdbot message tool
        subprocess.run([
            "clawdbot", "message", "send",
            "--message", full_message
        ], capture_output=True, timeout=10)
        print(f"📤 Telegram: {message[:50]}...")
    except Exception as e:
        print(f"❌ Telegram notification failed: {e}")

# ============================================================
# VISUAL ANALYSIS INTEGRATION
# ============================================================

def capture_and_analyze(position: PositionState) -> Dict[str, Any]:
    """
    Capture chart and run ICT analysis
    Returns analysis results
    """
    from visual_analyzer import capture_chart, analyze_chart_image, get_timeframe_prompt
    from ict_patterns import EXIT_CHECK_PROMPT
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "position": position.get_state(),
        "analyses": []
    }
    
    for tf in CONFIG["timeframes"]:
        print(f"\n📸 Capturing {position.symbol} {tf}...")
        
        chart_path = capture_chart(position.symbol, tf)
        if not chart_path:
            continue
            
        # Build position-aware prompt
        prompt = EXIT_CHECK_PROMPT.format(
            position_type=position.side,
            entry_zone=f"${position.entry_price:,.2f}"
        )
        
        prompt += f"""

ADDITIONAL CONTEXT:
- Current PnL: {position.pnl_percent:+.2f}%
- Time in position: {datetime.now() - position.entry_time}
- Looking at: {tf} timeframe

Based on ICT/SMC analysis, should this position be managed?
"""
        
        analysis = analyze_chart_image(chart_path, prompt)
        results["analyses"].append({
            "timeframe": tf,
            "chart_path": str(chart_path),
            "analysis": analysis
        })
    
    return results

# ============================================================
# SIGNAL INTERPRETATION (mock for integration)
# ============================================================

def interpret_visual_signal(analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Interpret the vision model's response to extract actionable signals
    
    In production, this parses the JSON response from the vision model.
    For now, it documents the expected format.
    """
    
    # Expected response structure from vision model:
    expected_format = {
        "exit_signal": "NONE | SCALE_OUT | FULL_EXIT | REVERSAL_IMMINENT",
        "confidence": 1-10,
        "bias": "BULLISH | BEARISH | NEUTRAL",
        "key_observations": ["list", "of", "observations"],
        "reasoning": "why this signal was generated"
    }
    
    # For now, return instruction to process
    return {
        "status": "awaiting_vision_response",
        "instructions": """
To interpret the visual analysis:
1. Run the image tool with the captured chart
2. Parse the JSON response for 'exit_signal' field
3. If confidence >= 6, notify via Telegram
4. If confidence >= 8, recommend action
5. Log all signals for pattern review
""",
        "expected_format": expected_format
    }

# ============================================================
# MONITORING LOOP
# ============================================================

async def monitor_position(position: PositionState):
    """
    Main monitoring loop - captures and analyzes at intervals
    """
    print("\n" + "=" * 60)
    print("POSITION MONITOR - VISUAL ANALYSIS ACTIVE")
    print("=" * 60)
    print(json.dumps(position.get_state(), indent=2))
    print("=" * 60)
    
    if CONFIG["telegram_notify"]:
        notify_telegram(
            f"Started monitoring {position.symbol} {position.side} @ ${position.entry_price:,.2f}",
            "normal"
        )
    
    check_count = 0
    
    while True:
        try:
            check_count += 1
            print(f"\n🔄 Check #{check_count} at {datetime.now().strftime('%H:%M:%S')}")
            
            # Capture and analyze
            results = capture_and_analyze(position)
            
            # Interpret signals
            signal = interpret_visual_signal(results)
            position.add_signal(signal)
            
            # Log results
            log_entry = {
                "check_number": check_count,
                "timestamp": datetime.now().isoformat(),
                "position": position.get_state(),
                "results": results,
                "signal": signal
            }
            
            with open(CONFIG["log_file"], "a") as f:
                f.write(json.dumps(log_entry, default=str) + "\n")
            
            print(f"   Position: {position.side} | PnL: {position.pnl_percent:+.2f}%")
            print(f"   Signal Status: {signal.get('status', 'unknown')}")
            
            # Wait for next check
            print(f"\n⏳ Next check in {CONFIG['check_interval_seconds']}s...")
            await asyncio.sleep(CONFIG["check_interval_seconds"])
            
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in monitoring loop: {e}")
            await asyncio.sleep(10)  # Brief pause on error

# ============================================================
# DEMO MODE
# ============================================================

def run_demo():
    """
    Demo mode - shows how the system works with mock data
    """
    print("\n" + "=" * 60)
    print("VISUAL TRADING SYSTEM - DEMO MODE")
    print("=" * 60)
    
    # Simulate the ETH trade from context
    demo_position = {
        "symbol": "ETH-PERP",
        "side": "LONG", 
        "entry_price": 2911.00,
        "current_price": 2952.00,
        "pnl_percent": 1.41
    }
    
    print(f"""
SCENARIO: ETH Long Position

Entry: ${demo_position['entry_price']:,.2f}
High:  $2,952 (where exit should have occurred)
PnL:   +{demo_position['pnl_percent']:.2f}%

WHAT DATA SHOWED:
- Price up 1.41%
- Still in profit
- No obvious data-driven exit signal

WHAT VISUAL ANALYSIS WOULD SHOW:
- Candles getting smaller (momentum dying)
- Long upper wicks forming (rejection)
- Approaching equal highs (liquidity pool)
- Volume decreasing on push higher
- FVG from earlier move now filled

VISUAL SIGNAL: SCALE_OUT → FULL_EXIT
CONFIDENCE: 8/10

This is why Atlas needs "eyes" - patterns are visible
that pure data misses.
""")
    
    print("=" * 60)
    print("SYSTEM COMPONENTS:")
    print("=" * 60)
    print("""
1. ict_patterns.py      - ICT concept prompts for vision models
2. visual_analyzer.py   - Chart capture and analysis
3. position_monitor.py  - Real-time position monitoring (this file)

USAGE:
  # One-shot analysis
  python3 visual_analyzer.py --symbol ETH-PERP --analyze-now
  
  # Monitor open position
  python3 position_monitor.py --symbol ETH-PERP --side LONG --entry 2911
  
  # Multi-timeframe analysis  
  python3 visual_analyzer.py --symbol ETH-PERP --mtf

INTEGRATION:
  The system integrates with Clawdbot's browser and image tools.
  When monitoring, it captures TradingView charts and uses vision
  models to identify ICT patterns for exit signals.
""")

# ============================================================
# MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Position Monitor with Visual Analysis")
    parser.add_argument("--symbol", "-s", default="ETH-PERP", help="Trading symbol")
    parser.add_argument("--side", default="LONG", choices=["LONG", "SHORT"], help="Position side")
    parser.add_argument("--entry", "-e", type=float, required=False, help="Entry price")
    parser.add_argument("--interval", "-i", type=int, default=60, help="Check interval in seconds")
    parser.add_argument("--demo", action="store_true", help="Run demo mode")
    parser.add_argument("--no-notify", action="store_true", help="Disable Telegram notifications")
    
    args = parser.parse_args()
    
    if args.demo:
        run_demo()
        return
    
    if not args.entry:
        print("❌ Entry price required. Use --entry <price>")
        print("   Or run --demo for demonstration")
        return
    
    # Update config
    CONFIG["check_interval_seconds"] = args.interval
    CONFIG["telegram_notify"] = not args.no_notify
    
    # Create position
    position = PositionState(
        symbol=args.symbol,
        side=args.side,
        entry_price=args.entry
    )
    
    # Run monitoring loop
    asyncio.run(monitor_position(position))

if __name__ == "__main__":
    main()
