#!/usr/bin/env python3
"""
ATLAS Chart Generator - Visualizations for trading and learning
Supports: P&L charts, pattern strength, learning curves
Output: PNG images or ASCII art
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Output directory
CHART_DIR = Path("/Users/atlasbuilds/clawd/memory/.charts")
CHART_DIR.mkdir(parents=True, exist_ok=True)

def ascii_bar_chart(data: dict, title: str = "", max_width: int = 50) -> str:
    """Generate ASCII bar chart from dict of label -> value"""
    if not data:
        return "No data to chart"
    
    lines = []
    if title:
        lines.append(f"{'═' * (max_width + 20)}")
        lines.append(f"  {title}")
        lines.append(f"{'═' * (max_width + 20)}")
    
    max_val = max(abs(v) for v in data.values()) if data.values() else 1
    max_label_len = max(len(str(k)) for k in data.keys()) if data.keys() else 0
    
    for label, value in data.items():
        bar_len = int(abs(value) / max_val * max_width) if max_val > 0 else 0
        bar_char = "█" if value >= 0 else "░"
        sign = "+" if value > 0 else "" if value == 0 else ""
        bar = bar_char * bar_len
        lines.append(f"  {label:<{max_label_len}} │ {bar} {sign}{value:.2f}")
    
    lines.append(f"{'─' * (max_width + 20)}")
    return "\n".join(lines)

def ascii_line_chart(values: list, title: str = "", height: int = 10, width: int = 60) -> str:
    """Generate ASCII line chart from list of values"""
    if not values or len(values) < 2:
        return "Need at least 2 data points"
    
    min_val = min(values)
    max_val = max(values)
    range_val = max_val - min_val if max_val != min_val else 1
    
    lines = []
    if title:
        lines.append(f"{'═' * (width + 10)}")
        lines.append(f"  {title}")
        lines.append(f"{'═' * (width + 10)}")
    
    # Scale values to chart height
    scaled = [(v - min_val) / range_val * (height - 1) for v in values]
    
    # Resample to fit width
    step = len(values) / width
    resampled = []
    for i in range(width):
        idx = min(int(i * step), len(scaled) - 1)
        resampled.append(scaled[idx])
    
    # Generate chart grid
    for row in range(height - 1, -1, -1):
        line = f"  {max_val - (max_val - min_val) * (height - 1 - row) / (height - 1):>8.1f} │"
        for col in range(width):
            if resampled[col] >= row - 0.5 and resampled[col] < row + 0.5:
                line += "●"
            elif resampled[col] > row:
                line += "│"
            else:
                line += " "
        lines.append(line)
    
    lines.append(f"  {'':>8} └{'─' * width}")
    lines.append(f"  {'':>8}  Start{' ' * (width - 10)}End")
    
    return "\n".join(lines)

def pattern_strength_chart(patterns: dict) -> str:
    """Visualize pattern strengths from neuroplasticity system"""
    if not patterns:
        return "No patterns to visualize"
    
    return ascii_bar_chart(patterns, "Pattern Strength Weights")

def pnl_history_chart(trades: list) -> str:
    """Visualize cumulative P&L from trade history"""
    if not trades:
        return "No trades to chart"
    
    cumulative = []
    running_total = 0
    for trade in trades:
        pnl = trade.get('pnl', 0)
        running_total += pnl
        cumulative.append(running_total)
    
    return ascii_line_chart(cumulative, f"Cumulative P&L ({len(trades)} trades)")

def learning_curve_chart(outcomes: list) -> str:
    """Visualize learning over time (rolling win rate)"""
    if len(outcomes) < 5:
        return "Need at least 5 outcomes for learning curve"
    
    window = min(10, len(outcomes) // 3)
    rolling_wr = []
    
    for i in range(window, len(outcomes) + 1):
        wins = sum(1 for o in outcomes[i-window:i] if o > 0)
        rolling_wr.append(wins / window * 100)
    
    return ascii_line_chart(rolling_wr, f"Rolling Win Rate (window={window})")

def save_chart(content: str, name: str) -> str:
    """Save chart to file and return path"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = CHART_DIR / f"{name}_{timestamp}.txt"
    filepath.write_text(content)
    return str(filepath)

# Example/Demo functions
def demo_charts():
    """Generate demo charts to show capabilities"""
    
    # Demo pattern strengths
    patterns = {
        "morning_reversal": 0.85,
        "breakout_false": -0.65,
        "trend_continuation": 0.72,
        "news_overreaction": 0.55,
        "fomo_entry": -0.90,
    }
    print(pattern_strength_chart(patterns))
    print()
    
    # Demo P&L
    trades = [
        {"pnl": 50}, {"pnl": -30}, {"pnl": 100}, {"pnl": -20},
        {"pnl": 75}, {"pnl": -45}, {"pnl": 60}, {"pnl": 120},
        {"pnl": -50}, {"pnl": 80},
    ]
    print(pnl_history_chart(trades))
    print()
    
    # Demo learning curve
    outcomes = [1, -1, 1, -1, -1, 1, 1, -1, 1, 1, 1, -1, 1, 1, 1, 1, -1, 1, 1, 1]
    print(learning_curve_chart(outcomes))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        demo_charts()
    else:
        print("ATLAS Chart Generator")
        print("Usage: atlas-chart.py demo")
        print("       Import and use functions in other scripts")
        print()
        print("Functions:")
        print("  ascii_bar_chart(data, title)")
        print("  ascii_line_chart(values, title)")
        print("  pattern_strength_chart(patterns)")
        print("  pnl_history_chart(trades)")
        print("  learning_curve_chart(outcomes)")
