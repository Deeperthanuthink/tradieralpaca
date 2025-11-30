# Trading Bot Orchestration

This module contains the main `TradingBot` class that orchestrates the entire trading workflow. It initializes all components (config, logger, API client, strategy calculator, order manager), validates symbols, waits for market open, processes each symbol through the complete trading cycle (price retrieval, strike calculation, option chain lookup, order submission), and generates execution summaries. The bot ensures that failures for individual symbols don't stop processing of others, providing graceful degradation and comprehensive error reporting.
