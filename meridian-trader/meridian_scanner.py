"""
MERIDIAN V1 - Scanner
Pre-market level detection + real-time sweep monitoring

v1 Fixes:
  FIX 1 - Opening Flush Detection: skip bull signals in first 30 bars if 3 red opens
  FIX 2 - Reclaim Body Quality: reject wick reclaims (body < 20% of range)
  FIX 3 - Level Fatigue: skip level after 2+ successful reclaims this session
"""
import asyncio
import logging
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
import aiohttp
import pytz

import meridian_config as cfg
from meridian_alerts import alerts

log = logging.getLogger("meridian.scanner")
ET = pytz.timezone("US/Eastern")


@dataclass
class SweepEvent:
    direction: str        # "bull" or "bear"
    level: float          # The PM level that was swept
    sweep_bar_idx: int    # Bar index when sweep happened
    sweep_price: float    # Price at sweep
    reclaimed: bool = False
    expired: bool = False


@dataclass
class ScannerState:
    pm_high: Optional[float] = None
    pm_low: Optional[float] = None
    clusters: list = field(default_factory=list)
    sweep_history: list = field(default_factory=list)    # (level, timestamp)
    reclaim_history: list = field(default_factory=list)  # (level, timestamp) — FIX 3
    active_sweep: Optional[SweepEvent] = None
    bars_since_sweep: int = 0
    bar_count: int = 0
    flush_mode: bool = False  # FIX 1: True if opening 3 bars were all red


