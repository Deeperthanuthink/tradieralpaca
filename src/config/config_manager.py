"""Configuration manager for loading and validating configuration."""
import json
import os
import re
from typing import List
from .models import Config, AlpacaCredentials, TradierCredentials, LoggingConfig


class ConfigManager:
    """Manages loading and validation of configuration."""
    
    def __init__(self):
        """Initialize the ConfigManager."""
        self._config: Config = None
    
    def load_config(self, config_path: str) -> Config:
        """Load configuration from a JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Config object with loaded configuration
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
            json.JSONDecodeError: If JSON is malformed
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {config_path}\n"
                f"Please create a configuration file at this location."
            )
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON format in configuration file: {e.msg}",
                e.doc,
                e.pos
            )
        
        # Substitute environment variables
        config_data = self._substitute_env_vars(config_data)
        
        # Get broker type
        broker_type = config_data.get('broker_type', 'tradier')
        
        # Parse broker-specific credentials
        alpaca_credentials = None
        tradier_credentials = None
        
        if broker_type.lower() == 'alpaca':
            alpaca_data = config_data.get('alpaca', {})
            alpaca_credentials = AlpacaCredentials(
                api_key=alpaca_data.get('api_key', ''),
                api_secret=alpaca_data.get('api_secret', ''),
                paper=alpaca_data.get('paper', True)
            )
        elif broker_type.lower() == 'tradier':
            tradier_data = config_data.get('tradier', {})
            tradier_credentials = TradierCredentials(
                api_token=tradier_data.get('api_token', ''),
                account_id=tradier_data.get('account_id', ''),
                base_url=tradier_data.get('base_url', 'https://sandbox.tradier.com')
            )
        
        logging_data = config_data.get('logging', {})
        logging_config = LoggingConfig(
            level=logging_data.get('level', 'INFO'),
            file_path=logging_data.get('file_path', 'logs/trading_bot.log')
        )
        
        # Create main config with type conversion error handling
        try:
            config = Config(
                symbols=config_data.get('symbols', []),
                strike_offset_percent=float(config_data.get('strike_offset_percent', 5.0)),
                spread_width=float(config_data.get('spread_width', 5.0)),
                contract_quantity=int(config_data.get('contract_quantity', 1)),
                execution_day=config_data.get('execution_day', 'Tuesday'),
                execution_time_offset_minutes=int(config_data.get('execution_time_offset_minutes', 30)),
                expiration_offset_weeks=int(config_data.get('expiration_offset_weeks', 1)),
                broker_type=broker_type,
                alpaca_credentials=alpaca_credentials,
                tradier_credentials=tradier_credentials,
                logging_config=logging_config
            )
        except (ValueError, TypeError) as e:
            raise ValueError(
                f"Invalid configuration value type: {e}\n"
                f"Please check that numeric values are numbers and other values are correct types."
            )
        
        # Validate configuration
        if not self.validate_config(config):
            raise ValueError("Configuration validation failed")
        
        self._config = config
        return config
    
    def _substitute_env_vars(self, data):
        """Recursively substitute environment variables in configuration data.
        
        Environment variables should be in the format ${VAR_NAME}.
        
        Args:
            data: Configuration data (dict, list, or string)
            
        Returns:
            Data with environment variables substituted
        """
        if isinstance(data, dict):
            return {key: self._substitute_env_vars(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self._substitute_env_vars(item) for item in data]
        elif isinstance(data, str):
            # Find all ${VAR_NAME} patterns
            pattern = r'\$\{([^}]+)\}'
            matches = re.findall(pattern, data)
            result = data
            for var_name in matches:
                env_value = os.environ.get(var_name, '')
                result = result.replace(f'${{{var_name}}}', env_value)
            return result
        else:
            return data
    
    def validate_config(self, config: Config) -> bool:
        """Validate the configuration.
        
        Args:
            config: Config object to validate
            
        Returns:
            True if valid
            
        Raises:
            ValueError: If validation fails with error message
        """
        is_valid, error_message = config.validate()
        if not is_valid:
            raise ValueError(f"Configuration validation error: {error_message}")
        return True
    
    def get_symbols(self) -> List[str]:
        """Get the list of symbols to trade.
        
        Returns:
            List of symbol strings
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config first.")
        return self._config.symbols
    
    def get_strike_offset_percent(self) -> float:
        """Get the strike price offset percentage.
        
        Returns:
            Strike offset percentage
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config first.")
        return self._config.strike_offset_percent
    
    def get_spread_width(self) -> float:
        """Get the spread width in dollars.
        
        Returns:
            Spread width
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config first.")
        return self._config.spread_width
    
    def get_contract_quantity(self) -> int:
        """Get the number of contracts per trade.
        
        Returns:
            Contract quantity
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config first.")
        return self._config.contract_quantity
    
    def get_execution_day(self) -> str:
        """Get the day of week for execution.
        
        Returns:
            Execution day name
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config first.")
        return self._config.execution_day
    
    def get_execution_time_offset_minutes(self) -> int:
        """Get the execution time offset in minutes after market open.
        
        Returns:
            Execution time offset in minutes
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config first.")
        return self._config.execution_time_offset_minutes
    
    def get_expiration_offset_weeks(self) -> int:
        """Get the expiration offset in weeks.
        
        Returns:
            Expiration offset weeks
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config first.")
        return self._config.expiration_offset_weeks
    
    def get_tradier_credentials(self) -> TradierCredentials:
        """Get Tradier API credentials.
        
        Returns:
            TradierCredentials object
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config first.")
        return self._config.tradier_credentials
    
    def get_logging_config(self) -> LoggingConfig:
        """Get logging configuration.
        
        Returns:
            LoggingConfig object
        """
        if self._config is None:
            raise RuntimeError("Configuration not loaded. Call load_config first.")
        return self._config.logging_config
