#!/usr/bin/env python3
"""
Atlas Eyes - Main Entry Point
Unified visual trading analysis for Atlas

Usage:
  python3 atlas_eyes.py analyze ETH-PERP
  python3 atlas_eyes.py monitor --symbol ETH-PERP --side LONG --entry 2911
  python3 atlas_eyes.py quick-check /path/to/chart.png
"""

import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# ============================================================
# BANNER
# ============================================================

BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║     █████╗ ████████╗██╗      █████╗ ███████╗                  ║
║    ██╔══██╗╚══██╔══╝██║     ██╔══██╗██╔════╝                  ║
║    ███████║   ██║   ██║     ███████║███████╗                  ║
║    ██╔══██║   ██║   ██║     ██╔══██║╚════██║                  ║
║    ██║  ██║   ██║   ███████╗██║  ██║███████║                  ║
║    ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝                  ║
║                                                               ║
║    ███████╗██╗   ██╗███████╗███████╗                          ║
║    ██╔════╝╚██╗ ██╔╝██╔════╝██╔════╝                          ║
║    █████╗   ╚████╔╝ █████╗  ███████╗                          ║
║    ██╔══╝    ╚██╔╝  ██╔══╝  ╚════██║                          ║
║    ███████╗   ██║   ███████╗███████║                          ║
║    ╚══════╝   ╚═╝   ╚══════╝╚══════╝                          ║
║                                                               ║
║    Visual Trading System - ICT/SMC Chart Analysis             ║
╚═══════════════════════════════════════════════════════════════╝
"""

# ============================================================
# ICT QUICK REFERENCE (for Atlas context)
# ============================================================

ICT_QUICKREF = """
╔═══════════════════════════════════════════════════════════════╗
║                   ICT/SMC QUICK REFERENCE                     ║
╠═══════════════════════════════════════════════════════════════╣
║ MARKET STRUCTURE                                              ║
║   • BOS (Break of Structure) - Continuation signal            ║
║   • ChoCH (Change of Character) - Reversal signal             ║
║   • HH/HL = Uptrend | LH/LL = Downtrend                       ║
╠═══════════════════════════════════════════════════════════════╣
║ ORDER BLOCKS (OB)                                             ║
║   • Bullish OB: Last red candle before up move (demand)       ║
║   • Bearish OB: Last green candle before down move (supply)   ║
║   • Price often returns to OBs before continuing              ║
╠═══════════════════════════════════════════════════════════════╣
║ FAIR VALUE GAP (FVG/Imbalance)                                ║
║   • Gap between candle 1 high and candle 3 low                ║
║   • Price tends to return to fill gaps                        ║
║   • Watch reaction at gap fill for continuation/reversal      ║
╠═══════════════════════════════════════════════════════════════╣
║ LIQUIDITY                                                     ║
║   • Equal Highs/Lows = Stop loss clusters                     ║
║   • Smart money hunts these levels                            ║
║   • Liquidity grab + reversal = high probability setup        ║
╠═══════════════════════════════════════════════════════════════╣
║ EXIT SIGNALS                                                  ║
║   🔴 FULL EXIT: ChoCH, OB break, MTF alignment against        ║
║   🟡 SCALE OUT: FVG filled, momentum waning, liq approach     ║
║   🟢 HOLD: Structure intact, pulling back to OB, trend OK     ║
╚═══════════════════════════════════════════════════════════════╝
"""

# ============================================================
# COMMANDS
# ============================================================

def cmd_analyze(args):
    """One-shot chart analysis"""
    from visual_analyzer import multi_timeframe_analysis, save_analysis
    
    print(f"\n📊 Analyzing {args.symbol}...")
    
    if args.mtf:
        result = multi_timeframe_analysis(args.symbol, ["1m", "5m", "15m"])
    else:
        from visual_analyzer import capture_chart, analyze_chart_image
        chart = capture_chart(args.symbol, args.timeframe)
        if chart:
            result = analyze_chart_image(chart)
        else:
            result = {"error": "Chart capture failed"}
    
    if not args.quiet:
        print(json.dumps(result, indent=2, default=str))
    
    save_analysis(result, args.symbol)
    return result

def cmd_monitor(args):
    """Start position monitoring"""
    from position_monitor import PositionState, monitor_position
    import asyncio
    
    position = PositionState(
        symbol=args.symbol,
        side=args.side,
        entry_price=args.entry
    )
    
    asyncio.run(monitor_position(position))

def cmd_quick_check(args):
    """Quick analysis of existing chart image"""
    from visual_analyzer import analyze_chart_image, quick_bias_check, exit_check
    from pathlib import Path
    
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return
    
    print(f"\n🔍 Quick check: {image_path.name}")
    
    if args.exit:
        result = exit_check(image_path, args.position)
    else:
        result = quick_bias_check(image_path)
    
    print(json.dumps(result, indent=2, default=str))
    return result

def cmd_status(args):
    """Show system status"""
    print("\n📊 ATLAS EYES STATUS")
    print("=" * 40)
    
    # Check captures
    captures_dir = Path(__file__).parent / "captures"
    if captures_dir.exists():
        dates = list(captures_dir.iterdir())
        print(f"Captures: {len(dates)} days stored")
        if dates:
            latest = max(dates)
            charts = list(latest.iterdir())
            print(f"  Latest: {latest.name} ({len(charts)} charts)")
    else:
        print("Captures: None yet")
    
    # Check analysis
    analysis_dir = Path(__file__).parent / "analysis"
    if analysis_dir.exists():
        analyses = list(analysis_dir.glob("*.json"))
        print(f"Analyses: {len(analyses)} saved")
    else:
        print("Analyses: None yet")
    
    # Check monitor log
    log_file = Path(__file__).parent / "monitor_log.json"
    if log_file.exists():
        with open(log_file) as f:
            lines = f.readlines()
        print(f"Monitor log: {len(lines)} entries")
    else:
        print("Monitor log: Empty")

def cmd_help(args):
    """Show ICT quick reference"""
    print(ICT_QUICKREF)

# ============================================================
# MAIN
# ============================================================

def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(
        description="Atlas Eyes - Visual Trading Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  atlas_eyes.py analyze ETH-PERP --mtf
  atlas_eyes.py monitor --symbol SOL-PERP --side LONG --entry 150.50
  atlas_eyes.py quick-check /path/to/chart.png --exit
  atlas_eyes.py ict-ref
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # analyze command
    p_analyze = subparsers.add_parser("analyze", help="Analyze a trading pair")
    p_analyze.add_argument("symbol", help="Trading symbol (e.g., ETH-PERP)")
    p_analyze.add_argument("--timeframe", "-t", default="5m", help="Timeframe")
    p_analyze.add_argument("--mtf", action="store_true", help="Multi-timeframe analysis")
    p_analyze.add_argument("--quiet", "-q", action="store_true", help="Minimal output")
    p_analyze.set_defaults(func=cmd_analyze)
    
    # monitor command
    p_monitor = subparsers.add_parser("monitor", help="Monitor open position")
    p_monitor.add_argument("--symbol", "-s", required=True, help="Trading symbol")
    p_monitor.add_argument("--side", required=True, choices=["LONG", "SHORT"])
    p_monitor.add_argument("--entry", "-e", type=float, required=True, help="Entry price")
    p_monitor.add_argument("--interval", "-i", type=int, default=60, help="Check interval")
    p_monitor.set_defaults(func=cmd_monitor)
    
    # quick-check command
    p_quick = subparsers.add_parser("quick-check", help="Quick analysis of image")
    p_quick.add_argument("image", help="Path to chart image")
    p_quick.add_argument("--exit", action="store_true", help="Check for exit signal")
    p_quick.add_argument("--position", default="LONG", help="Position type for exit check")
    p_quick.set_defaults(func=cmd_quick_check)
    
    # status command
    p_status = subparsers.add_parser("status", help="Show system status")
    p_status.set_defaults(func=cmd_status)
    
    # ict-ref command
    p_ict = subparsers.add_parser("ict-ref", help="Show ICT quick reference")
    p_ict.set_defaults(func=cmd_help)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        print("\n💡 Try: python3 atlas_eyes.py ict-ref")
        return
    
    args.func(args)

if __name__ == "__main__":
    main()
