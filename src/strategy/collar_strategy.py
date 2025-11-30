"""
Collar Strategy Implementation

A collar strategy protects stock holdings by:
1. Buying a protective put (downside protection)
2. Selling a covered call (generates income to offset put cost)

This creates a "collar" around your stock position, limiting both gains and losses.
"""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class CollarParameters:
    """Parameters for a collar strategy.
    
    A collar consists of:
    - Long stock position (100 shares per collar)
    - Long put (protective put below current price)
    - Short call (covered call above current price)
    """
    symbol: str
    current_price: float
    shares_owned: int  # Should be multiple of 100
    
    # Put parameters (downside protection)
    put_strike: float  # Strike price for protective put
    put_expiration: date
    
    # Call parameters (income generation)
    call_strike: float  # Strike price for covered call
    call_expiration: date
    
    # Number of collars (1 collar = 100 shares + 1 put + 1 call)
    num_collars: int
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate collar parameters.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Must own at least 100 shares per collar
        if self.shares_owned < self.num_collars * 100:
            return False, f"Need {self.num_collars * 100} shares but only own {self.shares_owned}"
        
        # Put strike should be below current price (out-of-the-money)
        if self.put_strike >= self.current_price:
            return False, f"Put strike ${self.put_strike} must be below current price ${self.current_price}"
        
        # Call strike should be above current price (out-of-the-money)
        if self.call_strike <= self.current_price:
            return False, f"Call strike ${self.call_strike} must be above current price ${self.current_price}"
        
        # Put strike should be below call strike
        if self.put_strike >= self.call_strike:
            return False, f"Put strike ${self.put_strike} must be below call strike ${self.call_strike}"
        
        # Expirations should be in the future
        if self.put_expiration < date.today():
            return False, "Put expiration must be in the future"
        if self.call_expiration < date.today():
            return False, "Call expiration must be in the future"
        
        return True, None
    
    def get_max_profit(self) -> float:
        """Calculate maximum profit potential.
        
        Max profit occurs if stock rises to call strike.
        Profit = (Call Strike - Current Price) * Shares
        Plus any net credit from options
        """
        return (self.call_strike - self.current_price) * self.shares_owned
    
    def get_max_loss(self) -> float:
        """Calculate maximum loss potential.
        
        Max loss occurs if stock drops to put strike.
        Loss = (Current Price - Put Strike) * Shares
        Minus any net credit from options
        """
        return (self.current_price - self.put_strike) * self.shares_owned
    
    def get_protection_range(self) -> tuple[float, float]:
        """Get the price range where position is protected.
        
        Returns:
            Tuple of (floor_price, ceiling_price)
        """
        return (self.put_strike, self.call_strike)


class CollarCalculator:
    """Calculator for collar strategy parameters."""
    
    def __init__(self, put_offset_percent: float = 5.0, call_offset_percent: float = 5.0):
        """Initialize collar calculator.
        
        Args:
            put_offset_percent: How far below current price to place put (default 5%)
            call_offset_percent: How far above current price to place call (default 5%)
        """
        self.put_offset_percent = put_offset_percent
        self.call_offset_percent = call_offset_percent
    
    def calculate_put_strike(self, current_price: float) -> float:
        """Calculate protective put strike price.
        
        Put is placed below current price for downside protection.
        
        Args:
            current_price: Current stock price
            
        Returns:
            Put strike price
        """
        return current_price * (1 - self.put_offset_percent / 100)
    
    def calculate_call_strike(self, current_price: float) -> float:
        """Calculate covered call strike price.
        
        Call is placed above current price to generate income.
        
        Args:
            current_price: Current stock price
            
        Returns:
            Call strike price
        """
        return current_price * (1 + self.call_offset_percent / 100)
    
    def calculate_num_collars(self, shares_owned: int) -> int:
        """Calculate how many collars can be created.
        
        Each collar requires 100 shares.
        
        Args:
            shares_owned: Number of shares owned
            
        Returns:
            Number of collars that can be created
        """
        return shares_owned // 100
    
    def find_nearest_strike_below(self, target: float, available_strikes: list) -> float:
        """Find nearest available strike at or below target.
        
        Args:
            target: Target strike price
            available_strikes: List of available strikes
            
        Returns:
            Nearest strike at or below target
        """
        strikes_below = [s for s in available_strikes if s <= target]
        if not strikes_below:
            raise ValueError(f"No strikes available at or below ${target}")
        return max(strikes_below)
    
    def find_nearest_strike_above(self, target: float, available_strikes: list) -> float:
        """Find nearest available strike at or above target.
        
        Args:
            target: Target strike price
            available_strikes: List of available strikes
            
        Returns:
            Nearest strike at or above target
        """
        strikes_above = [s for s in available_strikes if s >= target]
        if not strikes_above:
            raise ValueError(f"No strikes available at or above ${target}")
        return min(strikes_above)
    
    def validate_collar_parameters(self, params: CollarParameters) -> bool:
        """Validate collar parameters.
        
        Args:
            params: CollarParameters to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails
        """
        is_valid, error = params.validate()
        if not is_valid:
            raise ValueError(f"Collar validation error: {error}")
        return True
