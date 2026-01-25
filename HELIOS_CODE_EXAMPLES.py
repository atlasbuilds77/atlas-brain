"""
HELIOS SCALPING SYSTEM - CODE EXAMPLES
Based on Robinhood API Reverse Engineering

This file contains production-ready code examples for implementing
the Helios options scalping system targeting SPY/QQQ 0DTE options.
"""

import asyncio
import json
import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum
import websockets
import aiohttp


# ============================================================================
# DATA MODELS (Based on Robinhood API structures)
# ============================================================================

class OrderType(Enum):
    LIMIT = "limit"
    MARKET = "market"
    STOP_LIMIT = "stop_limit"


class TimeInForce(Enum):
    IOC = "ioc"  # Immediate-or-Cancel (best for entries)
    GTC = "gtc"  # Good-Til-Canceled (best for exits)
    DAY = "day"
    FOK = "fok"  # Fill-or-Kill


class PositionEffect(Enum):
    OPEN = "open"
    CLOSE = "close"


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderDirection(Enum):
    DEBIT = "debit"
    CREDIT = "credit"


@dataclass
class OptionLeg:
    option_url: str
    side: OrderSide
    position_effect: PositionEffect
    ratio_quantity: int = 1


@dataclass
class OptionOrderRequest:
    account_url: str
    legs: List[OptionLeg]
    type: OrderType
    price: Decimal
    quantity: int
    time_in_force: TimeInForce
    trigger: str = "immediate"
    direction: OrderDirection = None
    override_day_trade_checks: bool = False
    override_dtbp_checks: bool = False


@dataclass
class OptionInstrument:
    id: uuid.UUID
    url: str
    chain_id: uuid.UUID
    chain_symbol: str
    expiration_date: date
    strike_price: Decimal
    type: str  # "call" or "put"
    tradability_symbol: str  # e.g., "SPY 260123C00500000"


@dataclass
class OptionQuote:
    instrument_id: uuid.UUID
    bid_price: Decimal
    ask_price: Decimal
    bid_size: int
    ask_size: int
    last_trade_price: Decimal
    mark_price: Decimal
    timestamp: datetime


# ============================================================================
# ROBINHOOD API CLIENT
# ============================================================================

