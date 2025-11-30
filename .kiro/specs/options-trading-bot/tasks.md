# Implementation Plan

- [x] 1. Set up project structure and dependencies
  - Create directory structure for src/, tests/, logs/, and config/
  - Create requirements.txt with dependencies: alpaca-trade-api, schedule, python-dotenv
  - Create main entry point script
  - Create sample config.json template
  - _Requirements: 2.1, 2.4, 6.1_

- [-] 2. Implement configuration management
  - [x] 2.1 Create Config data models
    - Implement Config, AlpacaCredentials, and LoggingConfig dataclasses
    - Add validation methods for each data model
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 4.1, 5.1, 6.1_
  
  - [x] 2.2 Implement ConfigManager class
    - Write load_config method to read and parse JSON configuration
    - Implement environment variable substitution for API credentials
    - Add validate_config method to check required fields and value ranges
    - Implement getter methods for all configuration parameters
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 4.1, 5.1, 6.1_
  
  - [x] 2.3 Add configuration error handling
    - Handle missing config file with clear error message
    - Handle invalid JSON format
    - Validate symbol format (uppercase letters only)
    - Validate numeric ranges (positive values for quantities, valid percentages)
    - _Requirements: 2.3, 4.4_
  
  - [x] 2.4 Write unit tests for ConfigManager
    - Test valid configuration loading
    - Test invalid configuration handling
    - Test environment variable substitution
    - Test default value application
    - _Requirements: 2.1, 2.2, 2.3, 3.1, 4.1, 6.1_

- [x] 3. Implement logging system
  - [x] 3.1 Create BotLogger class
    - Implement structured logging with timestamp and log levels
    - Configure both file and console output handlers
    - Add context dictionary support for structured data
    - Implement log rotation to prevent disk space issues
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_
  
  - [x] 3.2 Add specialized logging methods
    - Implement log_trade method for trade execution details
    - Implement log_execution_summary for cycle summaries
    - Ensure API credentials are never logged
    - _Requirements: 8.1, 8.5, 6.5_
  
  - [x] 3.3 Write unit tests for BotLogger
    - Test log file creation and writing
    - Test console output
    - Test credential masking
    - _Requirements: 8.1, 8.5, 6.5_

- [x] 4. Implement Alpaca API client
  - [x] 4.1 Create AlpacaClient class with authentication
    - Initialize Alpaca REST API client with credentials
    - Implement authenticate method to verify credentials
    - Add connection error handling with appropriate logging
    - _Requirements: 6.1, 6.2, 6.3, 6.4_
  
  - [x] 4.2 Implement market data methods
    - Implement is_market_open method using Alpaca clock API
    - Implement get_market_open_time for schedule calculations
    - Implement get_current_price to retrieve latest quote for a symbol
    - Add error handling for unavailable price data
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  
  - [x] 4.3 Implement options data methods
    - Implement get_option_chain to retrieve available strikes and expirations
    - Add filtering for put options only
    - Handle cases where option chain is unavailable
    - _Requirements: 7.5_
  
  - [x] 4.4 Implement order submission
    - Implement submit_spread_order to create and submit put credit spread orders
    - Use Alpaca's multi-leg order format for spreads
    - Return structured OrderResult with order ID and status
    - _Requirements: 1.4, 9.1_
  
  - [x] 4.5 Write unit tests for AlpacaClient
    - Mock Alpaca API responses
    - Test authentication success and failure
    - Test market status checks
    - Test price retrieval
    - Test order submission
    - _Requirements: 6.2, 6.3, 7.1, 7.3_

- [x] 5. Implement strategy calculation logic
  - [x] 5.1 Create StrategyCalculator class
    - Initialize with configuration parameters
    - Create data models for SpreadParameters
    - _Requirements: 3.3, 3.4_
  
  - [x] 5.2 Implement strike price calculations
    - Implement calculate_short_strike using offset percentage below market price
    - Implement calculate_long_strike by subtracting spread width
    - Implement find_nearest_strike to round to available strikes
    - _Requirements: 1.2, 3.3, 3.4_
  
  - [x] 5.3 Implement expiration date calculation
    - Implement calculate_expiration_date to find Friday of target week
    - Handle cases where Friday is a holiday (use next valid expiration)
    - _Requirements: 1.3, 5.4_
  
  - [x] 5.4 Add spread validation
    - Implement validate_spread_parameters to check strike ordering
    - Verify strikes are available in option chain
    - Ensure spread width is positive
    - _Requirements: 7.5_
  
  - [x] 5.5 Write unit tests for StrategyCalculator
    - Test strike calculations with various market prices
    - Test expiration date calculations
    - Test strike rounding logic
    - Test validation logic
    - _Requirements: 1.2, 1.3, 3.3, 3.4_

- [x] 6. Implement order management with retry logic
  - [x] 6.1 Create OrderManager class
    - Initialize with AlpacaClient and Logger dependencies
    - Create SpreadOrder and OrderResult data models
    - _Requirements: 9.1_
  
  - [x] 6.2 Implement order creation and validation
    - Implement create_spread_order to construct order objects
    - Implement validate_order to check order parameters
    - _Requirements: 1.4, 4.2_
  
  - [x] 6.3 Implement retry logic with exponential backoff
    - Implement retry_order with configurable max retries (default 3)
    - Use exponential backoff: 1s, 2s, 4s between retries
    - Log each retry attempt with details
    - Return failure result after max retries exceeded
    - _Requirements: 9.3, 9.4_
  
  - [x] 6.4 Add error handling for order failures
    - Handle order rejection errors
    - Handle insufficient buying power
    - Handle network timeouts
    - Ensure failures for one symbol don't stop processing others
    - _Requirements: 9.1, 9.2, 9.4_
  
  - [x] 6.5 Write unit tests for OrderManager
    - Test order creation
    - Test retry logic with mocked failures
    - Test exponential backoff timing
    - Test error handling
    - _Requirements: 9.1, 9.3, 9.4_

