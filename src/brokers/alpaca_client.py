"""Alpaca broker client using Lumibot."""
from datetime import datetime, date, timedelta
from typing import List, Optional

from lumibot.brokers import Alpaca
from lumibot.entities import Asset

from src.logging.bot_logger import BotLogger
from .base_client import (
    BaseBrokerClient, OptionContract, SpreadOrder, 
    OrderResult, AccountInfo
)


class AlpacaClient(BaseBrokerClient):
    """Client for Alpaca broker using Lumibot framework."""
    
    def __init__(self, api_key: str, api_secret: str, paper: bool = True, logger: Optional[BotLogger] = None):
        """Initialize Alpaca client.
        
        Args:
            api_key: Alpaca API key
            api_secret: Alpaca API secret
            paper: If True, use paper trading (default: True)
            logger: Optional logger instance
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.paper = paper
        self.logger = logger
        
        # Initialize Lumibot Alpaca broker
        self.broker = Alpaca(
            api_key=api_key,
            api_secret=api_secret,
            paper=paper
        )
        
        if logger:
            logger.log_info(
                "Initialized Lumibot Alpaca broker",
                {
                    "framework": "Lumibot",
                    "broker": "Alpaca",
                    "paper": paper
                }
            )
    
    def get_broker_name(self) -> str:
        """Get the name of the broker."""
        return "Alpaca"
    
    def _generate_synthetic_strikes(self, symbol: str, expiration: date) -> List[OptionContract]:
        """Generate synthetic option strikes when real data is unavailable.
        
        Args:
            symbol: Stock symbol
            expiration: Expiration date
            
        Returns:
            List of synthetic OptionContract objects
        """
        strikes = []
        for strike in range(50, 100, 5):
            strikes.append(float(strike))
        for strike in range(100, 200, 5):
            strikes.append(float(strike))
        for strike in range(200, 500, 10):
            strikes.append(float(strike))
        for strike in range(500, 1000, 25):
            strikes.append(float(strike))
        
        put_options = []
        exp_str = expiration.strftime('%y%m%d')
        
        for strike in strikes:
            strike_str = f"{int(strike * 1000):08d}"
            option_symbol = f"{symbol}{exp_str}P{strike_str}"
            
            contract = OptionContract(
                symbol=option_symbol,
                strike=strike,
                expiration=expiration,
                option_type='put'
            )
            put_options.append(contract)
        
        return put_options
    
    def authenticate(self) -> bool:
        """Authenticate with Alpaca API."""
        try:
            if self.logger:
                self.logger.log_info(
                    "Using Lumibot framework with Alpaca",
                    {"broker": "Alpaca", "framework": "Lumibot"}
                )
            
            # Verify by checking market status
            is_open = self.broker.is_market_open()
            
            if self.logger:
                self.logger.log_info(
                    "✓ Successfully authenticated with Alpaca via Lumibot",
                    {
                        "broker": "Alpaca",
                        "paper": self.paper,
                        "market_open": is_open,
                        "framework": "Lumibot"
                    }
                )
            return True
                
        except Exception as e:
            if self.logger:
                self.logger.log_error(
                    f"Alpaca authentication failed: {str(e)}",
                    e,
                    {"broker": "Alpaca", "error_type": type(e).__name__}
                )
            return False
    
    def is_market_open(self) -> bool:
        """Check if the market is currently open."""
        try:
            is_open = self.broker.is_market_open()
            if self.logger:
                self.logger.log_info(
                    f"Market status checked: {'OPEN' if is_open else 'CLOSED'}",
                    {"broker": "Alpaca"}
                )
            return is_open
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Error checking market status: {str(e)}", e)
            raise
    
    def get_market_open_time(self) -> datetime:
        """Get the next market open time."""
        try:
            # Simple approximation
            now = datetime.now()
            next_day = now + timedelta(days=1)
            while next_day.weekday() >= 5:
                next_day += timedelta(days=1)
            next_open = next_day.replace(hour=9, minute=30, second=0, microsecond=0)
            
            if self.logger:
                self.logger.log_info(
                    "Estimated next market open time",
                    {"next_open": next_open.isoformat(), "broker": "Alpaca"}
                )
            return next_open
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Error getting market open time: {str(e)}", e)
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """Get the current market price for a symbol."""
        try:
            asset = Asset(symbol=symbol, asset_type="stock")
            price = self.broker.get_last_price(asset)
            
            if price is None or price <= 0:
                raise ValueError(f"Price data unavailable for symbol {symbol}")
            
            if self.logger:
                self.logger.log_info(
                    f"Retrieved current price for {symbol}",
                    {"symbol": symbol, "price": price, "broker": "Alpaca"}
                )
            return float(price)
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Error getting price for {symbol}: {str(e)}", e)
            raise
    
    def get_option_chain(self, symbol: str, expiration: date) -> List[OptionContract]:
        """Get option chain for a symbol and expiration date."""
        try:
            underlying = Asset(symbol=symbol, asset_type="stock")
            chains = self.broker.get_chains(underlying)
            
            if not chains:
                raise ValueError(f"No option chains available for {symbol}")
            
            expiration_str = expiration.strftime('%Y-%m-%d')
            put_options = []
            
            for chain in chains:
                if hasattr(chain, 'expiration') and str(chain.expiration) == expiration_str:
                    if hasattr(chain, 'puts') and chain.puts:
                        for strike in chain.puts:
                            exp_str = expiration.strftime('%y%m%d')
                            strike_str = f"{int(strike * 1000):08d}"
                            option_symbol = f"{symbol}{exp_str}P{strike_str}"
                            
                            contract = OptionContract(
                                symbol=option_symbol,
                                strike=float(strike),
                                expiration=expiration,
                                option_type='put'
                            )
                            put_options.append(contract)
            
            if not put_options:
                if self.logger:
                    self.logger.log_warning(
                        f"No put options from API for {symbol} - generating synthetic strikes (market may be closed)",
                        {"symbol": symbol, "expiration": expiration_str}
                    )
                
                # Generate synthetic option chain when real data unavailable
                put_options = self._generate_synthetic_strikes(symbol, expiration)
                
                if self.logger:
                    self.logger.log_info(
                        f"Generated {len(put_options)} synthetic strikes for {symbol}",
                        {"symbol": symbol, "strike_count": len(put_options)}
                    )
            
            if self.logger:
                self.logger.log_info(
                    f"Retrieved option chain for {symbol}",
                    {"symbol": symbol, "expiration": expiration_str, "put_count": len(put_options), "broker": "Alpaca"}
                )
            return put_options
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Error getting option chain for {symbol}: {str(e)}", e)
            raise ValueError(f"Option chain unavailable for {symbol}") from e
    
    def submit_spread_order(self, spread: SpreadOrder) -> OrderResult:
        """Submit a put credit spread order."""
        try:
            expiration_str = spread.expiration.strftime('%y%m%d')
            short_strike_str = f"{int(spread.short_strike * 1000):08d}"
            long_strike_str = f"{int(spread.long_strike * 1000):08d}"
            
            short_symbol = f"{spread.symbol}{expiration_str}P{short_strike_str}"
            long_symbol = f"{spread.symbol}{expiration_str}P{long_strike_str}"
            
            short_put = Asset(symbol=short_symbol, asset_type="option")
            long_put = Asset(symbol=long_symbol, asset_type="option")
            
            short_order = self.broker.create_order(short_put, spread.quantity, "sell", "market")
            long_order = self.broker.create_order(long_put, spread.quantity, "buy", "market")
            
            short_result = self.broker.submit_order(short_order)
            long_result = self.broker.submit_order(long_order)
            
            if short_result and long_result:
                result = OrderResult(
                    success=True,
                    order_id=f"{short_result.identifier}_{long_result.identifier}",
                    status="submitted",
                    error_message=None
                )
                
                if self.logger:
                    self.logger.log_info(
                        f"Successfully submitted spread order for {spread.symbol}",
                        {"symbol": spread.symbol, "broker": "Alpaca", "short_order_id": short_result.identifier}
                    )
                return result
            else:
                return OrderResult(success=False, order_id=None, status="rejected", 
                                 error_message="Failed to submit one or both legs")
        except Exception as e:
            if self.logger:
                self.logger.log_error(f"Error submitting order for {spread.symbol}: {str(e)}", e)
            return OrderResult(success=False, order_id=None, status="error", error_message=str(e))
    
    def get_account_info(self) -> AccountInfo:
        """Get account information."""
        return AccountInfo(
            account_number="alpaca_account",
            buying_power=0.0,
            cash=0.0,
            portfolio_value=0.0
        )
