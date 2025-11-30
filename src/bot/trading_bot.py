"""Main trading bot orchestration."""
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import List, Optional
import time

from src.config.config_manager import ConfigManager
from src.config.models import Config
from src.brokers.broker_factory import BrokerFactory
from src.brokers.base_client import BaseBrokerClient
from src.strategy.strategy_calculator import StrategyCalculator, SpreadParameters
from src.order.order_manager import OrderManager, TradeResult
from src.logging.bot_logger import BotLogger


@dataclass
class ExecutionSummary:
    """Summary of a trading cycle execution."""
    execution_date: datetime
    total_symbols: int
    successful_trades: int
    failed_trades: int
    trade_results: List[TradeResult]


class TradingBot:
    """Main trading bot that orchestrates the entire trading workflow."""
    
    def __init__(self, config_path: str, dry_run: bool = False):
        """Initialize the TradingBot.
        
        Args:
            config_path: Path to the configuration file
            dry_run: If True, no actual orders will be submitted
        """
        self.config_path = config_path
        self.dry_run = dry_run
        self.config: Optional[Config] = None
        self.config_manager: Optional[ConfigManager] = None
        self.logger: Optional[BotLogger] = None
        self.broker_client: Optional[BaseBrokerClient] = None
        self.strategy_calculator: Optional[StrategyCalculator] = None
        self.order_manager: Optional[OrderManager] = None
        self._initialized = False
    
    def initialize(self) -> bool:
        """Initialize all components of the trading bot.
        
        This method sets up:
        - Configuration manager and loads config
        - Logger
        - Alpaca client and authenticates
        - Strategy calculator
        - Order manager
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Load configuration
            self.config_manager = ConfigManager()
            self.config = self.config_manager.load_config(self.config_path)
            
            # Initialize logger
            self.logger = BotLogger(self.config.logging_config)
            self.logger.log_info(
                "Trading bot initialization started",
                {"config_path": self.config_path, "dry_run": self.dry_run}
            )
            
            # Initialize broker client using factory
            broker_type = self.config.broker_type
            self.logger.log_info(f"Initializing {broker_type} broker via Lumibot")
            
            if broker_type.lower() == 'alpaca':
                credentials = {
                    'api_key': self.config.alpaca_credentials.api_key,
                    'api_secret': self.config.alpaca_credentials.api_secret,
                    'paper': self.config.alpaca_credentials.paper
                }
            else:  # tradier
                credentials = {
                    'api_token': self.config.tradier_credentials.api_token,
                    'account_id': self.config.tradier_credentials.account_id,
                    'base_url': self.config.tradier_credentials.base_url
                }
            
            self.broker_client = BrokerFactory.create_broker(
                broker_type=broker_type,
                credentials=credentials,
                logger=self.logger
            )
            
            # Authenticate with broker
            self.logger.log_info(f"Authenticating with {broker_type} API via Lumibot")
            if not self.broker_client.authenticate():
                self.logger.log_error(f"Failed to authenticate with {broker_type} API")
                return False
            
            # Initialize strategy calculator
            self.strategy_calculator = StrategyCalculator(self.config)
            self.logger.log_info("Strategy calculator initialized")
            
            # Initialize order manager
            self.order_manager = OrderManager(
                broker_client=self.broker_client,
                logger=self.logger,
                dry_run=self.dry_run
            )
            if self.dry_run:
                self.logger.log_info("Order manager initialized in DRY-RUN mode")
            else:
                self.logger.log_info("Order manager initialized")
            
            self._initialized = True
            self.logger.log_info(
                "Trading bot initialization complete",
                {
                    "symbols": self.config.symbols,
                    "strike_offset": self.config.strike_offset_percent,
                    "spread_width": self.config.spread_width,
                    "contract_quantity": self.config.contract_quantity
                }
            )
            
            return True
            
        except FileNotFoundError as e:
            if self.logger:
                self.logger.log_error(
                    f"Configuration file not found: {str(e)}",
                    e,
                    {
                        "config_path": self.config_path,
                        "error_type": "FileNotFoundError"
                    }
                )
            else:
                print(f"ERROR: Configuration file not found: {str(e)}")
            return False
            
        except ValueError as e:
            if self.logger:
                self.logger.log_error(
                    f"Configuration validation error: {str(e)}",
                    e,
                    {
                        "config_path": self.config_path,
                        "error_type": "ValueError"
                    }
                )
            else:
                print(f"ERROR: Configuration validation error: {str(e)}")
            return False
            
        except Exception as e:
            if self.logger:
                self.logger.log_error(
                    f"Unexpected error during initialization: {str(e)}",
                    e,
                    {
                        "config_path": self.config_path,
                        "error_type": type(e).__name__
                    }
                )
            else:
                print(f"ERROR: Unexpected error during initialization: {str(e)}")
            return False
    
    def execute_trading_cycle(self, market_wait_timeout_minutes: int = 60) -> ExecutionSummary:
        """Execute a complete trading cycle for all configured symbols.
        
        This method:
        1. Verifies the bot is initialized
        2. Checks market status (but proceeds regardless)
        3. Processes each configured symbol
        4. Submits orders (queued if market closed, executed immediately if open)
        5. Collects results into an ExecutionSummary
        
        Args:
            market_wait_timeout_minutes: Not used (kept for backward compatibility)
        
        Returns:
            ExecutionSummary with results of the trading cycle
            
        Raises:
            RuntimeError: If bot is not initialized
        
        Note:
            Orders are submitted with GTC (Good-Til-Canceled) time-in-force,
            allowing them to be placed when market is closed. They will be
            queued and executed when the market opens.
        """
        if not self._initialized:
            raise RuntimeError("Trading bot not initialized. Call initialize() first.")
        
        execution_date = datetime.now()
        self.logger.log_info("Starting trading cycle", {"execution_date": execution_date.isoformat()})
        
        # Check market status but don't block execution
        try:
            is_market_open = self.broker_client.is_market_open()
            if is_market_open:
                self.logger.log_info("Market is currently OPEN - orders will be executed immediately")
            else:
                self.logger.log_warning(
                    "Market is currently CLOSED - orders will be queued and executed when market opens",
                    {"note": "Orders will appear in Alpaca dashboard as pending"}
                )
        except Exception as e:
            self.logger.log_warning(
                f"Could not check market status: {str(e)} - proceeding anyway",
                {"error": str(e)}
            )
        
        # Get list of symbols to process
        symbols = self.config.symbols
        self.logger.log_info(
            f"Processing {len(symbols)} symbols",
            {"symbols": symbols}
        )
        
        # Validate symbols before processing
        valid_symbols = []
        invalid_symbols = []
        
        for symbol in symbols:
            if self._validate_symbol(symbol):
                valid_symbols.append(symbol)
            else:
                invalid_symbols.append(symbol)
        
        if invalid_symbols:
            self.logger.log_warning(
                f"Skipping {len(invalid_symbols)} invalid symbol(s): {', '.join(invalid_symbols)}",
                {"invalid_symbols": invalid_symbols}
            )
        
        if not valid_symbols:
            self.logger.log_error("No valid symbols to process")
            return ExecutionSummary(
                execution_date=execution_date,
                total_symbols=len(symbols),
                successful_trades=0,
                failed_trades=len(symbols),
                trade_results=[]
            )
        
        self.logger.log_info(
            f"Processing {len(valid_symbols)} valid symbol(s)",
            {"valid_symbols": valid_symbols}
        )
        
        # Process each valid symbol and collect results
        trade_results: List[TradeResult] = []
        
        for symbol in valid_symbols:
            try:
                self.logger.log_info(f"Processing symbol: {symbol}")
                trade_result = self.process_symbol(symbol)
                trade_results.append(trade_result)
                
            except Exception as e:
                # Ensure failure for one symbol doesn't stop processing others
                self.logger.log_error(
                    f"Unexpected error processing symbol {symbol}",
                    e,
                    {
                        "symbol": symbol,
                        "error_type": type(e).__name__,
                        "execution_date": execution_date.isoformat()
                    }
                )
                
                # Create a failed trade result
                failed_result = TradeResult(
                    symbol=symbol,
                    success=False,
                    order_id=None,
                    short_strike=0.0,
                    long_strike=0.0,
                    expiration=date.today(),
                    quantity=0,
                    filled_price=None,
                    error_message=f"Unexpected error: {type(e).__name__}: {str(e)}",
                    timestamp=datetime.now()
                )
                trade_results.append(failed_result)
        
        # Calculate summary statistics
        successful_trades = sum(1 for result in trade_results if result.success)
        failed_trades = len(trade_results) - successful_trades
        
        # Create execution summary
        summary = ExecutionSummary(
            execution_date=execution_date,
            total_symbols=len(symbols),
            successful_trades=successful_trades,
            failed_trades=failed_trades,
            trade_results=trade_results
        )
        
        # Log execution summary
        self._log_execution_summary(summary)
        
        return summary
    
    def _validate_symbol(self, symbol: str) -> bool:
        """Validate if a symbol is valid for trading.
        
        Args:
            symbol: Stock symbol to validate
            
        Returns:
            True if symbol is valid, False otherwise
        """
        # Basic validation: symbol should be uppercase letters only, 1-5 characters
        if not symbol:
            self.logger.log_warning(
                "Empty symbol provided",
                {"symbol": symbol}
            )
            return False
        
        if not isinstance(symbol, str):
            self.logger.log_warning(
                "Symbol must be a string",
                {"symbol": symbol, "type": type(symbol).__name__}
            )
            return False
        
        # Check if symbol contains only uppercase letters
        if not symbol.isupper() or not symbol.isalpha():
            self.logger.log_warning(
                f"Invalid symbol format: {symbol}. Symbol must contain only uppercase letters",
                {"symbol": symbol}
            )
            return False
        
        # Check symbol length (typically 1-5 characters for US stocks)
        if len(symbol) < 1 or len(symbol) > 5:
            self.logger.log_warning(
                f"Invalid symbol length: {symbol}. Symbol must be 1-5 characters",
                {"symbol": symbol, "length": len(symbol)}
            )
            return False
        
        # In dry-run mode or if market is closed, skip price validation
        if self.dry_run:
            self.logger.log_info(
                f"[DRY-RUN MODE] Symbol {symbol} passed basic validation (skipping price check)",
                {"symbol": symbol, "dry_run": True}
            )
            return True
        
        # Try to verify symbol exists by fetching price
        # If this fails (market closed, API issue), accept the symbol anyway
        try:
            price = self.broker_client.get_current_price(symbol)
            if price <= 0:
                self.logger.log_warning(
                    f"Invalid price for symbol {symbol}: ${price}",
                    {"symbol": symbol, "price": price}
                )
                return False
            
            self.logger.log_info(
                f"Symbol {symbol} validated successfully",
                {"symbol": symbol, "price": price}
            )
            return True
            
        except Exception as e:
            # If we can't validate (market closed, API issue), accept the symbol
            self.logger.log_warning(
                f"Could not validate {symbol} (market may be closed): {str(e)}",
                {"symbol": symbol, "error": str(e)}
            )
            self.logger.log_info(
                f"Accepting {symbol} despite validation failure (will attempt to trade)",
                {"symbol": symbol}
            )
            return True  # Accept symbol even if validation fails
    
    def _wait_for_market_open(self, timeout_minutes: int = 60) -> bool:
        """Wait for market to open with timeout.
        
        This method checks if the market is open. If closed, it waits until
        the market opens or the timeout is reached.
        
        Args:
            timeout_minutes: Maximum minutes to wait for market to open
            
        Returns:
            True if market is open, False if timeout reached
        """
        try:
            # Check if market is currently open
            if self.broker_client.is_market_open():
                self.logger.log_info("Market is open, proceeding with trading cycle")
                return True
            
            # Market is closed, get next open time
            self.logger.log_warning("Market is currently closed")
            
            try:
                next_open = self.broker_client.get_market_open_time()
                now = datetime.now(next_open.tzinfo)  # Match timezone
                wait_time = (next_open - now).total_seconds()
                
                self.logger.log_info(
                    f"Market will open at {next_open.isoformat()}",
                    {
                        "next_open": next_open.isoformat(),
                        "wait_seconds": int(wait_time)
                    }
                )
                
                # Check if wait time exceeds timeout
                timeout_seconds = timeout_minutes * 60
                if wait_time > timeout_seconds:
                    self.logger.log_warning(
                        f"Market open time ({wait_time/60:.1f} min) exceeds timeout ({timeout_minutes} min)",
                        {
                            "wait_minutes": wait_time / 60,
                            "timeout_minutes": timeout_minutes
                        }
                    )
                    return False
                
                # Wait until market opens
                if wait_time > 0:
                    self.logger.log_info(
                        f"Waiting {wait_time/60:.1f} minutes for market to open",
                        {"wait_minutes": wait_time / 60}
                    )
                    
                    # Sleep in intervals to allow for interruption
                    sleep_interval = 60  # Check every minute
                    elapsed = 0
                    
                    while elapsed < wait_time:
                        time.sleep(min(sleep_interval, wait_time - elapsed))
                        elapsed += sleep_interval
                        
                        # Check if market opened early
                        if self.broker_client.is_market_open():
                            self.logger.log_info("Market opened, proceeding with trading cycle")
                            return True
                    
                    # Final check after wait
                    if self.broker_client.is_market_open():
                        self.logger.log_info("Market is now open, proceeding with trading cycle")
                        return True
                    else:
                        self.logger.log_warning("Market still closed after waiting")
                        return False
                
            except Exception as e:
                self.logger.log_error(
                    "Failed to get market open time, cannot wait for market",
                    e
                )
                return False
                
        except Exception as e:
            self.logger.log_error(
                "Failed to check market status",
                e
            )
            # If we can't check market status, log error but don't block execution
            # This allows the bot to attempt trading even if market check fails
            self.logger.log_warning("Proceeding with trading cycle despite market check failure")
            return True
    
    def process_symbol(self, symbol: str) -> TradeResult:
        """Process a single symbol through the complete trading workflow.
        
        This method:
        1. Gets current market price
        2. Calculates spread parameters using StrategyCalculator
        3. Retrieves option chain and finds available strikes
        4. Submits order using OrderManager
        
        Args:
            symbol: Stock symbol to process (e.g., 'AAPL')
            
        Returns:
            TradeResult with execution details
        """
        timestamp = datetime.now()
        
        try:
            # Get current market price
            self.logger.log_info(f"Fetching current price for {symbol}")
            current_price = self.broker_client.get_current_price(symbol)
            self.logger.log_info(
                f"Current price for {symbol}: ${current_price:.2f}",
                {"symbol": symbol, "price": current_price}
            )
            
            # Calculate spread parameters
            self.logger.log_info(f"Calculating spread parameters for {symbol}")
            
            # Calculate short strike (below market price)
            short_strike = self.strategy_calculator.calculate_short_strike(
                current_price=current_price,
                offset_percent=self.config.strike_offset_percent
            )
            
            # Calculate long strike (below short strike)
            long_strike = self.strategy_calculator.calculate_long_strike(
                short_strike=short_strike,
                spread_width=self.config.spread_width
            )
            
            # Calculate expiration date
            expiration = self.strategy_calculator.calculate_expiration_date(
                execution_date=date.today(),
                offset_weeks=self.config.expiration_offset_weeks
            )
            
            self.logger.log_info(
                f"Calculated strikes for {symbol}",
                {
                    "symbol": symbol,
                    "short_strike": f"${short_strike:.2f}",
                    "long_strike": f"${long_strike:.2f}",
                    "expiration": expiration.isoformat(),
                    "spread_width": f"${short_strike - long_strike:.2f}"
                }
            )
            
            # Retrieve option chain and find available strikes
            self.logger.log_info(f"Retrieving option chain for {symbol}")
            
            # Store original calculated strikes for logging
            original_short_strike = short_strike
            original_long_strike = long_strike
            
            try:
                option_chain = self.broker_client.get_option_chain(symbol, expiration)
                available_strikes = sorted([contract.strike for contract in option_chain])
                
                if not available_strikes:
                    error_msg = "No option strikes available in option chain"
                    self.logger.log_warning(
                        f"Skipping {symbol} - {error_msg}",
                        {"symbol": symbol, "expiration": expiration.isoformat()}
                    )
                    return TradeResult(
                        symbol=symbol,
                        success=False,
                        order_id=None,
                        short_strike=short_strike,
                        long_strike=long_strike,
                        expiration=expiration,
                        quantity=self.config.contract_quantity,
                        filled_price=None,
                        error_message=error_msg,
                        timestamp=timestamp
                    )
                
                self.logger.log_info(
                    f"Retrieved {len(available_strikes)} available strikes for {symbol}",
                    {
                        "symbol": symbol,
                        "strike_count": len(available_strikes),
                        "min_strike": min(available_strikes),
                        "max_strike": max(available_strikes)
                    }
                )
                
                # Find nearest available strikes below target (for put credit spreads)
                try:
                    short_strike = self.strategy_calculator.find_nearest_strike_below(
                        target_strike=short_strike,
                        available_strikes=available_strikes
                    )
                except ValueError as e:
                    error_msg = f"Cannot find suitable short strike: {str(e)}"
                    self.logger.log_warning(
                        f"Skipping {symbol} - {error_msg}",
                        {"symbol": symbol, "target_strike": original_short_strike}
                    )
                    return TradeResult(
                        symbol=symbol,
                        success=False,
                        order_id=None,
                        short_strike=original_short_strike,
                        long_strike=original_long_strike,
                        expiration=expiration,
                        quantity=self.config.contract_quantity,
                        filled_price=None,
                        error_message=error_msg,
                        timestamp=timestamp
                    )
                
                try:
                    long_strike = self.strategy_calculator.find_nearest_strike_below(
                        target_strike=long_strike,
                        available_strikes=available_strikes
                    )
                except ValueError as e:
                    error_msg = f"Cannot find suitable long strike: {str(e)}"
                    self.logger.log_warning(
                        f"Skipping {symbol} - {error_msg}",
                        {"symbol": symbol, "target_strike": original_long_strike}
                    )
                    return TradeResult(
                        symbol=symbol,
                        success=False,
                        order_id=None,
                        short_strike=short_strike,
                        long_strike=original_long_strike,
                        expiration=expiration,
                        quantity=self.config.contract_quantity,
                        filled_price=None,
                        error_message=error_msg,
                        timestamp=timestamp
                    )
                
                # Check if we had to use fallback strikes (different from calculated)
                if abs(short_strike - original_short_strike) > 0.01 or abs(long_strike - original_long_strike) > 0.01:
                    self.logger.log_info(
                        f"Using fallback strikes for {symbol} (calculated strikes not available)",
                        {
                            "symbol": symbol,
                            "calculated_short": f"${original_short_strike:.2f}",
                            "actual_short": f"${short_strike:.2f}",
                            "calculated_long": f"${original_long_strike:.2f}",
                            "actual_long": f"${long_strike:.2f}"
                        }
                    )
                else:
                    self.logger.log_info(
                        f"Using calculated strikes for {symbol} (exact match found)",
                        {
                            "symbol": symbol,
                            "short_strike": f"${short_strike:.2f}",
                            "long_strike": f"${long_strike:.2f}"
                        }
                    )
                
            except ValueError as e:
                # Option chain unavailable - log and skip symbol
                error_msg = f"Option chain unavailable: {str(e)}"
                self.logger.log_warning(
                    f"Skipping {symbol} - {error_msg}",
                    {"symbol": symbol, "error": error_msg}
                )
                
                return TradeResult(
                    symbol=symbol,
                    success=False,
                    order_id=None,
                    short_strike=original_short_strike,
                    long_strike=original_long_strike,
                    expiration=expiration,
                    quantity=self.config.contract_quantity,
                    filled_price=None,
                    error_message=error_msg,
                    timestamp=timestamp
                )
            
            # Validate spread parameters
            actual_spread_width = short_strike - long_strike
            
            # Check if spread width is reasonable (within 50% of configured width)
            configured_width = self.config.spread_width
            if actual_spread_width < configured_width * 0.5:
                error_msg = f"Actual spread width (${actual_spread_width:.2f}) is too narrow compared to configured (${configured_width:.2f})"
                self.logger.log_warning(
                    f"Skipping {symbol} - {error_msg}",
                    {
                        "symbol": symbol,
                        "actual_width": actual_spread_width,
                        "configured_width": configured_width
                    }
                )
                return TradeResult(
                    symbol=symbol,
                    success=False,
                    order_id=None,
                    short_strike=short_strike,
                    long_strike=long_strike,
                    expiration=expiration,
                    quantity=self.config.contract_quantity,
                    filled_price=None,
                    error_message=error_msg,
                    timestamp=timestamp
                )
            
            spread_params = SpreadParameters(
                symbol=symbol,
                short_strike=short_strike,
                long_strike=long_strike,
                expiration=expiration,
                current_price=current_price,
                spread_width=actual_spread_width
            )
            
            try:
                self.strategy_calculator.validate_spread_parameters(spread_params)
            except ValueError as e:
                error_msg = f"Spread validation failed: {str(e)}"
                self.logger.log_error(
                    f"Invalid spread parameters for {symbol}",
                    e,
                    {"symbol": symbol}
                )
                
                return TradeResult(
                    symbol=symbol,
                    success=False,
                    order_id=None,
                    short_strike=short_strike,
                    long_strike=long_strike,
                    expiration=expiration,
                    quantity=self.config.contract_quantity,
                    filled_price=None,
                    error_message=error_msg,
                    timestamp=timestamp
                )
            
            # Submit order using OrderManager
            self.logger.log_info(f"Submitting order for {symbol}")
            trade_result = self.order_manager.submit_order_with_error_handling(
                symbol=symbol,
                short_strike=short_strike,
                long_strike=long_strike,
                expiration=expiration,
                quantity=self.config.contract_quantity,
                max_retries=3
            )
            
            return trade_result
            
        except ValueError as e:
            # Handle price data unavailable or other value errors
            error_msg = f"Data error: {str(e)}"
            self.logger.log_error(
                f"Failed to process {symbol}: {error_msg}",
                e,
                {
                    "symbol": symbol,
                    "error_type": "ValueError",
                    "timestamp": timestamp.isoformat()
                }
            )
            
            return TradeResult(
                symbol=symbol,
                success=False,
                order_id=None,
                short_strike=0.0,
                long_strike=0.0,
                expiration=date.today(),
                quantity=self.config.contract_quantity,
                filled_price=None,
                error_message=error_msg,
                timestamp=timestamp
            )
            
        except Exception as e:
            # Handle any unexpected errors
            error_msg = f"Unexpected error: {type(e).__name__}: {str(e)}"
            self.logger.log_error(
                f"Unexpected error processing {symbol}",
                e,
                {
                    "symbol": symbol,
                    "error_type": type(e).__name__,
                    "timestamp": timestamp.isoformat()
                }
            )
            
            return TradeResult(
                symbol=symbol,
                success=False,
                order_id=None,
                short_strike=0.0,
                long_strike=0.0,
                expiration=date.today(),
                quantity=self.config.contract_quantity,
                filled_price=None,
                error_message=error_msg,
                timestamp=timestamp
            )

    def _log_execution_summary(self, summary: ExecutionSummary):
        """Log execution summary with success/failure counts and detailed report.
        
        This method generates a comprehensive report of the trading cycle,
        including overall statistics and individual trade results.
        
        Args:
            summary: ExecutionSummary to log
        """
        # Log overall summary
        summary_dict = {
            'execution_date': summary.execution_date.isoformat(),
            'total_symbols': summary.total_symbols,
            'successful_trades': summary.successful_trades,
            'failed_trades': summary.failed_trades
        }
        
        self.logger.log_execution_summary(summary_dict)
        
        # Generate detailed report of all trade results
        self.logger.log_info("=" * 60)
        self.logger.log_info("DETAILED TRADE RESULTS")
        self.logger.log_info("=" * 60)
        
        for trade_result in summary.trade_results:
            status = "SUCCESS" if trade_result.success else "FAILED"
            
            trade_info = {
                "symbol": trade_result.symbol,
                "status": status,
                "short_strike": f"${trade_result.short_strike:.2f}",
                "long_strike": f"${trade_result.long_strike:.2f}",
                "expiration": trade_result.expiration.isoformat(),
                "quantity": trade_result.quantity
            }
            
            if trade_result.success:
                if trade_result.order_id:
                    trade_info["order_id"] = trade_result.order_id
                if trade_result.filled_price:
                    trade_info["filled_price"] = f"${trade_result.filled_price:.2f}"
                
                self.logger.log_info(
                    f"✓ {trade_result.symbol}: Order submitted successfully",
                    trade_info
                )
            else:
                trade_info["error"] = trade_result.error_message
                self.logger.log_error(
                    f"✗ {trade_result.symbol}: Order failed",
                    context=trade_info
                )
        
        self.logger.log_info("=" * 60)
        
        # Log summary statistics
        success_rate = (summary.successful_trades / summary.total_symbols * 100) if summary.total_symbols > 0 else 0
        
        self.logger.log_info(
            f"Trading cycle complete: {summary.successful_trades}/{summary.total_symbols} successful ({success_rate:.1f}%)",
            {
                "execution_date": summary.execution_date.isoformat(),
                "success_rate": f"{success_rate:.1f}%"
            }
        )
        
        # Ensure graceful handling of partial failures
        if summary.failed_trades > 0:
            self.logger.log_warning(
                f"{summary.failed_trades} trade(s) failed during this cycle",
                {
                    "failed_count": summary.failed_trades,
                    "total_count": summary.total_symbols
                }
            )
            
            # Log failed symbols for easy reference
            failed_symbols = [
                result.symbol for result in summary.trade_results 
                if not result.success
            ]
            self.logger.log_warning(
                f"Failed symbols: {', '.join(failed_symbols)}",
                {"failed_symbols": failed_symbols}
            )

    def shutdown(self):
        """Perform graceful shutdown and cleanup.
        
        This method:
        1. Closes broker connections
        2. Flushes log buffers
        3. Cleans up resources
        """
        if self.logger:
            self.logger.log_info("Initiating trading bot shutdown")
        
        try:
            # Close broker connections
            if self.broker_client:
                broker_name = self.broker_client.get_broker_name()
                self.logger.log_info(f"Closing {broker_name} broker connections")
                # Lumibot brokers handle cleanup internally
                self.broker_client = None
            
            # Flush log buffers
            if self.logger:
                self.logger.log_info("Flushing log buffers")
                for handler in self.logger.logger.handlers:
                    handler.flush()
            
            # Mark as not initialized
            self._initialized = False
            
            if self.logger:
                self.logger.log_info("Trading bot shutdown complete")
            
        except Exception as e:
            if self.logger:
                self.logger.log_error(
                    "Error during shutdown",
                    e,
                    {
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )
            else:
                print(f"ERROR during shutdown: {type(e).__name__}: {str(e)}")
