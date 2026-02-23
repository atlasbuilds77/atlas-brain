"""
MERIDIAN V1 - Main Orchestrator
Coordinates scanner → executor → alerts pipeline
"""
import asyncio
import logging
import sys
from datetime import datetime
import pytz

import meridian_config as cfg
from meridian_scanner import scanner, SweepEvent
from meridian_executor import executor
from meridian_alerts import alerts

ET = pytz.timezone("US/Eastern")

# ── Session Bias Lock ──
# Set by first signal of the day. Opposing direction blocked for rest of session.
session_bias: str | None = None   # "bull" or "bear"

# ── Logging Setup ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(cfg.LOG_DIR / f"meridian_{datetime.now().strftime('%Y%m%d')}.log"),
    ],
)
log = logging.getLogger("meridian.main")


async def on_signal(sweep: SweepEvent):
    """Called when scanner detects a valid sweep+reclaim setup."""
    global session_bias
    log.info(f"🎯 SIGNAL: {sweep.direction} sweep+reclaim at {sweep.level}")

    # ── Time Check: Don't enter too close to trade window end ──
    now_et = datetime.now(ET)
    if now_et.hour == cfg.TRADE_END_HOUR and now_et.minute >= 20:
        log.warning(
            f"⛔ Signal BLOCKED: Too close to trade window end (10:30 ET). "
            f"Not enough time to reach target. Current time: {now_et.strftime('%H:%M:%S')} ET"
        )
        return

    # ── Session Bias Lock ──
    # First signal of the day sets the bias. Opposing signals are blocked.
    if session_bias is None:
        session_bias = sweep.direction
        log.info(f"📌 Session bias SET: {session_bias.upper()}")
    elif sweep.direction != session_bias:
        log.warning(
            f"⛔ Signal BLOCKED: {sweep.direction.upper()} opposes session bias "
            f"({session_bias.upper()}). Skipping."
        )
        return

    if executor.position:
        log.warning("Already in position, skipping signal")
        return

    await executor.execute_entry(sweep)

    if executor.position:
        asyncio.create_task(executor.manage_position())


async def main():
    log.info("=" * 50)
    log.info("MERIDIAN V1 Starting")
    log.info("=" * 50)

    now_et = datetime.now(ET)
    log.info(f"Current ET time: {now_et.strftime('%H:%M:%S')}")

    # Phase 1: Pre-market scan
    if now_et.hour < cfg.MARKET_OPEN_HOUR or (
        now_et.hour == cfg.MARKET_OPEN_HOUR and now_et.minute < cfg.MARKET_OPEN_MIN
    ):
        log.info("Phase 1: Pre-market level detection")
        await scanner.run_premarket()

        if scanner.state.pm_high and scanner.state.pm_low:
            log.info(f"PM HIGH: {scanner.state.pm_high}")
            log.info(f"PM LOW:  {scanner.state.pm_low}")
            log.info(f"Clusters: {len(scanner.state.clusters)}")
        else:
            log.warning("No PM levels detected - will retry at market open")
    else:
        log.info("Market already open - fetching PM levels retroactively")
        await scanner.run_premarket()

    # Phase 2: Market open scanning
    trade_end_hour = cfg.TRADE_END_HOUR
    trade_end_min = cfg.TRADE_END_MIN
    if now_et.hour < trade_end_hour or (
        now_et.hour == trade_end_hour and now_et.minute < trade_end_min
    ):
        log.info("Phase 2: Market open sweep detection")
        await scanner.run_market_scan(on_signal_callback=on_signal)
    else:
        log.info("Trade window already closed for today")

    # Phase 3: If still in position, keep managing
    if executor.position:
        log.info("Phase 3: Managing remaining position")
        await executor.manage_position()

    log.info("MERIDIAN V1 session complete")
    await alerts.send("🏁 <b>MERIDIAN V1</b> - Session complete")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("MERIDIAN V1 interrupted")
    except Exception as e:
        log.exception(f"MERIDIAN V1 fatal error: {e}")
        asyncio.run(alerts.send(f"🚨 <b>MERIDIAN V1 ERROR</b>\n{e}"))
