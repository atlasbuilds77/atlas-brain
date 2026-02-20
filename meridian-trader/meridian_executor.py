"""
MERIDIAN V1 - Executor
Tradier order execution + position management
"""
import asyncio
import logging
import math
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
import aiohttp
import pytz

import meridian_config as cfg
from meridian_alerts import alerts
from meridian_scanner import SweepEvent

log = logging.getLogger("meridian.executor")
ET = pytz.timezone("US/Eastern")


@dataclass
class Position:
    direction: str           # "bull" or "bear"
    symbol_0dte: str         # Option symbol
    symbol_1dte: str
    qty_0dte: int
    qty_1dte: int
    entry_price_0dte: float
    entry_price_1dte: float
    avg_entry: float
    stop_pct: float = -0.50  # Current stop level
    high_water: float = 0.0  # Highest P&L %
    order_ids: list = field(default_factory=list)
    # Per-account tracking for multi-account exit
    account_lots: list = field(default_factory=list)  # [{name, account, token, qty_0dte, qty_1dte}]


class MeridianExecutor:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {cfg.TRADIER_TOKEN}",
            "Accept": "application/json",
        }
        self.base = cfg.TRADIER_BASE_URL
        self.account = cfg.TRADIER_ACCOUNT
        self.position: Optional[Position] = None

    # ── Option Chain ──

    async def get_option_chain(self, session: aiohttp.ClientSession,
                                expiration: str, option_type: str = "call") -> list:
        """Fetch option chain for given expiration."""
        url = f"{self.base}/v1/markets/options/chains"
        params = {
            "symbol": cfg.SYMBOL,
            "expiration": expiration,
            "greeks": "false",
        }
        async with session.get(url, headers=self.headers, params=params) as resp:
            if resp.status != 200:
                log.error(f"Chain error {resp.status}: {await resp.text()}")
                return []
            data = await resp.json()
            options = data.get("options", {})
            if not options:
                return []
            chain = options.get("option", [])
            if isinstance(chain, dict):
                chain = [chain]
            return [o for o in chain if o.get("option_type") == option_type]

    async def get_expirations(self, session: aiohttp.ClientSession) -> list:
        """Get available option expirations."""
        url = f"{self.base}/v1/markets/options/expirations"
        params = {"symbol": cfg.SYMBOL}
        async with session.get(url, headers=self.headers, params=params) as resp:
            if resp.status != 200:
                return []
            data = await resp.json()
            exps = data.get("expirations", {}).get("date", [])
            if isinstance(exps, str):
                exps = [exps]
            return exps

    def select_strike(self, chain: list, underlying_price: float,
                      direction: str, otm_offset: float = 3.0) -> Optional[dict]:
        """Select strike $3 OTM."""
        if direction == "bull":
            target = underlying_price + otm_offset
            calls = [o for o in chain if o.get("option_type") == "call"]
            if not calls:
                return None
            return min(calls, key=lambda o: abs(float(o["strike"]) - target))
        else:
            target = underlying_price - otm_offset
            puts = [o for o in chain if o.get("option_type") == "put"]
            if not puts:
                return None
            return min(puts, key=lambda o: abs(float(o["strike"]) - target))

    # ── Order Execution ──

    async def place_order(self, session: aiohttp.ClientSession,
                          option_symbol: str, qty: int, side: str = "buy_to_open",
                          account: str = None, token: str = None) -> Optional[str]:
        """Place a market order via Tradier. Uses per-account token if provided."""
        acct = account or self.account
        auth = token or self.headers["Authorization"].split(" ")[1]
        url = f"{self.base}/v1/accounts/{acct}/orders"
        headers = {"Authorization": f"Bearer {auth}", "Accept": "application/json"}
        payload = {
            "class": "option",
            "symbol": cfg.SYMBOL,
            "option_symbol": option_symbol,
            "side": side,
            "quantity": str(qty),
            "type": "market",
            "duration": "day",
        }
        async with session.post(url, headers=headers, data=payload) as resp:
            if resp.status != 200:
                log.error(f"Order error {resp.status} [{acct}]: {await resp.text()}")
                return None
            data = await resp.json()
            order = data.get("order", {})
            order_id = order.get("id")
            log.info(f"Order placed [{acct}]: {order_id} - {side} {qty}x {option_symbol}")
            return str(order_id) if order_id else None

    async def get_account_balance(self, session: aiohttp.ClientSession,
                                   account: str, token: str) -> float:
        """Get account equity for position sizing."""
        url = f"{self.base}/v1/accounts/{account}/balances"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    log.warning(f"Balance API {resp.status} for {account}")
                    return 0.0
                data = await resp.json()
                bal = data.get("balances", {})
                # Cash accounts: equity=0, use total_equity or total_cash
                val = (bal.get("total_equity") or
                       bal.get("total_cash") or
                       bal.get("equity") or 0)
                log.info(f"[{account}] balance raw: total_equity={bal.get('total_equity')} "
                         f"total_cash={bal.get('total_cash')} equity={bal.get('equity')}")
                return float(val)
        except Exception as e:
            log.warning(f"Balance fetch exception for {account}: {e}")
            return 0.0

    async def get_quote(self, session: aiohttp.ClientSession, symbol: str) -> Optional[float]:
        """Get current quote for a symbol."""
        url = f"{self.base}/v1/markets/quotes"
        params = {"symbols": symbol}
        async with session.get(url, headers=self.headers, params=params) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            quotes = data.get("quotes", {}).get("quote", {})
            if isinstance(quotes, list):
                quotes = quotes[0]
            return float(quotes.get("last", 0))

    async def get_underlying_price(self, session: aiohttp.ClientSession) -> float:
        """Get current QQQ price."""
        price = await self.get_quote(session, cfg.SYMBOL)
        return price or 0.0

    # ── Entry Logic ──

    async def execute_entry(self, sweep: SweepEvent):
        """Execute full entry: 80% 0DTE + 20% 1DTE."""
        log.info(f"Executing entry for {sweep.direction} sweep at {sweep.level}")

        async with aiohttp.ClientSession() as session:
            price = await self.get_underlying_price(session)
            if price <= 0:
                log.error("Cannot get underlying price")
                return

            expirations = await self.get_expirations(session)
            if len(expirations) < 2:
                log.error("Not enough expirations available")
                return

            today = datetime.now(ET).strftime("%Y-%m-%d")
            exp_0dte = expirations[0]
            exp_1dte = expirations[1] if expirations[0] == today else expirations[0]
            if exp_0dte != today and len(expirations) >= 2:
                exp_0dte = expirations[0]
                exp_1dte = expirations[1]

            opt_type = "call" if sweep.direction == "bull" else "put"
            chain_0dte = await self.get_option_chain(session, exp_0dte, opt_type)
            chain_1dte = await self.get_option_chain(session, exp_1dte, opt_type)

            if not chain_0dte or not chain_1dte:
                log.error("Empty option chains")
                return

            strike_0dte = self.select_strike(chain_0dte, price, sweep.direction, cfg.OTM_OFFSET)
            strike_1dte = self.select_strike(chain_1dte, price, sweep.direction, cfg.OTM_OFFSET)

            if not strike_0dte or not strike_1dte:
                log.error("Could not find appropriate strikes")
                return

            sym_0dte = strike_0dte["symbol"]
            sym_1dte = strike_1dte["symbol"]
            ask_0dte = float(strike_0dte.get("ask", strike_0dte.get("last", 1.0)))
            ask_1dte = float(strike_1dte.get("ask", strike_1dte.get("last", 1.0)))

            # ── Multi-Account Execution ──
            all_order_ids = []
            account_lots = []
            total_qty_0dte = 0
            total_qty_1dte = 0

            for acct_cfg in cfg.TRADING_ACCOUNTS:
                acct_name    = acct_cfg["name"]
                acct_id      = acct_cfg["account"]
                acct_token   = acct_cfg["token"]
                size_pct     = acct_cfg["size_pct"]
                fallback_eq  = acct_cfg.get("fallback_equity", 0)

                equity = await self.get_account_balance(session, acct_id, acct_token)
                if equity <= 0:
                    if fallback_eq > 0:
                        log.warning(f"[{acct_name}] API equity=0, using hardwired fallback=${fallback_eq:.2f}")
                        equity = fallback_eq
                    else:
                        log.error(f"[{acct_name}] No equity and no fallback — skipping")
                        continue

                budget = equity * size_pct
                budget_0dte = budget * cfg.POSITION_0DTE_PCT
                budget_1dte = budget * cfg.POSITION_1DTE_PCT

                qty_0 = max(1, int(budget_0dte / (ask_0dte * 100)))
                qty_1 = max(1, int(budget_1dte / (ask_1dte * 100)))

                log.info(f"[{acct_name}] equity=${equity:.0f} budget=${budget:.0f} "
                         f"→ {qty_0}x 0DTE + {qty_1}x 1DTE")

                oid_0 = await self.place_order(session, sym_0dte, qty_0, account=acct_id, token=acct_token)
                oid_1 = await self.place_order(session, sym_1dte, qty_1, account=acct_id, token=acct_token)
                all_order_ids.extend([oid_0, oid_1])
                total_qty_0dte += qty_0
                total_qty_1dte += qty_1
                account_lots.append({
                    "name": acct_name, "account": acct_id, "token": acct_token,
                    "qty_0dte": qty_0, "qty_1dte": qty_1,
                })

            if not any(all_order_ids):
                log.error("All orders failed across all accounts!")
                return

            qty_0dte = total_qty_0dte
            qty_1dte = total_qty_1dte

            avg_entry = ((ask_0dte * qty_0dte) + (ask_1dte * qty_1dte)) / (qty_0dte + qty_1dte) if (qty_0dte + qty_1dte) > 0 else ask_0dte
            self.position = Position(
                direction=sweep.direction,
                symbol_0dte=sym_0dte,
                symbol_1dte=sym_1dte,
                qty_0dte=qty_0dte,
                qty_1dte=qty_1dte,
                entry_price_0dte=ask_0dte,
                entry_price_1dte=ask_1dte,
                avg_entry=avg_entry,
                order_ids=all_order_ids,
                account_lots=account_lots,
            )

            await alerts.entry_executed(
                sweep.direction, qty_0dte, qty_1dte,
                float(strike_0dte["strike"]), avg_entry
            )

            # AUTO-BROADCAST (BOOT-CRITICAL: every options trade must broadcast)
            try:
                import requests as req
                payload = {
                    "symbol": cfg.SYMBOL,
                    "strike_0dte": float(strike_0dte["strike"]),
                    "strike_1dte": float(strike_1dte["strike"]),
                    "expiry_0dte": exp_0dte,
                    "expiry_1dte": exp_1dte,
                    "action": "buy_to_open",
                    "direction": sweep.direction,
                    "qty_0dte": qty_0dte,
                    "qty_1dte": qty_1dte,
                    "avg_entry": avg_entry,
                    "option_type": opt_type,
                    "source": "meridian_auto",
                }
                req.post("http://localhost:8001/broadcast", json=payload, timeout=3)
                log.info("Auto-broadcast sent to copy-trade relay")
            except Exception as e:
                log.warning(f"Broadcast failed (non-critical): {e}")

    # ── Position Management ──

    async def manage_position(self):
        """Monitor and manage open position with trailing stops."""
        if not self.position:
            return

        pos = self.position
        log.info(f"Managing position: {pos.direction}")

        async with aiohttp.ClientSession() as session:
            while self.position:
                now_et = datetime.now(ET)
                if now_et.hour >= 15 and now_et.minute >= 55:
                    await self._exit_position(session, "EOD")
                    break

                price_0dte = await self.get_quote(session, pos.symbol_0dte) or 0
                price_1dte = await self.get_quote(session, pos.symbol_1dte) or 0

                if price_0dte == 0 and price_1dte == 0:
                    await asyncio.sleep(10)
                    continue

                total_entry = (pos.entry_price_0dte * pos.qty_0dte +
                              pos.entry_price_1dte * pos.qty_1dte)
                total_current = (price_0dte * pos.qty_0dte +
                                price_1dte * pos.qty_1dte)
                pnl_pct = (total_current - total_entry) / total_entry if total_entry > 0 else 0

                if pnl_pct > pos.high_water:
                    pos.high_water = pnl_pct

                for threshold, trail in cfg.TRAIL_LEVELS:
                    if pos.high_water >= threshold:
                        new_stop = trail
                        if new_stop > pos.stop_pct:
                            log.info(f"Trailing stop updated: {pos.stop_pct:.0%} → {new_stop:.0%}")
                            pos.stop_pct = new_stop

                if pnl_pct <= pos.stop_pct:
                    await self._exit_position(session, f"STOP ({pos.stop_pct:.0%})")
                    break

                log.debug(f"P&L: {pnl_pct:+.1%} | HW: {pos.high_water:+.1%} | Stop: {pos.stop_pct:.0%}")
                await asyncio.sleep(15)

    async def _exit_position(self, session: aiohttp.ClientSession, reason: str):
        """Close all position legs across all accounts."""
        pos = self.position
        if not pos:
            return

        log.info(f"Exiting position: {reason}")

        # Multi-account exit — close each account's positions separately
        if pos.account_lots:
            for lot in pos.account_lots:
                acct_id = lot["account"]
                acct_token = lot["token"]
                acct_name = lot["name"]
                if lot["qty_0dte"] > 0:
                    log.info(f"Closing [{acct_name}] {lot['qty_0dte']}x 0DTE")
                    await self.place_order(session, pos.symbol_0dte, lot["qty_0dte"],
                                           "sell_to_close", account=acct_id, token=acct_token)
                if lot["qty_1dte"] > 0:
                    log.info(f"Closing [{acct_name}] {lot['qty_1dte']}x 1DTE")
                    await self.place_order(session, pos.symbol_1dte, lot["qty_1dte"],
                                           "sell_to_close", account=acct_id, token=acct_token)
        else:
            # Fallback: old behavior (single account)
            if pos.qty_0dte > 0:
                await self.place_order(session, pos.symbol_0dte, pos.qty_0dte, "sell_to_close")
            if pos.qty_1dte > 0:
                await self.place_order(session, pos.symbol_1dte, pos.qty_1dte, "sell_to_close")

        price_0dte = await self.get_quote(session, pos.symbol_0dte) or 0
        price_1dte = await self.get_quote(session, pos.symbol_1dte) or 0
        total_entry = (pos.entry_price_0dte * pos.qty_0dte + pos.entry_price_1dte * pos.qty_1dte)
        total_exit = (price_0dte * pos.qty_0dte + price_1dte * pos.qty_1dte)
        pnl = (total_exit - total_entry) * 100
        pnl_pct = (total_exit - total_entry) / total_entry if total_entry > 0 else 0

        await alerts.exit_executed(pos.direction, pnl, pnl_pct, reason)
        self.position = None


executor = MeridianExecutor()
