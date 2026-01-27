#!/usr/bin/env python3
"""
Crypto Trading Strategy Calculator
Demonstrates calculations for delta-neutral strategies, funding rate arbitrage, and grid trading
"""

import math
from typing import Dict, List, Tuple

class CryptoStrategyCalculator:
    """Calculator for various crypto trading strategies"""
    
    @staticmethod
    def funding_rate_arbitrage(
        capital: float,
        asset_price: float,
        funding_rate_percent: float,
        interval_hours: int = 8,
        trading_fees_percent: float = 0.04
    ) -> Dict[str, float]:
        """
        Calculate funding rate arbitrage returns
        
        Args:
            capital: Total capital in USD
            asset_price: Price of the asset in USD
            funding_rate_percent: Funding rate as percentage (e.g., 0.03 for 0.03%)
            interval_hours: Funding interval in hours (typically 8)
            trading_fees_percent: Total trading fees as percentage
        
        Returns:
            Dictionary with calculated metrics
        """
        # Convert percentage to decimal
        funding_rate = funding_rate_percent / 100
        
        # Calculate position size (assuming equal allocation to long and short)
        position_size = capital / asset_price
        
        # Daily funding periods
        daily_periods = 24 / interval_hours
        
        # Daily income before fees
        daily_income = position_size * asset_price * funding_rate * daily_periods
        
        # Annual income
        annual_income = daily_income * 365
        
        # Trading fees (enter and exit)
        total_fees = capital * (trading_fees_percent / 100) * 2
        
        # Net returns
        net_annual_income = annual_income - total_fees
        annual_return_percent = (net_annual_income / capital) * 100
        
        return {
            'position_size': position_size,
            'daily_income': daily_income,
            'annual_income': annual_income,
            'trading_fees': total_fees,
            'net_annual_income': net_annual_income,
            'annual_return_percent': annual_return_percent,
            'daily_return_percent': (daily_income / capital) * 100
        }
    
    @staticmethod
    def cash_and_carry_arbitrage(
        spot_price: float,
        futures_price: float,
        days_to_expiry: int,
        position_size: float,
        trading_fees_percent: float = 0.04
    ) -> Dict[str, float]:
        """
        Calculate cash-and-carry arbitrage returns
        
        Args:
            spot_price: Current spot price
            futures_price: Futures contract price
            days_to_expiry: Days until futures expiry
            position_size: Size of position in USD
            trading_fees_percent: Total trading fees as percentage
        
        Returns:
            Dictionary with calculated metrics
        """
        # Calculate premium
        premium = futures_price - spot_price
        premium_percent = (premium / spot_price) * 100
        
        # Gross profit
        gross_profit = (position_size / spot_price) * premium
        
        # Trading fees
        fees = position_size * (trading_fees_percent / 100)
        
        # Net profit
        net_profit = gross_profit - fees
        
        # Returns
        return_percent = (net_profit / position_size) * 100
        annualized_return = return_percent * (365 / days_to_expiry)
        
        return {
            'premium': premium,
            'premium_percent': premium_percent,
            'gross_profit': gross_profit,
            'trading_fees': fees,
            'net_profit': net_profit,
            'return_percent': return_percent,
            'annualized_return': annualized_return
        }
    
    @staticmethod
    def grid_trading_calculator(
        capital: float,
        asset_price: float,
        grid_range_percent: float,
        num_grids: int,
        grid_type: str = 'geometric',
        volatility_percent: float = 2.0,
        trading_fees_percent: float = 0.04
    ) -> Dict[str, float]:
        """
        Calculate grid trading parameters and expected returns
        
        Args:
            capital: Total capital in USD
            asset_price: Current asset price
            grid_range_percent: Total price range as percentage (e.g., 20 for ±10%)
            num_grids: Number of grid levels (buy/sell pairs)
            grid_type: 'geometric' or 'arithmetic'
            volatility_percent: Expected daily volatility as percentage
            trading_fees_percent: Trading fees per transaction
        
        Returns:
            Dictionary with calculated metrics
        """
        # Calculate price range
        range_decimal = grid_range_percent / 100
        lower_price = asset_price * (1 - range_decimal/2)
        upper_price = asset_price * (1 + range_decimal/2)
        
        # Calculate grid spacing
        if grid_type == 'geometric':
            # Geometric grid: equal percentage spacing
            grid_ratio = (upper_price / lower_price) ** (1 / num_grids)
            grid_levels = [lower_price * (grid_ratio ** i) for i in range(num_grids + 1)]
            grid_spacing_percent = (grid_ratio - 1) * 100
        else:
            # Arithmetic grid: equal price spacing
            price_step = (upper_price - lower_price) / num_grids
            grid_levels = [lower_price + i * price_step for i in range(num_grids + 1)]
            grid_spacing_percent = (price_step / asset_price) * 100
        
        # Capital per grid
        capital_per_grid = capital / num_grids
        
        # Expected trades per day (based on volatility)
        daily_volatility = asset_price * (volatility_percent / 100)
        expected_trades_per_day = daily_volatility / (asset_price * (grid_spacing_percent / 100))
        expected_trades_per_day = min(expected_trades_per_day, num_grids * 2)  # Cap at grid capacity
        
        # Profit per trade (before fees)
        if grid_type == 'geometric':
            profit_per_trade = capital_per_grid * (grid_spacing_percent / 100)
        else:
            profit_per_trade = capital_per_grid * grid_spacing_percent / 100
        
        # Daily profit (before fees)
        daily_profit_before_fees = profit_per_trade * expected_trades_per_day
        
        # Account for fees (each trade has buy and sell)
        fees_per_trade = capital_per_grid * (trading_fees_percent / 100) * 2
        daily_profit_after_fees = daily_profit_before_fees - (fees_per_trade * expected_trades_per_day)
        
        # Monthly and annual returns
        monthly_return = (daily_profit_after_fees * 30 / capital) * 100
        annual_return = monthly_return * 12
        
        return {
            'lower_price': lower_price,
            'upper_price': upper_price,
            'grid_levels': grid_levels,
            'grid_spacing_percent': grid_spacing_percent,
            'capital_per_grid': capital_per_grid,
            'expected_trades_per_day': expected_trades_per_day,
            'profit_per_trade': profit_per_trade,
            'daily_profit_before_fees': daily_profit_before_fees,
            'daily_profit_after_fees': daily_profit_after_fees,
            'monthly_return_percent': monthly_return,
            'annual_return_percent': annual_return
        }
    
    @staticmethod
    def protective_put_hedge(
        asset_price: float,
        position_size: float,
        put_strike: float,
        put_premium: float,
        time_to_expiry_days: int
    ) -> Dict[str, float]:
        """
        Calculate protective put hedge parameters
        
        Args:
            asset_price: Current asset price
            position_size: Size of position in USD
            put_strike: Put option strike price
            put_premium: Put option premium in USD
            time_to_expiry_days: Days until option expiry
        
        Returns:
            Dictionary with calculated metrics
        """
        # Number of puts needed (assuming 1 put per asset)
        num_assets = position_size / asset_price
        num_puts = math.ceil(num_assets)
        
        # Total cost of hedge
        hedge_cost = num_puts * put_premium
        hedge_cost_percent = (hedge_cost / position_size) * 100
        
        # Protection level
        protected_price = put_strike
        
        # Maximum loss
        max_loss = (asset_price - put_strike) * num_assets + hedge_cost
        max_loss_percent = (max_loss / position_size) * 100
        
        # Breakeven price
        breakeven_price = asset_price + (hedge_cost / num_assets)
        
        # Annualized hedge cost
        annualized_cost_percent = hedge_cost_percent * (365 / time_to_expiry_days)
        
        return {
            'num_puts_needed': num_puts,
            'hedge_cost': hedge_cost,
            'hedge_cost_percent': hedge_cost_percent,
            'protected_price': protected_price,
            'max_loss': max_loss,
            'max_loss_percent': max_loss_percent,
            'breakeven_price': breakeven_price,
            'annualized_cost_percent': annualized_cost_percent
        }
    
    @staticmethod
    def pairs_trading_metrics(
        price_a: List[float],
        price_b: List[float],
        entry_z_score: float = 2.0,
        exit_z_score: float = 0.5
    ) -> Dict[str, float]:
        """
        Calculate pairs trading metrics
        
        Args:
            price_a: Historical prices of asset A
            price_b: Historical prices of asset B
            entry_z_score: Z-score threshold for entry
            exit_z_score: Z-score threshold for exit
        
        Returns:
            Dictionary with calculated metrics
        """
        import numpy as np
        
        # Calculate hedge ratio (beta) using linear regression
        returns_a = np.diff(np.log(price_a))
        returns_b = np.diff(np.log(price_b))
        
        # Simple OLS regression
        cov_matrix = np.cov(returns_a, returns_b)
        beta = cov_matrix[0, 1] / cov_matrix[0, 0]
        
        # Calculate spread
        spread = []
        for i in range(min(len(price_a), len(price_b))):
            spread.append(price_b[i] - beta * price_a[i])
        
        # Spread statistics
        spread_mean = np.mean(spread)
        spread_std = np.std(spread)
        
        # Current z-score
        current_spread = spread[-1]
        current_z_score = (current_spread - spread_mean) / spread_std
        
        # Trading signal
        if abs(current_z_score) > entry_z_score:
            signal = "TRADE" if current_z_score > 0 else "REVERSE_TRADE"
        elif abs(current_z_score) < exit_z_score:
            signal = "EXIT"
        else:
            signal = "HOLD"
        
        return {
            'hedge_ratio_beta': beta,
            'spread_mean': spread_mean,
            'spread_std': spread_std,
            'current_spread': current_spread,
            'current_z_score': current_z_score,
            'trading_signal': signal,
            'entry_threshold': entry_z_score,
            'exit_threshold': exit_z_score
        }