class RobinhoodOptionsAPI:
    """
    REST API client for Robinhood options trading.
    Based on reverse-engineered OptionsApi.java
    """
    
    BASE_URL = "https://api.robinhood.com"
    
    def __init__(self, auth_token: str, account_number: str):
        self.auth_token = auth_token
        self.account_number = account_number
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={
                "Authorization": f"Bearer {self.auth_token}",
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def submit_option_order(self, order_request: OptionOrderRequest) -> Dict:
        """
        Submit options order (primary endpoint for scalping).
        Endpoint: POST /options/orders/
        """
        url = f"{self.BASE_URL}/options/orders/"
        
        # Convert to API format
        payload = {
            "account": order_request.account_url,
            "legs": [
                {
                    "option": leg.option_url,
                    "side": leg.side.value,
                    "position_effect": leg.position_effect.value,
                    "ratio_quantity": leg.ratio_quantity
                }
                for leg in order_request.legs
            ],
            "type": order_request.type.value,
            "price": str(order_request.price),
            "quantity": order_request.quantity,
            "time_in_force": order_request.time_in_force.value,
            "trigger": order_request.trigger,
            "direction": order_request.direction.value if order_request.direction else None,
            "override_day_trade_checks": order_request.override_day_trade_checks,
            "override_dtbp_checks": order_request.override_dtbp_checks
        }
        
        # Extended timeout for order submission (from reverse engineering)
        timeout = aiohttp.ClientTimeout(total=25)
        
        async with self.session.post(url, json=payload, timeout=timeout) as resp:
            resp.raise_for_status()
            return await resp.json()
    
    async def replace_option_order(
        self, 
        order_id: uuid.UUID, 
        new_order_request: OptionOrderRequest
    ) -> Dict:
        """
        Replace existing order (FASTER than cancel + submit).
        Endpoint: PATCH /options/orders/{orderId}/
        """
        url = f"{self.BASE_URL}/options/orders/{order_id}/"
        
        payload = {
            "account": new_order_request.account_url,
            "legs": [
                {
                    "option": leg.option_url,
                    "side": leg.side.value,
                    "position_effect": leg.position_effect.value,
                    "ratio_quantity": leg.ratio_quantity
                }
                for leg in new_order_request.legs
            ],
            "type": new_order_request.type.value,
            "price": str(new_order_request.price),
            "quantity": new_order_request.quantity,
            "time_in_force": new_order_request.time_in_force.value,
            "trigger": new_order_request.trigger,
            "direction": new_order_request.direction.value if new_order_request.direction else None
        }
        
        timeout = aiohttp.ClientTimeout(total=25)
        
        async with self.session.patch(url, json=payload, timeout=timeout) as resp:
            resp.raise_for_status()
            return await resp.json()
    
    async def cancel_option_order(self, order_id: uuid.UUID) -> None:
        """
        Cancel options order.
        Endpoint: POST /options/orders/{orderId}/cancel/
        """
        url = f"{self.BASE_URL}/options/orders/{order_id}/cancel/"
        
        async with self.session.post(url, json={}) as resp:
            resp.raise_for_status()
    
    async def get_option_quote(
        self, 
        instrument_id: uuid.UUID, 
        include_all_sessions: bool = False
    ) -> OptionQuote:
        """
        Get real-time quote for single option.
        Endpoint: GET /marketdata/options/{instrumentId}/
        """
        url = f"{self.BASE_URL}/marketdata/options/{instrument_id}/"
        params = {"include_all_sessions": str(include_all_sessions).lower()}
        
        async with self.session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            
            return OptionQuote(
                instrument_id=uuid.UUID(data["instrument_id"]),
                bid_price=Decimal(data["bid_price"]) if data.get("bid_price") else Decimal("0"),
                ask_price=Decimal(data["ask_price"]) if data.get("ask_price") else Decimal("0"),
                bid_size=int(data.get("bid_size", 0)),
                ask_size=int(data.get("ask_size", 0)),
                last_trade_price=Decimal(data.get("last_trade_price", "0")),
                mark_price=Decimal(data.get("mark_price", "0")),
                timestamp=datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
            )
    
    async def get_active_options_for_chain(
        self,
        chain_id: uuid.UUID,
        option_type: str,
        expiration_date: date,
        page_size: int = 200
    ) -> List[OptionInstrument]:
        """
        Get all active options for a chain (e.g., SPY 0DTE options).
        Endpoint: GET /options/instruments/?state=active
        """
        url = f"{self.BASE_URL}/options/instruments/"
        params = {
            "state": "active",
            "chain_id": str(chain_id),
            "type": option_type,
            "expiration_dates": expiration_date.isoformat(),
            "page_size": page_size
        }
        
        instruments = []
        cursor = None
        
        while True:
            if cursor:
                params["cursor"] = cursor
            
            async with self.session.get(url, params=params) as resp:
                resp.raise_for_status()
                data = await resp.json()
                
                for item in data["results"]:
                    instruments.append(OptionInstrument(
                        id=uuid.UUID(item["id"]),
                        url=item["url"],
                        chain_id=uuid.UUID(item["chain_id"]),
                        chain_symbol=item["chain_symbol"],
                        expiration_date=date.fromisoformat(item["expiration_date"]),
                        strike_price=Decimal(item["strike_price"]),
                        type=item["type"],
                        tradability_symbol=item.get("tradability", {}).get("symbol", "")
                    ))
                
                cursor = data.get("next")
                if not cursor:
                    break
        
        return instruments
    
    async def get_available_contracts(self) -> int:
        """
        Check how many contracts can be purchased (buying power check).
        Endpoint: GET /options/orders/available_contracts/{account_number}/
        """
        url = f"{self.BASE_URL}/options/orders/available_contracts/{self.account_number}/"
        params = {
            "strategy_code": "single_leg"
        }
        
        async with self.session.get(url, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
            return int(data.get("num_of_contracts", 0))


# ============================================================================
# WEBSOCKET CLIENT FOR REAL-TIME DATA
# ============================================================================

class RobinhoodWebsocketClient:
    """
    Websocket client for real-time market data.
    Based on reverse-engineered MdWebsocketSource.java
    """
    
    WS_URL = "wss://api.robinhood.com/"
    
    def __init__(self, auth_token: str, app_version: str = "1.0.0"):
        self.auth_token = auth_token
        self.app_version = app_version
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.subscriptions: Dict[str, asyncio.Queue] = {}
    
    async def connect(self):
        """Connect to websocket and authenticate."""
        self.ws = await websockets.connect(self.WS_URL)
        
        # Send setup message
        await self.send_message({
            "type": "setup",
            "version": self.app_version
        })
        
        # Wait for auth prompt
        response = await self.receive_message()
        
        if response.get("type") == "auth_state" and response.get("state") == "unauthorized":
            # Send auth token
            await self.send_message({
                "type": "auth",
                "token": self.auth_token
            })
            
            # Wait for authorized state
            response = await self.receive_message()
        
        # Open feed channel
        await self.send_message({
            "type": "open_channel",
            "channel": 1  # Feed channel
        })
        
        # Start message processor
        asyncio.create_task(self._process_messages())
        
        # Start keep-alive
        asyncio.create_task(self._keep_alive())
    
    async def subscribe_to_option_quote(self, tradability_symbol: str) -> asyncio.Queue:
        """
        Subscribe to real-time option quote updates.
        Example: tradability_symbol = "SPY 260123C00500000"
        """
        topic_key = f"quote_{tradability_symbol}"
        
        if topic_key not in self.subscriptions:
            self.subscriptions[topic_key] = asyncio.Queue()
            
            # Send subscription message
            await self.send_message({
                "type": "update_feed_subscription",
                "channel": 1,
                "add": [{
                    "type": "equity_quote_qbbo",
                    "symbol": tradability_symbol,
                    "include_quote_params": True,
                    "include_inactive": False,
                    "include_bbo_source": True,
                    "bounds": "regular"
                }]
            })
        
        return self.subscriptions[topic_key]
    
    async def subscribe_to_l2_orderbook(self, symbol: str) -> asyncio.Queue:
        """
        Subscribe to L2 order book for underlying (SPY/QQQ).
        """
        topic_key = f"l2_{symbol}"
        
        if topic_key not in self.subscriptions:
            self.subscriptions[topic_key] = asyncio.Queue()
            
            await self.send_message({
                "type": "update_feed_subscription",
                "channel": 1,
                "add": [{
                    "type": "equity_l2_full",
                    "symbol": symbol,
                    "include_quote_params": True,
                    "include_inactive": False,
                    "include_bbo_source": True,
                    "bounds": "regular"
                }]
            })
        
        return self.subscriptions[topic_key]
    
    async def send_message(self, message: Dict):
        """Send message to websocket."""
        if self.ws:
            await self.ws.send(json.dumps(message))
    
    async def receive_message(self) -> Dict:
        """Receive message from websocket."""
        if self.ws:
            msg = await self.ws.recv()
            return json.loads(msg)
        return {}
    
    async def _process_messages(self):
        """Process incoming messages and route to subscribers."""
        try:
            while self.ws:
                message = await self.receive_message()
                
                if message.get("type") == "feed_data":
                    # Route to appropriate subscription queue
                    symbol = message.get("symbol")
                    data_type = message.get("data_type")
                    
                    if data_type == "quote":
                        topic_key = f"quote_{symbol}"
                    elif data_type == "l2":
                        topic_key = f"l2_{symbol}"
                    else:
                        continue
                    
                    if topic_key in self.subscriptions:
                        await self.subscriptions[topic_key].put(message)
        
        except Exception as e:
            print(f"Websocket error: {e}")
            # Implement reconnection logic here
    
    async def _keep_alive(self):
        """Send keep-alive messages every 30 seconds."""
        while self.ws:
            await asyncio.sleep(30)
            await self.send_message({"type": "keep_alive"})


# ============================================================================
# HELIOS SCALPING ENGINE
# ============================================================================

class HeliosScalpingEngine:
    """
    Main scalping engine for 0DTE options on SPY/QQQ.
    """
    
    def __init__(
        self,
        api_client: RobinhoodOptionsAPI,
        ws_client: RobinhoodWebsocketClient,
        risk_params: Dict
    ):
        self.api = api_client
        self.ws = ws_client
        self.risk_params = risk_params
        self.active_trades: Dict[uuid.UUID, Dict] = {}
    
    async def execute_scalp_trade(
        self,
        option_instrument: OptionInstrument,
        entry_price: Decimal,
        quantity: int,
        side: OrderSide
    ) -> Optional[uuid.UUID]:
        """
        Execute a complete scalping trade with entry and auto exit orders.
        """
        # Step 1: Validate buying power
        available_contracts = await self.api.get_available_contracts()
        if quantity > available_contracts:
            print(f"Insufficient buying power. Requested: {quantity}, Available: {available_contracts}")
            return None
        
        # Step 2: Submit entry order (IOC for immediate execution)
        account_url = f"{self.api.BASE_URL}/accounts/{self.api.account_number}/"
        
        entry_order_request = OptionOrderRequest(
            account_url=account_url,
            legs=[OptionLeg(
                option_url=option_instrument.url,
                side=side,
                position_effect=PositionEffect.OPEN,
                ratio_quantity=1
            )],
            type=OrderType.LIMIT,
            price=entry_price,
            quantity=quantity,
            time_in_force=TimeInForce.IOC,  # Immediate-or-Cancel
            direction=OrderDirection.DEBIT if side == OrderSide.BUY else OrderDirection.CREDIT
        )
        
        try:
            entry_order = await self.api.submit_option_order(entry_order_request)
            order_id = uuid.UUID(entry_order["id"])
            
            print(f"Entry order submitted: {order_id}")
            
            # Step 3: Monitor for fill
            filled_quantity = await self._monitor_order_fill(order_id)
            
            if filled_quantity > 0:
                print(f"Entry filled: {filled_quantity} contracts at {entry_price}")
                
                # Step 4: Submit exit orders
                await self._submit_exit_orders(
                    option_instrument=option_instrument,
                    entry_price=entry_price,
                    quantity=filled_quantity,
                    entry_side=side
                )
                
                return order_id
            else:
                print("Entry order not filled (IOC canceled)")
                return None
        
        except Exception as e:
            print(f"Error executing trade: {e}")
            return None
    
    async def _monitor_order_fill(self, order_id: uuid.UUID, timeout: int = 5) -> int:
        """
        Monitor order until filled or timeout.
        Returns filled quantity.
        """
        start_time = asyncio.get_event_loop().time()
        
        while (asyncio.get_event_loop().time() - start_time) < timeout:
            # Poll order status
            url = f"{self.api.BASE_URL}/options/orders/{order_id}/"
            async with self.api.session.get(url) as resp:
                if resp.status == 200:
                    order_data = await resp.json()
                    state = order_data.get("state")
                    
                    if state == "filled":
                        return int(order_data.get("processed_quantity", 0))
                    elif state in ["cancelled", "rejected", "failed"]:
                        return 0
            
            await asyncio.sleep(0.1)  # Poll every 100ms
        
        return 0
    
    async def _submit_exit_orders(
        self,
        option_instrument: OptionInstrument,
        entry_price: Decimal,
        quantity: int,
        entry_side: OrderSide
    ):
        """
        Submit profit target and stop loss orders.
        """
        # Calculate exit prices
        profit_target_pct = Decimal(str(self.risk_params["profit_target_percent"]))
        stop_loss_pct = Decimal(str(self.risk_params["stop_loss_percent"]))
        
        if entry_side == OrderSide.BUY:
            # Long position
            profit_price = entry_price * (Decimal("1") + profit_target_pct)
            stop_price = entry_price * (Decimal("1") - stop_loss_pct)
            exit_side = OrderSide.SELL
        else:
            # Short position
            profit_price = entry_price * (Decimal("1") - profit_target_pct)
            stop_price = entry_price * (Decimal("1") + stop_loss_pct)
            exit_side = OrderSide.BUY
        
        # Submit profit target (GTC limit order)
        account_url = f"{self.api.BASE_URL}/accounts/{self.api.account_number}/"
        
        profit_order_request = OptionOrderRequest(
            account_url=account_url,
            legs=[OptionLeg(
                option_url=option_instrument.url,
                side=exit_side,
                position_effect=PositionEffect.CLOSE,
                ratio_quantity=1
            )],
            type=OrderType.LIMIT,
            price=profit_price,
            quantity=quantity,
            time_in_force=TimeInForce.GTC,  # Let it rest in the book
            direction=OrderDirection.CREDIT if exit_side == OrderSide.SELL else OrderDirection.DEBIT
        )
        
        try:
            profit_order = await self.api.submit_option_order(profit_order_request)
            print(f"Profit target order submitted: {profit_order['id']} at {profit_price}")
            
            # Note: Stop loss would require manual monitoring or market order
            # Robinhood may not support stop-market for options
            print(f"Monitor stop loss manually at {stop_price}")
            
        except Exception as e:
            print(f"Error submitting exit orders: {e}")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def main():
    """
    Example usage of Helios scalping system.
    """
    # Configuration
    AUTH_TOKEN = "your_robinhood_auth_token_here"
    ACCOUNT_NUMBER = "your_account_number_here"
    SPY_CHAIN_ID = uuid.UUID("your_spy_chain_id_here")  # Get from API
    
    risk_params = {
        "profit_target_percent": 0.20,  # 20% profit target
        "stop_loss_percent": 0.10,      # 10% stop loss
        "max_position_size": 10,        # Max 10 contracts per trade
        "max_daily_trades": 50
    }
    
    # Initialize clients
    async with RobinhoodOptionsAPI(AUTH_TOKEN, ACCOUNT_NUMBER) as api:
        ws = RobinhoodWebsocketClient(AUTH_TOKEN)
        await ws.connect()
        
        # Initialize engine
        engine = HeliosScalpingEngine(api, ws, risk_params)
        
        # Get 0DTE SPY options
        today = date.today()
        spy_options = await api.get_active_options_for_chain(
            chain_id=SPY_CHAIN_ID,
            option_type="call",
            expiration_date=today
        )
        
        print(f"Found {len(spy_options)} 0DTE SPY call options")
        
        # Select ATM option (example)
        spy_quote = await api.get_option_quote(spy_options[0].id)
        atm_strike = spy_options[len(spy_options) // 2]  # Rough ATM
        
        print(f"Selected strike: ${atm_strike.strike_price}")
        
        # Get current quote
        option_quote = await api.get_option_quote(atm_strike.id)
        
        print(f"Current quote - Bid: {option_quote.bid_price}, Ask: {option_quote.ask_price}")
        
        # Calculate entry price (slightly aggressive)
        entry_price = option_quote.ask_price  # Buy at ask for immediate fill
        
        # Execute scalp trade
        trade_id = await engine.execute_scalp_trade(
            option_instrument=atm_strike,
            entry_price=entry_price,
            quantity=5,  # 5 contracts
            side=OrderSide.BUY
        )
        
        if trade_id:
            print(f"Trade executed successfully: {trade_id}")
        else:
            print("Trade failed")
        
        # Keep websocket alive for monitoring
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
