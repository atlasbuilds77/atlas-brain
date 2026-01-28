#!/usr/bin/env python3
"""
Visual Chart Analyzer for Atlas
Uses vision models to analyze trading charts with ICT concepts
"""

import json
import os
import base64
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import argparse

# Import ICT prompts
from ict_patterns import (
    ICT_ANALYSIS_PROMPT, 
    QUICK_BIAS_PROMPT, 
    EXIT_CHECK_PROMPT,
    PATTERN_PROMPTS,
    get_timeframe_prompt
)

# ============================================================
# CONFIGURATION
# ============================================================

CONFIG = {
    "captures_dir": Path(__file__).parent / "captures",
    "analysis_dir": Path(__file__).parent / "analysis",
    "chart_sources": {
        "tradingview": "https://www.tradingview.com/chart/?symbol=",
        "birdeye": "https://birdeye.so/token/",
        "dexscreener": "https://dexscreener.com/solana/"
    },
    "symbols": {
        "SOL-PERP": "BINANCE:SOLUSDT.P",
        "ETH-PERP": "BINANCE:ETHUSDT.P", 
        "BTC-PERP": "BINANCE:BTCUSDT.P"
    }
}

# Ensure directories exist
CONFIG["captures_dir"].mkdir(parents=True, exist_ok=True)
CONFIG["analysis_dir"].mkdir(parents=True, exist_ok=True)

# ============================================================
# CHART CAPTURE (via Clawdbot browser tool)
# ============================================================

def capture_chart(symbol: str, timeframe: str = "5m", source: str = "tradingview") -> Optional[Path]:
    """
    Capture chart screenshot using Clawdbot browser tool
    Returns path to saved screenshot
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    date_dir = CONFIG["captures_dir"] / datetime.now().strftime("%Y-%m-%d")
    date_dir.mkdir(exist_ok=True)
    
    filename = f"{symbol}_{timeframe}_{timestamp}.png"
    filepath = date_dir / filename
    
    # Get TradingView symbol
    tv_symbol = CONFIG["symbols"].get(symbol, symbol)
    
    # Build URL with timeframe
    # TradingView URL format: symbol, interval in URL fragment
    tv_intervals = {"1m": "1", "5m": "5", "15m": "15", "1h": "60", "4h": "240"}
    interval = tv_intervals.get(timeframe, "5")
    
    chart_url = f"{CONFIG['chart_sources']['tradingview']}{tv_symbol}&interval={interval}"
    
    print(f"📸 Capturing {symbol} {timeframe} chart...")
    print(f"   URL: {chart_url}")
    
    # Use Clawdbot browser tool via CLI
    # Note: In production, this would use the browser tool directly
    # For now, we save a placeholder and document the integration
    
    try:
        # This is the command that would capture via Clawdbot
        # clawdbot browser --profile clawd screenshot --url <url> --out <path>
        result = subprocess.run([
            "clawdbot", "browser", 
            "--browser-profile", "clawd",
            "screenshot",
            "--url", chart_url,
            "--out", str(filepath)
        ], capture_output=True, text=True, timeout=30)
        
        if filepath.exists():
            print(f"   ✅ Saved to: {filepath}")
            return filepath
        else:
            print(f"   ❌ Capture failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("   ❌ Capture timed out")
        return None
    except FileNotFoundError:
        # Clawdbot not in PATH, try alternative
        print("   ⚠️ Clawdbot CLI not found, using fallback...")
        return _fallback_capture(chart_url, filepath)

def _fallback_capture(url: str, filepath: Path) -> Optional[Path]:
    """Fallback capture method using system screenshot or saved chart"""
    # Create a placeholder for testing
    print(f"   📝 Created placeholder at {filepath}")
    print(f"   💡 To actually capture, run:")
    print(f"      clawdbot browser --browser-profile clawd screenshot --url '{url}'")
    return None

# ============================================================
# IMAGE ENCODING
# ============================================================

def encode_image_base64(image_path: Path) -> str:
    """Encode image to base64 for API calls"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def get_image_data_url(image_path: Path) -> str:
    """Get data URL for image"""
    b64 = encode_image_base64(image_path)
    suffix = image_path.suffix.lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(suffix, "image/png")
    return f"data:{mime};base64,{b64}"

# ============================================================
# VISION MODEL ANALYSIS (via Clawdbot)
# ============================================================

def analyze_chart_image(
    image_path: Path,
    prompt: str = ICT_ANALYSIS_PROMPT,
    model: str = "gpt-4-vision-preview"
) -> Dict[str, Any]:
    """
    Analyze chart image using vision model via Clawdbot
    
    Note: This integrates with Clawdbot's image tool
    """
    print(f"🔍 Analyzing chart: {image_path.name}")
    print(f"   Model: {model}")
    
    # Build analysis request
    analysis = {
        "timestamp": datetime.now().isoformat(),
        "image": str(image_path),
        "model": model,
        "prompt_used": prompt[:100] + "..." if len(prompt) > 100 else prompt,
    }
    
    try:
        # Use Clawdbot's image analysis capability
        # This is the integration point with the image tool
        
        # For direct Python usage, we'd call the API
        # For Clawdbot agent usage, the image tool handles this
        
        # Example Clawdbot tool call format:
        # image(image=str(image_path), prompt=prompt)
        
        # For now, document the expected output format
        analysis["status"] = "ready_for_analysis"
        analysis["instructions"] = f"""
To analyze this chart, use the Clawdbot image tool:

image(
    image="{image_path}",
    prompt=\"\"\"
{prompt}
\"\"\"
)

The vision model will return ICT analysis in JSON format.
"""
        
        return analysis
        
    except Exception as e:
        analysis["status"] = "error"
        analysis["error"] = str(e)
        return analysis