class MeridianScanner:
    def __init__(self):
        self.state = ScannerState()
        self.headers = {
            "Authorization": f"Bearer {cfg.TRADIER_TOKEN}",
            "Accept": "application/json",
        }
        self.base = cfg.TRADIER_BASE_URL

    # ── Tradier Data ──

    async def fetch_bars(self, session: aiohttp.ClientSession,
                         interval: str = "1min",
                         start: str = None, end: str = None) -> list:
        """Fetch OHLCV bars from Tradier with retry logic."""
        url = f"{self.base}/v1/markets/timesales"
        params = {
            "symbol": cfg.SYMBOL,
            "interval": interval,
            "session_filter": "all",  # Include pre-market
        }
        if start:
            params["start"] = start
        if end:
            params["end"] = end

        # Retry logic: 3 attempts with exponential backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                async with session.get(url, headers=self.headers, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        log.error(f"Tradier bars error {resp.status}: {await resp.text()}")
                        return []
                    data = await resp.json()
                    series = data.get("series", {})
                    if not series:
                        return []
                    bars = series.get("data", [])
                    if isinstance(bars, dict):
                        bars = [bars]
                    return bars
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                log.warning(f"Tradier API error (attempt {attempt+1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait_time)
                else:
                    log.error(f"Tradier API failed after {max_retries} attempts. Returning empty.")
                    return []
            except Exception as e:
                # Catch-all for unexpected errors
                log.error(f"Unexpected error in fetch_bars (attempt {attempt+1}/{max_retries}): {type(e).__name__}: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    log.error("fetch_bars failed after retries with unexpected error. Returning empty.")
                    return []
        return []

    async def fetch_daily_bars(self, session: aiohttp.ClientSession, days: int = 15) -> list:
        """Fetch daily bars for cluster detection."""
        url = f"{self.base}/v1/markets/history"
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days + 5)).strftime("%Y-%m-%d")
        params = {
            "symbol": cfg.SYMBOL,
            "interval": "daily",
            "start": start_date,
            "end": end_date,
        }
        async with session.get(url, headers=self.headers, params=params) as resp:
            if resp.status != 200:
                log.error(f"Tradier daily error {resp.status}")
                return []
            data = await resp.json()
            history = data.get("history", {})
            if not history:
                return []
            days_data = history.get("day", [])
            if isinstance(days_data, dict):
                days_data = [days_data]
            return days_data[-days:]

    # ── Level Detection ──

    def compute_pm_levels(self, bars: list) -> tuple:
        """Calculate pre-market high and low from bars."""
        if not bars:
            return None, None
        highs = [float(b.get("high", b.get("price", 0))) for b in bars]
        lows = [float(b.get("low", b.get("price", 999999))) for b in bars]
        pm_high = max(highs) if highs else None
        pm_low = min(lows) if lows else None
        return pm_high, pm_low

    def find_clusters(self, daily_bars: list) -> list:
        """Find price clusters from daily highs/lows over lookback period."""
        levels = []
        for bar in daily_bars:
            levels.append(float(bar["high"]))
            levels.append(float(bar["low"]))

        if not levels:
            return []

        levels.sort()
        clusters = []
        i = 0
        while i < len(levels):
            cluster = [levels[i]]
            j = i + 1
            while j < len(levels):
                if abs(levels[j] - cluster[-1]) / cluster[-1] < cfg.CLUSTER_PROXIMITY_PCT:
                    cluster.append(levels[j])
                    j += 1
                else:
                    break
            if len(cluster) >= 2:
                clusters.append(sum(cluster) / len(cluster))
            i = j

        return sorted(clusters)

    # ── FIX 1: Opening Flush Detection ──

    def _check_opening_flush(self, bars: list) -> bool:
        """
        FIX 1: Check if first 3 regular-session bars are ALL red (close < open).
        If yes, sets flush_mode=True to block bull signals until bar 30.
        """
        if len(bars) < 3:
            return False
        first_three = bars[:3]
        all_red = all(
            float(b.get("close", b.get("price", 0))) < float(b.get("open", b.get("price", 0)))
            for b in first_three
        )
        if all_red and not self.state.flush_mode:
            self.state.flush_mode = True
            log.info("Opening flush detected — bull signals paused until bar 30")
        return all_red

    # ── Sweep Detection ──

    def _cooldown_ok(self, level: float) -> bool:
        """
        Check if level hasn't been swept too recently (15min cooldown).
        FIX 3: Also block if level has been successfully reclaimed 2+ times.
        """
        # FIX 3: Level fatigue check
        reclaim_count = sum(
            1 for lv, ts in self.state.reclaim_history
            if abs(lv - level) < 0.10
        )
        if reclaim_count >= 2:
            log.info(f"Level fatigued after 2 reclaims — skipping (level={level:.2f})")
            return False

        now = time.time()
        recent = [ts for lv, ts in self.state.sweep_history
                  if abs(lv - level) < 0.10 and now - ts < cfg.SWEEP_COOLDOWN_SEC]
        return len(recent) < 2

    def check_sweep(self, bar: dict) -> Optional[SweepEvent]:
        """Check if current bar sweeps a PM level."""
        if self.state.pm_high is None or self.state.pm_low is None:
            return None
        if self.state.active_sweep is not None:
            return None  # Already tracking a sweep

        price_high = float(bar.get("high", bar.get("price", 0)))
        price_low = float(bar.get("low", bar.get("price", 0)))
        close = float(bar.get("close", bar.get("price", 0)))

        # Bear sweep: price goes ABOVE pm_high then closes below
        if price_high > self.state.pm_high and close <= self.state.pm_high:
            if self._cooldown_ok(self.state.pm_high):
                return SweepEvent(
                    direction="bear",
                    level=self.state.pm_high,
                    sweep_bar_idx=self.state.bar_count,
                    sweep_price=price_high,
                )

        # Bull sweep: price goes BELOW pm_low then closes above
        if price_low < self.state.pm_low and close >= self.state.pm_low:
            if self._cooldown_ok(self.state.pm_low):
                return SweepEvent(
                    direction="bull",
                    level=self.state.pm_low,
                    sweep_bar_idx=self.state.bar_count,
                    sweep_price=price_low,
                )

        return None

    def check_reclaim(self, bar: dict) -> bool:
        """
        Check if price reclaims the swept level within MAX_RECLAIM_BARS.
        FIX 2: Reject wick reclaims — body must be >= 20% of bar range.
        """
        sweep = self.state.active_sweep
        if not sweep:
            return False

        bars_elapsed = self.state.bar_count - sweep.sweep_bar_idx
        close = float(bar.get("close", bar.get("price", 0)))

        if bars_elapsed > cfg.MAX_RECLAIM_BARS:
            sweep.expired = True
            log.info(f"Sweep expired after {bars_elapsed} bars")
            return False

        # Check directional reclaim
        reclaim_confirmed = False
        if sweep.direction == "bear":
            if close > sweep.level:
                reclaim_confirmed = True
        else:
            if close < sweep.level:
                reclaim_confirmed = True

        if not reclaim_confirmed:
            return False

        # ── FIX 2: Body Quality Check ──
        bar_open = float(bar.get("open", bar.get("price", 0)))
        bar_close = close
        bar_high = float(bar.get("high", bar.get("price", 0)))
        bar_low = float(bar.get("low", bar.get("price", 0)))
        bar_body = bar_close - bar_open   # positive = green, negative = red
        bar_range = bar_high - bar_low

        # For bull reclaim the body should be positive (green bar)
        # For bear reclaim the body should be negative (red bar)
        if sweep.direction == "bull":
            if bar_body <= 0:
                log.info("Reclaim rejected — weak body (wick reclaim): red bar on bull reclaim")
                return False
            if bar_range > 0 and bar_body < (bar_range * 0.20):
                log.info(f"Reclaim rejected — weak body (wick reclaim): body={bar_body:.3f} range={bar_range:.3f}")
                return False
        else:  # bear reclaim
            if bar_body >= 0:
                log.info("Reclaim rejected — weak body (wick reclaim): green bar on bear reclaim")
                return False
            if bar_range > 0 and abs(bar_body) < (bar_range * 0.20):
                log.info(f"Reclaim rejected — weak body (wick reclaim): body={abs(bar_body):.3f} range={bar_range:.3f}")
                return False

        # ── Valid reclaim confirmed ──
        sweep.reclaimed = True
        return True

    # ── Main Scan Loop ──

    async def run_premarket(self):
        """Run pre-market scan: fetch PM levels + clusters."""
        log.info("Starting pre-market scan...")
        async with aiohttp.ClientSession() as session:
            now_et = datetime.now(ET)
            today = now_et.strftime("%Y-%m-%d")

            # Fetch PM bars (4:00-9:30 ET)
            pm_start = f"{today} 04:00"
            pm_end = f"{today} 09:30"
            bars = await self.fetch_bars(session, start=pm_start, end=pm_end)

            if bars:
                self.state.pm_high, self.state.pm_low = self.compute_pm_levels(bars)
                log.info(f"PM HIGH: {self.state.pm_high}, PM LOW: {self.state.pm_low}")

                if self.state.pm_high and self.state.pm_low:
                    pm_range = self.state.pm_high - self.state.pm_low
                    if pm_range < cfg.MIN_PM_RANGE:
                        log.warning(f"PM RANGE ${pm_range:.2f} < ${cfg.MIN_PM_RANGE} - SKIPPING TODAY")
                        self.state.pm_high = None
                        self.state.pm_low = None
            else:
                log.warning("No PM bars available yet")

            # Fetch daily bars for clusters
            daily = await self.fetch_daily_bars(session, cfg.CLUSTER_LOOKBACK_DAYS)
            self.state.clusters = self.find_clusters(daily)
            log.info(f"Found {len(self.state.clusters)} clusters")

            if self.state.pm_high and self.state.pm_low:
                await alerts.pm_levels(self.state.pm_high, self.state.pm_low, self.state.clusters)

        return self.state

    async def run_market_scan(self, on_signal_callback=None):
        """Monitor market open for sweeps. Calls on_signal_callback(SweepEvent) on valid setup."""
        log.info("Starting market-open sweep scanner...")
        async with aiohttp.ClientSession() as session:
            while True:
                now_et = datetime.now(ET)

                # Only trade 9:30 ET onward (end computed dynamically below)
                market_open = now_et.replace(hour=cfg.MARKET_OPEN_HOUR, minute=cfg.MARKET_OPEN_MIN, second=0, microsecond=0)

                if now_et < market_open:
                    wait = (market_open - now_et).total_seconds()
                    log.info(f"Waiting {wait:.0f}s for market open...")
                    await asyncio.sleep(min(wait, 60))
                    continue

                # FIX 4: Extend trade window on flush days (bar 90 = 11:00 ET = 8:00 PT)
                if self.state.flush_mode:
                    trade_end = now_et.replace(hour=11, minute=0, second=0, microsecond=0)
                    window_label = "11:00 ET (flush day — extended to 8:00 PT)"
                else:
                    trade_end = now_et.replace(hour=cfg.TRADE_END_HOUR, minute=cfg.TRADE_END_MIN, second=0, microsecond=0)
                    window_label = f"{cfg.TRADE_END_HOUR}:{cfg.TRADE_END_MIN:02d} ET"

                if now_et > trade_end:
                    log.info(f"Trade window closed ({window_label})")
                    break

                # Fetch latest bars
                today = now_et.strftime("%Y-%m-%d")
                bars = await self.fetch_bars(session, start=f"{today} 09:30")

                if not bars:
                    await asyncio.sleep(10)
                    continue

                # ── FIX 1: Opening Flush Detection ──
                # Run once when we have at least 3 bars
                if self.state.bar_count == 0 and len(bars) >= 3:
                    self._check_opening_flush(bars)

                # Update PM levels if not set (late start)
                if self.state.pm_high is None:
                    pm_bars = await self.fetch_bars(session, start=f"{today} 04:00", end=f"{today} 09:30")
                    if pm_bars:
                        self.state.pm_high, self.state.pm_low = self.compute_pm_levels(pm_bars)
                        log.info(f"Late PM levels: H={self.state.pm_high} L={self.state.pm_low}")

                # Process latest bar
                latest = bars[-1]
                self.state.bar_count = len(bars)

                if self.state.active_sweep:
                    # Check for reclaim
                    if self.check_reclaim(latest):
                        sweep = self.state.active_sweep

                        # ── FIX 1: Block bull signals during flush mode ──
                        if self.state.flush_mode and sweep.direction == "bull" and self.state.bar_count < 30:
                            log.info(f"Opening flush active — bull signal blocked (bar {self.state.bar_count}/30)")
                        else:
                            log.info(f"✅ RECLAIM! {sweep.direction} sweep at {sweep.level}")
                            self.state.sweep_history.append((sweep.level, time.time()))
                            # FIX 3: Record successful reclaim separately
                            self.state.reclaim_history.append((sweep.level, time.time()))
                            if on_signal_callback:
                                await on_signal_callback(sweep)

                        self.state.active_sweep = None
                    elif self.state.active_sweep.expired:
                        log.info("Sweep expired, clearing")
                        self.state.active_sweep = None
                else:
                    # Check for new sweep
                    sweep = self.check_sweep(latest)
                    if sweep:
                        self.state.active_sweep = sweep
                        log.info(f"🔍 SWEEP: {sweep.direction} at {sweep.level}")
                        await alerts.sweep_detected(
                            sweep.direction, sweep.level, sweep.sweep_price
                        )

                # Poll every ~15 seconds
                await asyncio.sleep(15)


scanner = MeridianScanner()
