"""
Risk Management Module

Enforces trading rules to prevent catastrophic losses.

Critical Rules:
- Max loss per trade: 1-2% of account
- Max daily loss: 3% (circuit breaker)
- Position limits: 5-10% max per ticker
- Defined risk only: No naked options
- Stop loss automation: Executed without override
"""


class RiskManager:
    """
    Enforces risk management rules across all strategies
    """
    
    def __init__(self, account_size, config=None):
        self.account_size = account_size
        self.config = config or self._default_config()
        
        # State tracking
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.positions = {}
        self.circuit_breaker_triggered = False
    
    def _default_config(self):
        """Default risk management configuration"""
        return {
            "max_risk_per_trade_pct": 0.02,  # 2%
            "max_daily_loss_pct": 0.03,  # 3%
            "max_position_pct": 0.10,  # 10%
            "max_trades_per_day": 10,
            "allow_naked_options": False,
        }
    
    def check_trade_allowed(self, strategy_name, risk_amount):
        """
        Verify if trade meets risk management rules
        
        Returns: (allowed: bool, reason: str)
        """
        # Check circuit breaker
        if self.circuit_breaker_triggered:
            return False, "Daily loss limit hit - circuit breaker active"
        
        # Check daily loss
        if abs(self.daily_pnl) >= (self.account_size * self.config["max_daily_loss_pct"]):
            self.circuit_breaker_triggered = True
            return False, "Daily loss limit reached"
        
        # Check trade risk
        max_risk = self.account_size * self.config["max_risk_per_trade_pct"]
        if risk_amount > max_risk:
            return False, f"Trade risk ${risk_amount:.2f} exceeds max ${max_risk:.2f}"
        
        # Check trade count
        if self.trades_today >= self.config["max_trades_per_day"]:
            return False, "Max trades per day reached"
        
        return True, "Trade approved"
    
    def update_position(self, ticker, position_value):
        """Track position sizes per ticker"""
        self.positions[ticker] = position_value
        
        # Check position limit
        max_position = self.account_size * self.config["max_position_pct"]
        if position_value > max_position:
            return False, f"Position size exceeds limit: ${position_value:.2f} > ${max_position:.2f}"
        
        return True, "Position within limits"
    
    def update_daily_pnl(self, pnl):
        """Update daily P&L and check limits"""
        self.daily_pnl += pnl
        
        # Trigger circuit breaker if needed
        if abs(self.daily_pnl) >= (self.account_size * self.config["max_daily_loss_pct"]):
            self.circuit_breaker_triggered = True
            return False, "Circuit breaker triggered"
        
        return True, "P&L within limits"
    
    def increment_trade_count(self):
        """Track number of trades today"""
        self.trades_today += 1
    
    def reset_daily_state(self):
        """Reset daily tracking (call at market open)"""
        self.daily_pnl = 0.0
        self.trades_today = 0
        self.circuit_breaker_triggered = False
    
    def get_position_size(self, risk_amount, stop_distance):
        """
        Calculate position size based on risk and stop distance
        
        Args:
            risk_amount: Max $ to risk on trade
            stop_distance: Distance to stop loss in $
        
        Returns: Number of contracts
        """
        if stop_distance <= 0:
            return 0
        
        contracts = int(risk_amount / stop_distance)
        return max(1, contracts)  # Minimum 1 contract
    
    def validate_spread(self, spread_type, long_strike, short_strike):
        """
        Validate spread is defined risk
        
        Args:
            spread_type: "call" or "put"
            long_strike: Long option strike
            short_strike: Short option strike
        
        Returns: (valid: bool, reason: str)
        """
        if self.config["allow_naked_options"]:
            return True, "Naked options allowed"
        
        # Must have both legs
        if long_strike is None or short_strike is None:
            return False, "Naked options not allowed - must be spread"
        
        # Validate spread direction
        if spread_type == "call":
            if short_strike <= long_strike:
                return False, "Invalid call spread: short must be > long"
        elif spread_type == "put":
            if short_strike >= long_strike:
                return False, "Invalid put spread: short must be < long"
        else:
            return False, f"Unknown spread type: {spread_type}"
        
        return True, "Valid spread"


# Example usage
if __name__ == "__main__":
    rm = RiskManager(account_size=100000)
    
    # Check trade
    allowed, reason = rm.check_trade_allowed("test_strategy", 2000)
    print(f"Trade allowed: {allowed} - {reason}")
    
    # Validate spread
    valid, reason = rm.validate_spread("call", long_strike=4100, short_strike=4110)
    print(f"Spread valid: {valid} - {reason}")