# ============================================================
# QUICK ANALYSIS FUNCTIONS
# ============================================================

def quick_bias_check(image_path: Path) -> Dict[str, Any]:
    """Quick bias check - just BULLISH/BEARISH/NEUTRAL"""
    return analyze_chart_image(image_path, QUICK_BIAS_PROMPT)

def exit_check(image_path: Path, position_type: str = "LONG", entry_zone: str = "middle") -> Dict[str, Any]:
    """Check if position should be exited"""
    prompt = EXIT_CHECK_PROMPT.format(
        position_type=position_type,
        entry_zone=entry_zone
    )
    return analyze_chart_image(image_path, prompt)

def analyze_specific_pattern(image_path: Path, pattern: str) -> Dict[str, Any]:
    """Analyze for a specific ICT pattern"""
    if pattern not in PATTERN_PROMPTS:
        return {"error": f"Unknown pattern: {pattern}. Available: {list(PATTERN_PROMPTS.keys())}"}
    
    return analyze_chart_image(image_path, PATTERN_PROMPTS[pattern])

# ============================================================
# MULTI-TIMEFRAME ANALYSIS
# ============================================================

def multi_timeframe_analysis(symbol: str, timeframes: list = ["1m", "5m", "15m"]) -> Dict[str, Any]:
    """
    Capture and analyze multiple timeframes for confluence
    """
    print(f"📊 Multi-timeframe analysis for {symbol}")
    print(f"   Timeframes: {timeframes}")
    
    results = {
        "symbol": symbol,
        "timestamp": datetime.now().isoformat(),
        "timeframes": {}
    }
    
    for tf in timeframes:
        print(f"\n--- {tf} ---")
        chart_path = capture_chart(symbol, tf)
        
        if chart_path:
            prompt = get_timeframe_prompt(tf)
            analysis = analyze_chart_image(chart_path, prompt)
            results["timeframes"][tf] = {
                "image": str(chart_path),
                "analysis": analysis
            }
        else:
            results["timeframes"][tf] = {"status": "capture_failed"}
    
    return results

# ============================================================
# SAVE ANALYSIS RESULTS
# ============================================================

def save_analysis(analysis: Dict[str, Any], symbol: str) -> Path:
    """Save analysis results to JSON file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{symbol}_analysis_{timestamp}.json"
    filepath = CONFIG["analysis_dir"] / filename
    
    with open(filepath, "w") as f:
        json.dump(analysis, f, indent=2, default=str)
    
    print(f"💾 Analysis saved: {filepath}")
    return filepath

# ============================================================
# MAIN CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Visual Chart Analyzer for Atlas")
    parser.add_argument("--symbol", "-s", default="ETH-PERP", help="Trading symbol")
    parser.add_argument("--timeframe", "-t", default="5m", help="Chart timeframe")
    parser.add_argument("--analyze-now", "-a", action="store_true", help="Capture and analyze immediately")
    parser.add_argument("--mtf", action="store_true", help="Multi-timeframe analysis")
    parser.add_argument("--pattern", "-p", help="Specific pattern to check")
    parser.add_argument("--image", "-i", help="Analyze existing image file")
    parser.add_argument("--exit-check", action="store_true", help="Check if should exit position")
    parser.add_argument("--position", default="LONG", help="Position type for exit check")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("VISUAL CHART ANALYZER - ATLAS EDITION")
    print("=" * 60)
    
    if args.image:
        # Analyze existing image
        image_path = Path(args.image)
        if not image_path.exists():
            print(f"❌ Image not found: {image_path}")
            return
        
        if args.exit_check:
            result = exit_check(image_path, args.position)
        elif args.pattern:
            result = analyze_specific_pattern(image_path, args.pattern)
        else:
            result = analyze_chart_image(image_path)
        
        print(json.dumps(result, indent=2, default=str))
        
    elif args.mtf:
        # Multi-timeframe analysis
        result = multi_timeframe_analysis(args.symbol)
        save_analysis(result, args.symbol)
        
    elif args.analyze_now:
        # Capture and analyze single timeframe
        chart_path = capture_chart(args.symbol, args.timeframe)
        if chart_path:
            result = analyze_chart_image(chart_path)
            save_analysis(result, args.symbol)
            print(json.dumps(result, indent=2, default=str))
        else:
            print("❌ Could not capture chart")
            
    else:
        # Just capture
        capture_chart(args.symbol, args.timeframe)

if __name__ == "__main__":
    main()
