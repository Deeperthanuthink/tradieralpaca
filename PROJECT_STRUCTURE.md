# Project Structure

```
options-trading-bot/
│
├── main.py                      # Main entry point for the bot
├── demo.py                      # Demo mode for simulation (works when market closed)
├── requirements.txt             # Python dependencies
├── .env                         # API credentials (not committed to git)
├── .env.example                 # Template for environment variables
│
├── README.md                    # Main documentation
├── DEMO_README.md              # Demo mode documentation
├── DEPLOYMENT.md               # Production deployment guide
├── PROJECT_STRUCTURE.md        # This file
│
├── config/                      # Configuration files
│   ├── README.md               # Configuration documentation
│   ├── config.json             # Your configuration (not committed)
│   └── config.example.json     # Configuration template
│
├── logs/                        # Log files directory
│   ├── README.md               # Logging documentation
│   └── trading_bot.log         # Main log file (auto-rotated)
│
├── src/                         # Source code
│   ├── README.md               # Source code overview
│   │
│   ├── alpaca/                 # Alpaca API client
│   │   ├── README.md
│   │   └── alpaca_client.py   # API communication, market data, orders
│   │
│   ├── bot/                    # Main bot orchestration
│   │   ├── README.md
│   │   └── trading_bot.py     # Main workflow orchestration
│   │
│   ├── config/                 # Configuration management
│   │   ├── README.md
│   │   ├── config_manager.py  # Load and validate config
│   │   └── models.py          # Configuration data models
│   │
│   ├── logging/                # Structured logging
│   │   ├── README.md
│   │   └── bot_logger.py      # Logger with credential masking
│   │
│   ├── order/                  # Order management
│   │   ├── README.md
│   │   └── order_manager.py   # Order creation, validation, retry logic
│   │
│   ├── scheduler/              # Automated scheduling
│   │   ├── README.md
│   │   └── scheduler.py       # Weekly execution scheduler
│   │
│   └── strategy/               # Strategy calculations
│       ├── README.md
│       └── strategy_calculator.py  # Strike and expiration calculations
│
└── tests/                       # Unit tests
    ├── README.md               # Testing documentation
    ├── test_alpaca_client.py
    ├── test_bot_logger.py
    ├── test_config_manager.py
    ├── test_order_manager.py
    ├── test_scheduler.py
    ├── test_strategy_calculator.py
    └── test_trading_bot.py
```

## Key Files

### Entry Points

- **`main.py`**: Production entry point
  - Runs the bot with scheduler for automated weekly execution
  - Supports `--once` for single execution
  - Supports `--dry-run` for testing without orders
  - Requires valid API credentials

- **`demo.py`**: Demo/simulation mode
  - Works without API credentials
  - Runs even when market is closed
  - Shows complete workflow with simulated data
  - Perfect for learning and testing

### Configuration

- **`.env`**: Store API credentials securely
  ```
  ALPACA_API_KEY=your_key
  ALPACA_API_SECRET=your_secret
  ```

- **`config/config.json`**: Trading parameters
  - Symbols to trade
  - Strike offsets and spread widths
  - Execution schedule
  - Contract quantities

### Documentation

- **`README.md`**: Main documentation with installation, usage, troubleshooting
- **`DEMO_README.md`**: Detailed demo mode guide with examples
- **`DEPLOYMENT.md`**: Production deployment, systemd, Docker, security
- **`PROJECT_STRUCTURE.md`**: This file - project organization

## Module Organization

### Core Modules

1. **Alpaca Client** (`src/alpaca/`)
   - Authenticates with Alpaca API
   - Retrieves market data (prices, option chains)
   - Checks market status
   - Submits spread orders

2. **Trading Bot** (`src/bot/`)
   - Orchestrates entire workflow
   - Initializes all components
   - Processes each symbol
   - Handles errors gracefully

3. **Strategy Calculator** (`src/strategy/`)
   - Calculates strike prices
   - Determines expiration dates
   - Finds nearest available strikes
   - Validates spread parameters

4. **Order Manager** (`src/order/`)
   - Creates spread orders
   - Validates order parameters
   - Implements retry logic
   - Handles order errors

5. **Configuration** (`src/config/`)
   - Loads JSON configuration
   - Substitutes environment variables
   - Validates all parameters
   - Provides type-safe access

6. **Logging** (`src/logging/`)
   - Structured logging
   - Credential masking
   - Log rotation
   - Trade and summary logging

7. **Scheduler** (`src/scheduler/`)
   - Weekly execution scheduling
   - Market hours calculation
   - Graceful error handling
   - Start/stop controls

## Data Flow

```
main.py
  ↓
TradingBot.initialize()
  ↓
  ├─→ ConfigManager.load_config()
  ├─→ BotLogger (initialize logging)
  ├─→ AlpacaClient.authenticate()
  ├─→ StrategyCalculator (initialize)
  └─→ OrderManager (initialize)
  ↓
TradingBot.execute_trading_cycle()
  ↓
  ├─→ AlpacaClient.is_market_open()
  ↓
  └─→ For each symbol:
      ├─→ AlpacaClient.get_current_price()
      ├─→ StrategyCalculator.calculate_strikes()
      ├─→ StrategyCalculator.calculate_expiration()
      ├─→ AlpacaClient.get_option_chain()
      ├─→ StrategyCalculator.find_nearest_strikes()
      ├─→ OrderManager.submit_order_with_error_handling()
      │   └─→ OrderManager.retry_order()
      │       └─→ AlpacaClient.submit_spread_order()
      └─→ BotLogger.log_trade()
  ↓
TradingBot._log_execution_summary()
```

## Testing

Run all tests:
```bash
pytest
```

Run specific test:
```bash
pytest tests/test_trading_bot.py
```

Run with coverage:
```bash
pytest --cov=src tests/
```

## Development Workflow

1. **Setup**: Install dependencies, configure `.env` and `config.json`
2. **Demo**: Run `python demo.py` to understand workflow
3. **Dry-Run**: Run `python main.py --dry-run --once` with real API
4. **Paper Trading**: Run `python main.py --once` with paper account
5. **Scheduled**: Run `python main.py` for automated execution
6. **Production**: Update to live endpoint after thorough testing

## Security Notes

- `.env` and `config/config.json` are in `.gitignore`
- All credentials are masked in logs
- Use separate API keys for paper and live trading
- Restrict file permissions: `chmod 600 .env config/config.json`
- See [DEPLOYMENT.md](DEPLOYMENT.md) for comprehensive security guide

## Getting Help

- Check logs in `logs/trading_bot.log`
- Review troubleshooting section in [README.md](README.md)
- Run demo mode to understand expected behavior
- Use dry-run mode to test without risk
- Verify configuration against `config.example.json`
