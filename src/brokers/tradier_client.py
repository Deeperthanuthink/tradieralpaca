"""Tradier broker client using Lumibot."""
from datetime import datetime, date, timedelta
from typing import List, Optional

from lumibot.brokers import Tradier
from lumibot.entities import Asset

from src.logging.bot_logger import BotLogger
from .base_client import (
    BaseBrokerClient, OptionContract, SpreadOrder,
    OrderResult, AccountInfo
)


class TradierClient(BaseBrokerClient):
    """Client for interacting with Tradier API using Lumibot."""
    
    def __init__(self, api_token: str, account_id: str, base_url: str, logger: Optional[BotLogger] = None):
        """Initialize Lumibot Tradier client.
        
        Args:
            api_token: Tradier API access token
            account_id: Tradier account ID
            base_url: Tradier API base URL (sandbox or production)
            logger: Optional logger instance
        """
        self.api_token = api_token
        self.account_id = account_id
        self.logger = logger
        
        # Determine if using sandbox
        self.is_sandbox = 'sandbox' in base_url.lower()
        
        # Initialize Lumibot Tradier broker
        self.broker = Tradier(
            access_token=api_token,
            account_number=account_id,
            paper=self.is_sandbox
        )
        
        if logger:
            logger.log_info(
                "Initialized Lumibot Tradier broker",
                {
                    "framework": "Lumibot",
                    "broker": "Tradier",
                    "sandbox": self.is_sandbox,
                    "account_id": account_id
                }
            )
        
    def get_broker_name(self) -> str:
        """Get the name of the broker."""
        return "Tradier"
    
    def _generate_synthetic_strikes(self, symbol: str, expiration: date) -> List[OptionContract]:
        """Generate synthetic option strikes when real data is unavailable.
        
        This is used when the market is closed and option chains aren't available.
        Generates reasonable strikes based on typical option increments.
        
        Args:
            symbol: Stock symbol
            expiration: Expiration date
            
        Returns:
            List of synthetic OptionContract objects
        """
        # Generate strikes from $10 to $1500 with appropriate increments
        strikes = []
        
        # $10-$50: $1 increments
        for strike in range(10, 50, 1):
            strikes.append(float(strike))
        
        # $50-$100: $2.50 increments
        for strike in [50, 52.5, 55, 57.5, 60, 62.5, 65, 67.5, 70, 72.5, 75, 77.5, 80, 82.5, 85, 87.5, 90, 92.5, 95, 97.5, 100]:
            strikes.append(float(strike))
        
        # $100-$200: $2.50 increments  
        for strike in range(100, 200, 5):
            strikes.append(float(strike))
            strikes.append(float(strike + 2.5))
        
        # $200-$500: $5 increments
        for strike in range(200, 500, 5):
            strikes.append(float(strike))
        
        # $500-$1500: $10 increments
        for strike in range(500, 1500, 10):
            strikes.append(float(strike))
        
        # Create option contracts
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
    
    def get_framework_info(self) -> dict:
        """Get information about the trading framework being used.
        
        Returns:
            Dictionary with framework details
        """
        return {
            "framework": "Lumibot",
            "version": getattr(self.broker, '__version__', 'unknown'),
            "broker": "Tradier",
            "broker_class": self.broker.__class__.__name__,
            "sandbox": self.is_sandbox,
            "account_id": self.account_id
        }
    
    def authenticate(self) -> bool:
        """Authenticate with Tradier API and verify credentials.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            # Log framework info
            if self.logger:
                framework_info = self.get_framework_info()
                self.logger.log_info(
                    "Using Lumibot framework for trading",
                    framework_info
                )
            
            # Verify credentials by checking if we can get market status
            # Lumibot broker doesn't have get_cash() outside of Strategy context
            is_open = self.broker.is_market_open()
            
            # If we can check market status, authentication worked
            if self.logger:
                self.logger.log_info(
                    "✓ Successfully authenticated with Tradier API via Lumibot",
                    {
                        "account_id": self.account_id,
                        "sandbox": self.is_sandbox,
                        "market_open": is_open,
                        "framework": "Lumibot"
                    }
                )
            return True
                
        except Exception as e:
            error_msg = f"Unexpected error during authentication: {str(e)}"
            if self.logger:
                self.logger.log_error(
                    error_msg,
                    e,
                    {
                        "account_id": self.account_id,
                        "error_type": type(e).__name__
                    }
                )
            return False
    
    def is_market_open(self) -> bool:
        """Check if the market is currently open.
        
        Returns:
            True if market is open, False otherwise
        """
        try:
            is_open = self.broker.is_market_open()
            
            if self.logger:
                self.logger.log_info(
                    f"Market status checked: {'OPEN' if is_open else 'CLOSED'}"
                )
            
            return is_open
                
        except Exception as e:
            error_msg = f"Unexpected error checking market status: {str(e)}"
            if self.logger:
                self.logger.log_error(
                    error_msg,
                    e,
                    {"error_type": type(e).__name__}
                )
            raise
    
    def get_market_open_time(self) -> datetime:
        """Get the next market open time.
        
        Returns:
            Datetime of next market open
        """
        try:
            # Lumibot doesn't have a direct method for this
            # Return a default time (9:30 AM ET next trading day)
            from datetime import timedelta
            now = datetime.now()
            
            # Simple approximation - next weekday at 9:30 AM
            next_day = now + timedelta(days=1)
            while next_day.weekday() >= 5:  # Skip weekends
                next_day += timedelta(days=1)
            
            next_open = next_day.replace(hour=9, minute=30, second=0, microsecond=0)
            
            if self.logger:
                self.logger.log_info(
                    "Estimated next market open time",
                    {"next_open": next_open.isoformat()}
                )
            
            return next_open
                
        except Exception as e:
            error_msg = f"Unexpected error getting market open time: {str(e)}"
            if self.logger:
                self.logger.log_error(
                    error_msg,
                    e,
                    {"error_type": type(e).__name__}
                )
            raise
    
    def get_current_price(self, symbol: str) -> float:
        """Get the current market price for a symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            
        Returns:
            Current price as float
            
        Raises:
            ValueError: If price data is unavailable
        """
        try:
            # Create asset
            asset = Asset(symbol=symbol, asset_type="stock")
            
            # Get last price
            price = self.broker.get_last_price(asset)
            
            if price is None or price <= 0:
                raise ValueError(f"Price data unavailable for symbol {symbol}")
            
            if self.logger:
                self.logger.log_info(
                    f"Retrieved current price for {symbol}",
                    {"symbol": symbol, "price": price}
                )
            
            return float(price)
                
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error getting price for {symbol}: {str(e)}"
            if self.logger:
                self.logger.log_error(
                    error_msg,
                    e,
                    {
                        "symbol": symbol,
                        "error_type": type(e).__name__
                    }
                )
            raise
    
    def get_option_chain(self, symbol: str, expiration: date) -> List[OptionContract]:
        """Get option chain for a symbol and expiration date, filtered for put options.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            expiration: Option expiration date
            
        Returns:
            List of OptionContract objects for put options
            
        Raises:
            ValueError: If option chain is unavailable
        """
        try:
            # Create underlying asset
            underlying = Asset(symbol=symbol, asset_type="stock")
            
            # Get option chain using Lumibot
            chains = self.broker.get_chains(underlying)
            
            if not chains:
                raise ValueError(f"No option chains available for {symbol}")
            
            # Filter for the specific expiration date and put options
            expiration_str = expiration.strftime('%Y-%m-%d')
            put_options = []
            
            for chain in chains:
                # Check if this chain matches our expiration
                if hasattr(chain, 'expiration') and str(chain.expiration) == expiration_str:
                    # Get strikes for puts
                    if hasattr(chain, 'puts') and chain.puts:
                        for strike in chain.puts:
                            # Create option symbol in OCC format
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
                    {
                        "symbol": symbol,
                        "expiration": expiration_str,
                        "put_count": len(put_options)
                    }
                )
            
            return put_options
            
        except ValueError:
            raise
        except Exception as e:
            error_msg = f"Unexpected error getting option chain for {symbol}: {str(e)}"
            if self.logger:
                self.logger.log_error(
                    error_msg,
                    e,
                    {
                        "symbol": symbol,
                        "expiration": expiration.isoformat(),
                        "error_type": type(e).__name__
                    }
                )
            raise ValueError(f"Option chain unavailable for {symbol}") from e
    
    def submit_spread_order(self, spread: SpreadOrder) -> OrderResult:
        """Submit a put credit spread order to Tradier using Lumibot.
        
        Args:
            spread: SpreadOrder object with order details
            
        Returns:
            OrderResult with order ID and status
        """
        try:
            # Format expiration date
            expiration_str = spread.expiration.strftime('%y%m%d')
            
            # Construct option symbols using OCC format
            short_strike_str = f"{int(spread.short_strike * 1000):08d}"
            long_strike_str = f"{int(spread.long_strike * 1000):08d}"
            
            short_symbol = f"{spread.symbol}{expiration_str}P{short_strike_str}"
            long_symbol = f"{spread.symbol}{expiration_str}P{long_strike_str}"
            
            # Use Tradier's native API for multileg orders
            # Lumibot doesn't fully support option spreads, so we use direct API
            import requests
            
            # Calculate a reasonable credit price (typically 20-40% of spread width)
            spread_width = spread.short_strike - spread.long_strike
            estimated_credit = round(spread_width * 0.30, 2)  # 30% of spread width
            
            # Prepare multileg order data
            order_data = {
                'class': 'multileg',
                'symbol': spread.symbol,
                'type': 'credit',
                'duration': spread.time_in_force,
                'price': estimated_credit,  # Credit we want to receive
                'option_symbol[0]': short_symbol,
                'side[0]': 'sell_to_open',
                'quantity[0]': spread.quantity,
                'option_symbol[1]': long_symbol,
                'side[1]': 'buy_to_open',
                'quantity[1]': spread.quantity
            }
            
            # Get base URL from broker
            base_url = 'https://sandbox.tradier.com' if self.is_sandbox else 'https://api.tradier.com'
            
            # Submit via Tradier API
            response = requests.post(
                f'{base_url}/v1/accounts/{self.account_id}/orders',
                data=order_data,
                headers={
                    'Authorization': f'Bearer {self.api_token}',
                    'Accept': 'application/json'
                }
            )
            
            short_result = response
            long_result = response  # Same response for multileg
            
            if response.status_code in [200, 201]:
                result_data = response.json()
                order_info = result_data.get('order', {})
                order_id = order_info.get('id')
                status = order_info.get('status', 'submitted')
                
                result = OrderResult(
                    success=True,
                    order_id=str(order_id) if order_id else None,
                    status=status,
                    error_message=None
                )
                
                if self.logger:
                    self.logger.log_info(
                        f"Successfully submitted spread order for {spread.symbol}",
                        {
                            "symbol": spread.symbol,
                            "order_id": order_id,
                            "status": status,
                            "short_strike": spread.short_strike,
                            "long_strike": spread.long_strike,
                            "quantity": spread.quantity
                        }
                    )
                
                return result
            else:
                error_msg = f"Order rejected: {response.status_code} - {response.text}"
                
                result = OrderResult(
                    success=False,
                    order_id=None,
                    status="rejected",
                    error_message=error_msg
                )
                
                if self.logger:
                    self.logger.log_error(
                        f"Order rejected for {spread.symbol}: {error_msg}",
                        None,
                        {
                            "symbol": spread.symbol,
                            "short_strike": spread.short_strike,
                            "long_strike": spread.long_strike
                        }
                    )
                
                return result
                
        except Exception as e:
            error_msg = f"Unexpected error submitting order for {spread.symbol}: {str(e)}"
            
            if self.logger:
                self.logger.log_error(
                    error_msg,
                    e,
                    {
                        "symbol": spread.symbol,
                        "short_strike": spread.short_strike,
                        "long_strike": spread.long_strike,
                        "expiration": spread.expiration.isoformat(),
                        "quantity": spread.quantity,
                        "error_type": type(e).__name__
                    }
                )
            
            return OrderResult(
                success=False,
                order_id=None,
                status="error",
                error_message=str(e)
            )
    
    def get_account_info(self) -> AccountInfo:
        """Get account information from Tradier via Lumibot.
        
        Returns:
            AccountInfo object with account details
        """
        try:
            # Lumibot broker methods work best within Strategy context
            # For now, return placeholder values
            # In actual trading, positions are tracked automatically by Lumibot
            
            info = AccountInfo(
                account_number=self.account_id,
                buying_power=0.0,  # Lumibot tracks this internally
                cash=0.0,  # Lumibot tracks this internally
                portfolio_value=0.0  # Lumibot tracks this internally
            )
            
            if self.logger:
                self.logger.log_info(
                    "Account info requested (Lumibot tracks internally)",
                    {
                        "account_id": self.account_id,
                        "note": "Lumibot manages account state within Strategy context"
                    }
                )
            
            return info
                
        except Exception as e:
            error_msg = f"Unexpected error getting account info: {str(e)}"
            if self.logger:
                self.logger.log_error(
                    error_msg,
                    e,
                    {"error_type": type(e).__name__}
                )
            raise
