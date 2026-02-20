"""
MERIDIAN V1 - Telegram Alerts
"""
import asyncio
import logging
import aiohttp
from datetime import datetime
import meridian_config as cfg

log = logging.getLogger("meridian.alerts")


class MeridianAlerts:
    def __init__(self):
        self.token = cfg.TELEGRAM_BOT_TOKEN
        self.chat_id = cfg.TELEGRAM_CHAT_ID
        self.enabled = bool(self.token and self.chat_id)
        if not self.enabled:
            log.warning("Telegram alerts disabled - no token/chat_id configured")

    async def send(self, message: str):
        """Send a Telegram message."""
        if not self.enabled:
            log.info(f"[ALERT-DISABLED] {message}")
            return
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        log.error(f"Telegram error {resp.status}: {await resp.text()}")
        except Exception as e:
            log.error(f"Telegram send failed: {e}")

    def _now(self):
        return datetime.now().strftime("%H:%M:%S")

    async def pm_levels(self, pm_high: float, pm_low: float, clusters: list):
        cluster_str = ", ".join(f"${c:.2f}" for c in clusters[:5])
        await self.send(
            f"🔭 <b>MERIDIAN V1 - Pre-Market Levels</b>\n"
            f"⏰ {self._now()}\n"
            f"📈 PM High: <b>${pm_high:.2f}</b>\n"
            f"📉 PM Low: <b>${pm_low:.2f}</b>\n"
            f"🎯 Clusters: {cluster_str or 'None'}"
        )

    async def sweep_detected(self, direction: str, level: float, price: float):
        emoji = "🔴" if direction == "bear" else "🟢"
        await self.send(
            f"{emoji} <b>SWEEP DETECTED</b>\n"
            f"⏰ {self._now()}\n"
            f"Direction: {direction.upper()}\n"
            f"Level: ${level:.2f}\n"
            f"Price: ${price:.2f}\n"
            f"⏳ Watching for reclaim..."
        )

    async def entry_executed(self, direction: str, contracts_0dte: int, contracts_1dte: int,
                              strike: float, avg_price: float):
        emoji = "🟢" if direction == "bull" else "🔴"
        await self.send(
            f"{emoji} <b>ENTRY EXECUTED</b>\n"
            f"⏰ {self._now()}\n"
            f"Direction: {direction.upper()}\n"
            f"Strike: ${strike:.0f}\n"
            f"0DTE: {contracts_0dte} contracts\n"
            f"1DTE: {contracts_1dte} contracts\n"
            f"Avg Price: ${avg_price:.2f}"
        )

    async def exit_executed(self, direction: str, pnl: float, pnl_pct: float, reason: str):
        emoji = "✅" if pnl >= 0 else "❌"
        await self.send(
            f"{emoji} <b>EXIT - {reason.upper()}</b>\n"
            f"⏰ {self._now()}\n"
            f"Direction: {direction.upper()}\n"
            f"P&L: ${pnl:+.2f} ({pnl_pct:+.1%})\n"
        )


# Singleton
alerts = MeridianAlerts()