- [x] 7. Implement main trading bot orchestration
  - [x] 7.1 Create TradingBot class
    - Initialize with config path parameter
    - Create ExecutionSummary data model
    - Implement initialize method to set up all components
    - _Requirements: 1.1, 2.1, 6.1_
  
  - [x] 7.2 Implement trading cycle execution
    - Implement execute_trading_cycle as main workflow orchestrator
    - Verify market is open before processing
    - Loop through all configured symbols
    - Collect results into ExecutionSummary
    - _Requirements: 1.1, 7.1, 7.2_
  
  - [x] 7.3 Implement per-symbol processing
    - Implement process_symbol method for single symbol workflow
    - Get current market price
    - Calculate spread parameters using StrategyCalculator
    - Retrieve option chain and find available strikes
    - Submit order using OrderManager
    - Return TradeResult
    - _Requirements: 1.2, 1.3, 1.4, 7.3, 7.4_
  
  - [x] 7.4 Add execution summary and reporting
    - Log execution summary with success/failure counts
    - Generate detailed report of all trade results
    - Ensure graceful handling of partial failures
    - _Requirements: 8.1, 9.2, 9.5_
  
  - [x] 7.5 Implement shutdown and cleanup
    - Implement shutdown method for graceful termination
    - Close Alpaca client connections
    - Flush log buffers
    - _Requirements: 6.4_
  
  - [x] 7.6 Write integration tests for TradingBot
    - Test full trading cycle with mocked Alpaca API
    - Test multi-symbol processing
    - Test error handling across components
    - Test execution summary generation
    - _Requirements: 1.1, 1.4, 9.2, 9.5_

- [x] 8. Implement scheduler for automated execution
  - [x] 8.1 Create Scheduler class
    - Initialize with Config and TradingBot instances
    - Use schedule library for timing
    - _Requirements: 1.1, 5.1, 5.3_
  
  - [x] 8.2 Implement schedule calculation
    - Calculate execution time as market open + configured offset minutes
    - Handle timezone conversion to US/Eastern for market hours
    - Implement schedule_execution to set up weekly trigger
    - _Requirements: 1.1, 1.5, 5.3_
  
  - [x] 8.3 Implement scheduler run loop
    - Implement run method with continuous execution loop
    - Check schedule every minute
    - Handle scheduler errors with logging and restart attempts
    - Implement stop method for graceful shutdown
    - _Requirements: 1.1, 1.5_
        
  - [x] 8.4 Write unit tests for Scheduler
    - Test schedule calculation
    - Test timezone handling
    - Test execution triggering
    - _Requirements: 1.1, 5.3_

- [x] 9. Create main entry point and CLI
  - [x] 9.1 Create main.py entry point script
    - Parse command line arguments for config path
    - Initialize TradingBot with configuration
    - Initialize and start Scheduler
    - Handle keyboard interrupt for graceful shutdown
    - _Requirements: 1.1, 2.1_
  
  - [x] 9.2 Add command line options
    - Add --config option for custom config file path
    - Add --dry-run option for testing without actual orders
    - Add --once option to run single execution without scheduler
    - Add --version option
    - _Requirements: 2.4, 2.5, 3.5, 4.5, 5.5_
  
  - [x] 9.3 Create sample configuration files
    - Create config.example.json with documented parameters
    - Create .env.example for environment variables
    - Add README section explaining configuration
    - _Requirements: 2.1, 6.1_

- [x] 10. Add error handling and edge cases
  - [x] 10.1 Handle market closed scenarios
    - Detect when market is closed at execution time
    - Wait until market opens before proceeding
    - Add timeout to prevent infinite waiting
    - _Requirements: 7.1, 7.2_
  
  - [x] 10.2 Handle invalid symbols
    - Validate symbols before processing
    - Skip invalid symbols with warning log
    - Continue processing remaining valid symbols
    - _Requirements: 2.3, 7.4_
  
  - [x] 10.3 Handle missing option strikes
    - Detect when calculated strikes are not available
    - Find nearest available strikes as fallback
    - Log when fallback strikes are used
    - Skip symbol if no suitable strikes found
    - _Requirements: 7.4, 7.5_
  
  - [x] 10.4 Add comprehensive error logging
    - Ensure all error paths log sufficient detail
    - Include stack traces for unexpected errors
    - Add context information to all error logs
    - _Requirements: 8.2, 8.3_

- [x] 11. Create documentation and deployment guide
  - [x] 11.1 Create README.md
    - Add project overview and features
    - Document installation steps
    - Explain configuration options
    - Provide usage examples
    - Include troubleshooting section
    - _Requirements: 2.1, 6.1_
  
  - [x] 11.2 Add code documentation
    - Add docstrings to all classes and public methods
    - Document parameter types and return values
    - Add inline comments for complex logic
    - _Requirements: All_
  
  - [x] 11.3 Create deployment guide
    - Document environment setup steps
    - Explain how to run as background service
    - Provide systemd service file example
    - Document security best practices
    - _Requirements: 6.1, 6.5_