def main():
    """Example usage of the calculator"""
    calculator = CryptoStrategyCalculator()
    
    print("=" * 60)
    print("CRYPTO TRADING STRATEGY CALCULATOR")
    print("=" * 60)
    
    # Example 1: Funding Rate Arbitrage
    print("\n1. FUNDING RATE ARBITRAGE (ETH Example)")
    print("-" * 40)
    funding_results = calculator.funding_rate_arbitrage(
        capital=50000,
        asset_price=2000,
        funding_rate_percent=0.03,
        trading_fees_percent=0.04
    )
    
    for key, value in funding_results.items():
        if key == 'position_size':
            print(f"{key:25}: {value:.4f} ETH")
        elif 'percent' in key:
            print(f"{key:25}: {value:.2f}%")
        elif 'income' in key or 'fees' in key:
            print(f"{key:25}: ${value:.2f}")
    
    # Example 2: Cash-and-Carry Arbitrage
    print("\n2. CASH-AND-CARRY ARBITRAGE (BTC Example)")
    print("-" * 40)
    carry_results = calculator.cash_and_carry_arbitrage(
        spot_price=30000,
        futures_price=30300,
        days_to_expiry=90,
        position_size=100000,
        trading_fees_percent=0.04
    )
    
    for key, value in carry_results.items():
        if 'percent' in key:
            print(f"{key:25}: {value:.2f}%")
        else:
            print(f"{key:25}: ${value:.2f}")
    
    # Example 3: Grid Trading
    print("\n3. GRID TRADING CALCULATOR (BTC Example)")
    print("-" * 40)
    grid_results = calculator.grid_trading_calculator(
        capital=50000,
        asset_price=30000,
        grid_range_percent=20,  # ±10%
        num_grids=10,
        grid_type='geometric',
        volatility_percent=2.0,
        trading_fees_percent=0.04
    )
    
    # Print selected results
    selected_keys = [
        'lower_price', 'upper_price', 'grid_spacing_percent',
        'expected_trades_per_day', 'profit_per_trade',
        'daily_profit_after_fees', 'monthly_return_percent'
    ]
    
    for key in selected_keys:
        value = grid_results[key]
        if 'price' in key:
            print(f"{key:25}: ${value:.2f}")
        elif 'percent' in key:
            print(f"{key:25}: {value:.2f}%")
        else:
            print(f"{key:25}: {value:.4f}")
    
    # Example 4: Protective Put Hedge
    print("\n4. PROTECTIVE PUT HEDGE (BTC Example)")
    print("-" * 40)
    hedge_results = calculator.protective_put_hedge(
        asset_price=30000,
        position_size=100000,
        put_strike=28000,
        put_premium=500,
        time_to_expiry_days=30
    )
    
    for key, value in hedge_results.items():
        if key == 'num_puts_needed':
            print(f"{key:25}: {value:.0f}")
        elif 'percent' in key:
            print(f"{key:25}: {value:.2f}%")
        elif 'price' in key:
            print(f"{key:25}: ${value:.2f}")
        else:
            print(f"{key:25}: ${value:.2f}")
    
    print("\n" + "=" * 60)
    print("Note: These are simplified calculations for educational purposes.")
    print("Real trading involves additional risks and considerations.")
    print("=" * 60)


if __name__ == "__main__":
    main()