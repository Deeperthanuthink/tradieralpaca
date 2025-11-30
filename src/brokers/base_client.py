"""Base client interface for all brokers."""
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class OptionContract:
    """Represents an option contract."""
    symbol: str
    strike: float
    expiration: date
    option_type: str  # 'put' or 'call'


@dataclass
class SpreadOrder:
    """Represents a put credit spread order."""
    symbol: str
    short_strike: float
    long_strike: float
    expiration: date
    quantity: int
    order_type: str = "limit"
    time_in_force: str = "gtc"


@dataclass
class OrderResult:
    """Result of an order submission."""
    success: bool
    order_id: Optional[str]
    status: Optional[str]
    error_message: Optional[str]


@dataclass
class AccountInfo:
    """Account information."""
    account_number: str
    buying_power: float
    cash: float
    portfolio_value: float


class BaseBrokerClient(ABC):
    """Abstract base class for all broker clients."""
    
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the broker API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    def is_market_open(self) -> bool:
        """Check if the market is currently open.
        
        Returns:
            True if market is open, False otherwise
        """
        pass
    
    @abstractmethod
    def get_market_open_time(self) -> datetime:
        """Get the next market open time.
        
        Returns:
            Datetime of next market open
        """
        pass
    
    @abstractmethod
    def get_current_price(self, symbol: str) -> float:
        """Get the current market price for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price as float
        """
        pass
    
    @abstractmethod
    def get_option_chain(self, symbol: str, expiration: date) -> List[OptionContract]:
        """Get option chain for a symbol and expiration date.
        
        Args:
            symbol: Stock symbol
            expiration: Option expiration date
            
        Returns:
            List of OptionContract objects for put options
        """
        pass
    
    @abstractmethod
    def submit_spread_order(self, spread: SpreadOrder) -> OrderResult:
        """Submit a put credit spread order.
        
        Args:
            spread: SpreadOrder object with order details
            
        Returns:
            OrderResult with order ID and status
        """
        pass
    
    @abstractmethod
    def get_account_info(self) -> AccountInfo:
        """Get account information.
        
        Returns:
            AccountInfo object with account details
        """
        pass
    
    @abstractmethod
    def get_broker_name(self) -> str:
        """Get the name of the broker.
        
        Returns:
            Broker name string
        """
        pass
    
    @abstractmethod
    def submit_collar_order(self, symbol: str, put_strike: float, call_strike: float,
                           expiration: date, num_collars: int) -> OrderResult:
        """Submit a collar order (protective put + covered call).
        
        Args:
            symbol: Stock symbol
            put_strike: Strike price for protective put
            call_strike: Strike price for covered call
            expiration: Option expiration date
            num_collars: Number of collars (1 collar = 100 shares + 1 put + 1 call)
            
        Returns:
            OrderResult with order ID and status
        """
        pass
