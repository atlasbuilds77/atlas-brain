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
from meridian_db import (
    log_trade_entry, log_trade_exit,
    save_order, check_existing_order, update_order_fill
)

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
    # Profit milestone tracking for scaling exits
    scale_30_hit: bool = False
    scale_50_hit: bool = False
    scale_75_hit: bool = False
    scale_100_hit: bool = False


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
                                   account: str, token: str) -> dict:
        """
        Get detailed account balance including buying power.
        
        Returns:
            {
                "total_equity": float,
                "cash_available": float,
                "option_buying_power": float,
                "unsettled_funds": float,
            }
        """
        url = f"{self.base}/v1/accounts/{account}/balances"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    log.warning(f"Balance API {resp.status} for {account}")
                    return {
                        "total_equity": 0.0,
                        "cash_available": 0.0,
                        "option_buying_power": 0.0,
                        "unsettled_funds": 0.0,
                    }
                data = await resp.json()
                bal = data.get("balances", {})
                
                # Extract all relevant balance fields
                total_equity = float(bal.get("total_equity") or bal.get("total_cash") or bal.get("equity") or 0)
                
                # Get cash details
                cash = bal.get("cash", {})
                cash_available = float(cash.get("cash_available", 0))
                unsettled_funds = float(cash.get("unsettled_funds", 0))
                
                # Option buying power
                option_bp = float(bal.get("option_buying_power", 0))
                
                # Fallback: if cash_available is 0 but total_cash exists, use it
                if cash_available == 0 and bal.get("total_cash"):
                    cash_available = float(bal.get("total_cash", 0))
                
                log.info(f"[{account}] Balance: equity=${total_equity:.2f}, "
                         f"available=${cash_available:.2f}, unsettled=${unsettled_funds:.2f}, "
                         f"option_bp=${option_bp:.2f}")
                
                return {
                    "total_equity": total_equity,
                    "cash_available": cash_available,
                    "option_buying_power": option_bp,
                    "unsettled_funds": unsettled_funds,
                }
        except Exception as e:
            log.warning(f"Balance fetch exception for {account}: {e}")
            return {
                "total_equity": 0.0,
                "cash_available": 0.0,
                "option_buying_power": 0.0,
                "unsettled_funds": 0.0,
            }

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

                # Get detailed balance (including buying power)
                balance_info = await self.get_account_balance(session, acct_id, acct_token)
                equity = balance_info["total_equity"]
                cash_available = balance_info["cash_available"]
                unsettled_funds = balance_info["unsettled_funds"]
                option_bp = balance_info["option_buying_power"]
                
                if equity <= 0:
                    if fallback_eq > 0:
                        log.warning(f"[{acct_name}] API equity=0, using hardwired fallback=${fallback_eq:.2f}")
                        equity = fallback_eq
                        # Also set cash_available to fallback if it's 0
                        if cash_available == 0:
                            cash_available = fallback_eq
                    else:
                        log.error(f"[{acct_name}] No equity and no fallback — skipping")
                        continue

                # Position sizing based on AVAILABLE CASH (not total equity)
                budget = cash_available * size_pct
                budget_0dte = budget * cfg.POSITION_0DTE_PCT
                budget_1dte = budget * cfg.POSITION_1DTE_PCT

                log.info(f"[{acct_name}] Position sizing from available cash (not equity)")
                log.info(f"[{acct_name}]   Cash available: ${cash_available:.2f}")
                log.info(f"[{acct_name}]   Size %: {size_pct*100:.0f}%")
                log.info(f"[{acct_name}]   Budget: ${budget:.2f}")

                qty_0 = max(1, int(budget_0dte / (ask_0dte * 100)))
                qty_1 = max(1, int(budget_1dte / (ask_1dte * 100)))
                
                # ── BUYING POWER PRE-FLIGHT CHECK ──
                cost_0dte = ask_0dte * qty_0 * 100
                cost_1dte = ask_1dte * qty_1 * 100
                total_cost = cost_0dte + cost_1dte
                
                # Use available cash (NOT total equity) - this is the key fix
                buying_power = cash_available if cash_available > 0 else option_bp
                
                log.info(f"[{acct_name}] Checking buying power...")
                log.info(f"[{acct_name}]   Available: ${buying_power:.2f} | Unsettled: ${unsettled_funds:.2f} | Need: ${total_cost:.2f}")
                
                if buying_power < total_cost:
                    # INSUFFICIENT BUYING POWER - SKIP THIS ACCOUNT
                    shortage = total_cost - buying_power
                    log.warning(f"[{acct_name}] 🚫 Insufficient buying power - skipping order")
                    log.info(f"[{acct_name}]   Short by: ${shortage:.2f}")
                    log.info(f"[{acct_name}]   Total equity: ${equity:.2f} (includes unsettled)")
                    
                    # Log skipped trade to database
                    try:
                        setup_name = f"PM {'LOW' if sweep.level < price else 'HIGH'} Sweep"
                        skip_reason = f"Insufficient buying power: ${buying_power:.2f} available, ${total_cost:.2f} needed (unsettled: ${unsettled_funds:.2f})"
                        
                        # Log as skipped entry
                        log_trade_entry(
                            account_number=acct_id,
                            symbol=cfg.SYMBOL,
                            direction=sweep.direction,
                            asset_type="option",
                            strike=float(strike_0dte["strike"]),
                            expiry=exp_0dte,
                            entry_price=ask_0dte,
                            quantity=0,  # 0 qty indicates skipped
                            notes=f"SKIPPED: {skip_reason}",
                            setup_type=f"{setup_name} - SKIPPED",
                            entry_reasoning=skip_reason,
                            status="skipped"  # Mark as skipped in database
                        )
                        log.info(f"[{acct_name}] 📝 Logged skipped trade to database")
                    except Exception as e:
                        log.warning(f"[{acct_name}] Failed to log skipped trade: {e}")
                    
                    # Skip this account, continue to next
                    continue
                
                # SUCCESS - Buying power check passed
                margin = buying_power - total_cost
                log.info(f"[{acct_name}]   ✅ Buying power check PASSED | Margin: ${margin:.2f}")
                log.info(f"[{acct_name}]   Total equity: ${equity:.2f} (reference only)")
                log.info(f"[{acct_name}]   Order: {qty_0}x 0DTE + {qty_1}x 1DTE")

                # ── Log trades to database FIRST (to get trade_id) ──
                trade_id_0dte = None
                trade_id_1dte = None
                
                try:
                    # Build entry reasoning
                    setup_name = f"PM {'LOW' if sweep.level < price else 'HIGH'} Sweep"
                    entry_reasoning = f"""
{setup_name} + {'Reclaim' if sweep.direction == 'bull' else 'Rejection'}

Entry Signal:
- Swept level: ${sweep.level:.2f}
- Direction: {sweep.direction.upper()} ({opt_type})
- Current price: ${price:.2f}

Risk Management:
- Stop loss: -50% (${ask_0dte * 0.5:.2f} for 0DTE)
- Target: GEX cluster
- VIX regime: Monitor volatility

Setup detected by Meridian scanner at {datetime.now(ET).strftime('%H:%M:%S ET')}
                    """.strip()
                    
                    # Log 0DTE trade (get trade_id)
                    trade_id_0dte = log_trade_entry(
                        account_number=acct_id,
                        symbol=cfg.SYMBOL,
                        direction=sweep.direction,
                        asset_type="option",
                        strike=float(strike_0dte["strike"]),
                        expiry=exp_0dte,
                        entry_price=ask_0dte,
                        quantity=qty_0,
                        notes=f"0DTE {opt_type} entry | sweep_level={sweep.level}",
                        stop_loss=ask_0dte * 0.5,  # -50% stop
                        take_profit=None,  # Will be determined by GEX levels
                        entry_reasoning=entry_reasoning,
                        setup_type=f"{setup_name} + {'Reclaim' if sweep.direction == 'bull' else 'Rejection'}"
                    )
                    
                    # Log 1DTE trade (get trade_id)
                    trade_id_1dte = log_trade_entry(
                        account_number=acct_id,
                        symbol=cfg.SYMBOL,
                        direction=sweep.direction,
                        asset_type="option",
                        strike=float(strike_1dte["strike"]),
                        expiry=exp_1dte,
                        entry_price=ask_1dte,
                        quantity=qty_1,
                        notes=f"1DTE {opt_type} entry | sweep_level={sweep.level}",
                        stop_loss=ask_1dte * 0.5,  # -50% stop
                        take_profit=None,  # Will be determined by GEX levels
                        entry_reasoning=entry_reasoning,
                        setup_type=f"{setup_name} + {'Reclaim' if sweep.direction == 'bull' else 'Rejection'}"
                    )
                    
                    log.info(f"[{acct_name}] Trade entries logged: 0DTE trade_id={trade_id_0dte}, 1DTE trade_id={trade_id_1dte}")
                except Exception as e:
                    log.warning(f"Failed to log trade entry for {acct_name}: {e}")

                # ── Check for existing orders (DUPLICATE PREVENTION) ──
                log.info(f"[{acct_name}] Checking for existing orders...")
                
                existing_0dte = None
                existing_1dte = None
                
                if trade_id_0dte:
                    existing_0dte = check_existing_order(trade_id_0dte, sym_0dte, "buy_to_open")
                if trade_id_1dte:
                    existing_1dte = check_existing_order(trade_id_1dte, sym_1dte, "buy_to_open")
                
                # ── Place orders (only if they don't exist) ──
                oid_0 = None
                oid_1 = None
                
                if existing_0dte:
                    log.warning(f"[{acct_name}] 🚫 Order already exists for 0DTE, skipping duplicate (order_id={existing_0dte['order_id']})")
                    oid_0 = existing_0dte['order_id']
                else:
                    log.info(f"[{acct_name}] ✅ No existing order, placing new 0DTE order...")
                    oid_0 = await self.place_order(session, sym_0dte, qty_0, account=acct_id, token=acct_token)
                    if oid_0 and trade_id_0dte:
                        save_order(trade_id_0dte, oid_0, acct_id, cfg.SYMBOL, sym_0dte, "buy_to_open", qty_0)
                        log.info(f"[{acct_name}] 📝 Saved order to database: order_id={oid_0}")
                
                if existing_1dte:
                    log.warning(f"[{acct_name}] 🚫 Order already exists for 1DTE, skipping duplicate (order_id={existing_1dte['order_id']})")
                    oid_1 = existing_1dte['order_id']
                else:
                    log.info(f"[{acct_name}] ✅ No existing order, placing new 1DTE order...")
                    oid_1 = await self.place_order(session, sym_1dte, qty_1, account=acct_id, token=acct_token)
                    if oid_1 and trade_id_1dte:
                        save_order(trade_id_1dte, oid_1, acct_id, cfg.SYMBOL, sym_1dte, "buy_to_open", qty_1)
                        log.info(f"[{acct_name}] 📝 Saved order to database: order_id={oid_1}")
                
                all_order_ids.extend([oid_0, oid_1])
                total_qty_0dte += qty_0
                total_qty_1dte += qty_1
                account_lots.append({
                    "name": acct_name, "account": acct_id, "token": acct_token,
                    "qty_0dte": qty_0, "qty_1dte": qty_1,
                    "trade_id_0dte": trade_id_0dte, "trade_id_1dte": trade_id_1dte,
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
        log.info(f"Managing position: {pos.direction} | {pos.qty_0dte} 0DTE + {pos.qty_1dte} 1DTE")
        log.info(f"Scaling milestones: 30%→1/3, 50%→1/2, 75%→2/3, 100%→ALL")

        try:
            async with aiohttp.ClientSession() as session:
              while self.position:
                now_et = datetime.now(ET)
                
                # ── Smart Trade Window Close ──
                # Hard cutoff: 10:45 AM ET (7:45 AM PT) - must exit by then
                # Smart window: 10:28 AM ET (7:28 AM PT) - check if profitable & trending
                if now_et.hour >= cfg.TRADE_END_HOUR:
                    if now_et.minute >= 45:
                        # Hard stop - close everything
                        await self._exit_position(session, "TRADE_WINDOW_HARD_CLOSE")
                        break
                    elif now_et.minute >= 28:
                        # Smart window - check P&L and momentum
                        price_0dte = await self.get_quote(session, pos.symbol_0dte) or 0
                        price_1dte = await self.get_quote(session, pos.symbol_1dte) or 0
                        
                        if price_0dte > 0 and price_1dte > 0:
                            total_entry = (pos.entry_price_0dte * pos.qty_0dte +
                                          pos.entry_price_1dte * pos.qty_1dte)
                            total_current = (price_0dte * pos.qty_0dte +
                                            price_1dte * pos.qty_1dte)
                            pnl_pct = (total_current - total_entry) / total_entry if total_entry > 0 else 0
                            
                            # If profitable and moving toward target, let it run until 7:45 AM
                            if pnl_pct > 0.20:  # At least +20% profit
                                log.info(f"Smart window: +{pnl_pct:.1%} profit, letting position run until 10:45 AM ET")
                                # Continue managing - will hit hard stop at 10:45 or stop loss
                            else:
                                # Not profitable enough or losing - close now
                                await self._exit_position(session, f"TRADE_WINDOW_CLOSE (P&L {pnl_pct:+.1%})")
                                break
                        else:
                            # Can't get quotes - close to be safe
                            await self._exit_position(session, "TRADE_WINDOW_CLOSE (no quotes)")
                            break
                
                # End of day close
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

                # ── SCALING EXITS AT PROFIT MILESTONES ──
                # +30% = 1/3 off, +50% = half off, +75% = 2/3 off, +100% = all off
                
                try:
                    if pnl_pct >= 1.00 and not pos.scale_100_hit:
                        # +100%: Exit ALL remaining contracts
                        log.info(f"🎯 PROFIT TARGET: +{pnl_pct:.1%} - Closing ALL remaining position")
                        await alerts.send(f"🎯 <b>SCALE EXIT +100%</b> | P&L: +{pnl_pct:.1%} | Closing ALL")
                        await self._scale_exit(session, pos, 1.0, reason="SCALE_100")
                        pos.scale_100_hit = True
                        break  # Exit fully
                        
                    elif pnl_pct >= 0.75 and not pos.scale_75_hit:
                        # +75%: Exit 2/3 of original position
                        log.info(f"🎯 PROFIT MILESTONE: +{pnl_pct:.1%} - Scaling 2/3 off (locking profit)")
                        await alerts.send(f"🎯 <b>SCALE EXIT +75%</b> | P&L: +{pnl_pct:.1%} | Selling 2/3")
                        await self._scale_exit(session, pos, 2.0/3.0, reason="SCALE_75")
                        pos.scale_75_hit = True
                        pos.stop_pct = max(pos.stop_pct, 0.50)  # Raise stop to +50%
                        
                    elif pnl_pct >= 0.50 and not pos.scale_50_hit:
                        # +50%: Exit half of original position
                        log.info(f"🎯 PROFIT MILESTONE: +{pnl_pct:.1%} - Scaling half off (locking profit)")
                        await alerts.send(f"🎯 <b>SCALE EXIT +50%</b> | P&L: +{pnl_pct:.1%} | Selling 1/2")
                        await self._scale_exit(session, pos, 0.5, reason="SCALE_50")
                        pos.scale_50_hit = True
                        pos.stop_pct = max(pos.stop_pct, 0.25)  # Raise stop to +25%
                        
                    elif pnl_pct >= 0.30 and not pos.scale_30_hit:
                        # +30%: Exit 1/3 of original position
                        log.info(f"🎯 PROFIT MILESTONE: +{pnl_pct:.1%} - Scaling 1/3 off (locking profit)")
                        await alerts.send(f"🎯 <b>SCALE EXIT +30%</b> | P&L: +{pnl_pct:.1%} | Selling 1/3")
                        await self._scale_exit(session, pos, 1.0/3.0, reason="SCALE_30")
                        pos.scale_30_hit = True
                        pos.stop_pct = max(pos.stop_pct, 0.0)  # Raise stop to breakeven
                except Exception as e:
                    log.error(f"❌ Scale exit FAILED: {e}", exc_info=True)

                # ── TRAILING STOP (Safety net below milestones) ──
                for threshold, trail in cfg.TRAIL_LEVELS:
                    if pos.high_water >= threshold:
                        new_stop = trail
                        if new_stop > pos.stop_pct:
                            log.info(f"Trailing stop updated: {pos.stop_pct:.0%} → {new_stop:.0%}")
                            pos.stop_pct = new_stop

                if pnl_pct <= pos.stop_pct:
                    await self._exit_position(session, f"STOP ({pos.stop_pct:.0%})")
                    break

                log.info(f"P&L: {pnl_pct:+.1%} | HW: {pos.high_water:+.1%} | Stop: {pos.stop_pct:.0%} | Qty: {pos.qty_0dte}+{pos.qty_1dte}")
                await asyncio.sleep(15)
        except Exception as e:
            log.error(f"❌ manage_position CRASHED: {e}", exc_info=True)
            await alerts.send(f"🚨 <b>POSITION MONITOR CRASHED</b>\n{e}\nManual exit may be needed!")

    async def _scale_exit(self, session: aiohttp.ClientSession, pos: Position, 
                          scale_fraction: float, reason: str):
        """
        Partial exit: sell scale_fraction of ORIGINAL position.
        
        Example:
            - Original: 38 contracts 0DTE, 4 contracts 1DTE
            - scale_fraction=0.33 (1/3): Sell 13 0DTE, 1 1DTE
            - scale_fraction=0.50 (1/2): Sell 19 0DTE, 2 1DTE
        
        This tracks cumulative exits so we don't oversell.
        """
        if not pos or not pos.account_lots:
            return
            
        log.info(f"📊 Scaling exit: {scale_fraction:.1%} of original position ({reason})")
        
        # For each account, calculate what fraction to sell
        for lot in pos.account_lots:
            acct_id = lot["account"]
            acct_token = lot["token"]
            acct_name = lot["name"]
            
            # Get ORIGINAL quantities (at entry)
            original_0dte = lot.get("original_qty_0dte", lot["qty_0dte"])
            original_1dte = lot.get("original_qty_1dte", lot["qty_1dte"])
            
            # Store original if not set
            if "original_qty_0dte" not in lot:
                lot["original_qty_0dte"] = lot["qty_0dte"]
            if "original_qty_1dte" not in lot:
                lot["original_qty_1dte"] = lot["qty_1dte"]
            
            # Calculate target total sold (cumulative)
            target_sold_0dte = int(original_0dte * scale_fraction)
            target_sold_1dte = int(original_1dte * scale_fraction)
            
            # Calculate how much we've already sold
            already_sold_0dte = original_0dte - lot["qty_0dte"]
            already_sold_1dte = original_1dte - lot["qty_1dte"]
            
            # Calculate how much MORE to sell now
            to_sell_0dte = max(0, target_sold_0dte - already_sold_0dte)
            to_sell_1dte = max(0, target_sold_1dte - already_sold_1dte)
            
            if to_sell_0dte > 0:
                log.info(f"[{acct_name}] Selling {to_sell_0dte}x 0DTE (keeping {lot['qty_0dte'] - to_sell_0dte})")
                await self.place_order(session, pos.symbol_0dte, to_sell_0dte,
                                      "sell_to_close", account=acct_id, token=acct_token)
                lot["qty_0dte"] -= to_sell_0dte
                pos.qty_0dte -= to_sell_0dte
                
            if to_sell_1dte > 0:
                log.info(f"[{acct_name}] Selling {to_sell_1dte}x 1DTE (keeping {lot['qty_1dte'] - to_sell_1dte})")
                await self.place_order(session, pos.symbol_1dte, to_sell_1dte,
                                      "sell_to_close", account=acct_id, token=acct_token)
                lot["qty_1dte"] -= to_sell_1dte
                pos.qty_1dte -= to_sell_1dte
        
        log.info(f"✅ Scale exit complete - Position now: {pos.qty_0dte} 0DTE, {pos.qty_1dte} 1DTE")

    async def _verify_position_exists(self, session: aiohttp.ClientSession,
                                       account: str, token: str, symbol: str) -> int:
        """
        Verify position actually exists before attempting to close.
        Returns actual quantity held, or 0 if position doesn't exist.
        """
        url = f"{self.base}/v1/accounts/{account}/positions"
        headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
        try:
            async with session.get(url, headers=headers) as resp:
                if resp.status != 200:
                    return 0
                data = await resp.json()
                if 'positions' not in data or data['positions'] == 'null':
                    return 0
                positions = data['positions'].get('position', [])
                if not isinstance(positions, list):
                    positions = [positions]
                
                for pos in positions:
                    if pos.get('symbol') == symbol:
                        return int(pos.get('quantity', 0))
                return 0
        except Exception as e:
            log.warning(f"Failed to verify position for {symbol}: {e}")
            return 0

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
                
                # VERIFY positions actually exist before closing
                actual_qty_0dte = await self._verify_position_exists(
                    session, acct_id, acct_token, pos.symbol_0dte
                )
                actual_qty_1dte = await self._verify_position_exists(
                    session, acct_id, acct_token, pos.symbol_1dte
                )
                
                if actual_qty_0dte > 0:
                    log.info(f"Closing [{acct_name}] {actual_qty_0dte}x 0DTE (verified)")
                    await self.place_order(session, pos.symbol_0dte, actual_qty_0dte,
                                           "sell_to_close", account=acct_id, token=acct_token)
                elif lot["qty_0dte"] > 0:
                    log.warning(f"[{acct_name}] 0DTE position already closed externally (expected {lot['qty_0dte']}, found 0)")
                
                if actual_qty_1dte > 0:
                    log.info(f"Closing [{acct_name}] {actual_qty_1dte}x 1DTE (verified)")
                    await self.place_order(session, pos.symbol_1dte, actual_qty_1dte,
                                           "sell_to_close", account=acct_id, token=acct_token)
                elif lot["qty_1dte"] > 0:
                    log.warning(f"[{acct_name}] 1DTE position already closed externally (expected {lot['qty_1dte']}, found 0)")
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

        # ── Log trade exits to database ──
        # Parse option symbols to extract strike and expiry
        # Option symbol format: QQQ260221C00500000 (SYMBOL-YYMMDD-C/P-STRIKE*1000)
        try:
            # Extract strike and expiry from 0DTE symbol
            sym_0 = pos.symbol_0dte
            expiry_0dte = f"20{sym_0[3:5]}-{sym_0[5:7]}-{sym_0[7:9]}"  # YYMMDD -> YYYY-MM-DD
            strike_0dte = float(sym_0[10:]) / 1000  # Strike * 1000 -> actual strike
            
            # Extract strike and expiry from 1DTE symbol
            sym_1 = pos.symbol_1dte
            expiry_1dte = f"20{sym_1[3:5]}-{sym_1[5:7]}-{sym_1[7:9]}"
            strike_1dte = float(sym_1[10:]) / 1000
            
            # Log exits for each account
            if pos.account_lots:
                for lot in pos.account_lots:
                    acct_id = lot["account"]
                    acct_name = lot["name"]
                    
                    try:
                        # Update 0DTE trade
                        if lot["qty_0dte"] > 0:
                            log_trade_exit(
                                account_number=acct_id,
                                symbol=cfg.SYMBOL,
                                strike=strike_0dte,
                                expiry=expiry_0dte,
                                exit_price=price_0dte,
                                notes=reason
                            )
                        
                        # Update 1DTE trade
                        if lot["qty_1dte"] > 0:
                            log_trade_exit(
                                account_number=acct_id,
                                symbol=cfg.SYMBOL,
                                strike=strike_1dte,
                                expiry=expiry_1dte,
                                exit_price=price_1dte,
                                notes=reason
                            )
                    except Exception as e:
                        log.warning(f"Failed to log trade exit for {acct_name}: {e}")
                        
        except Exception as e:
            log.warning(f"Failed to parse option symbols for trade exit logging: {e}")

        await alerts.exit_executed(pos.direction, pnl, pnl_pct, reason)
        self.position = None


executor = MeridianExecutor()
