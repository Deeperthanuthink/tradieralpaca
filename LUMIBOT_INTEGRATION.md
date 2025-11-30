# Lumibot Integration with Tradier

The bot now uses **Lumibot** as the trading framework with **Tradier** as the broker. This provides a more robust and feature-rich trading experience.

## What is Lumibot?

Lumibot is a Python trading framework that provides:
- **Backtesting**: Test strategies on historical data
- **Live Trading**: Execute trades with multiple brokers
- **Paper Trading**: Practice with simulated money
- **Built-in Tradier Support**: Native integration with Tradier API

## Benefits

### Over Direct API Calls
1. **Simplified Order Management**: Lumibot handles complex order types
2. **Better Error Handling**: Built-in retry logic and error recovery
3. **Backtesting Capability**: Test strategies before going live
4. **Position Tracking**: Automatic position and portfolio management
5. **Market Data**: Unified interface for quotes and historical data

### Tradier + Lumibot Advantages
1. **Full Options Support**: Complete options trading capabilities
2. **Real-time Data**: Live market data in sandbox and production
3. **No Paper Trading Limitations**: Sandbox works like production
4. **Lower Costs**: Competitive commission structure

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `lumibot` - Trading framework
- `schedule` - Task scheduling
- `python-dotenv` - Environment variable management

### 2. Get Tradier Credentials

**Sandbox (Free Testing)**:
1. Sign up at https://sandbox.tradier.com/
2. Go to Settings → API Access
3. Create an Access Token
4. Note your Account ID

**Production (Real Trading)**:
1. Open account at https://brokerage.tradier.com/
2. Complete account approval
3. Generate API token
4. Use your account number

### 3. Configure Environment

Add to `.env`:
```bash
TRADIER_API_TOKEN=your_access_token_here
TRADIER_ACCOUNT_ID=your_account_id_here
```

### 4. Update Configuration

`config/config.json`:
```json
{
  "tradier": {
    "api_token": "${TRADIER_API_TOKEN}",
    "account_id": "${TRADIER_ACCOUNT_ID}",
    "base_url": "https://sandbox.tradier.com"
  }
}
```

**Base URLs**:
- Sandbox: `https://sandbox.tradier.com`
- Production: `https://api.tradier.com`

## Usage

### Demo Mode (No API Required)
```bash
python demo.py
```
Simulates trading with fake data.

### Dry-Run Mode (Real Data, No Orders)
```bash
python main.py --dry-run --once
```
Uses real market data but doesn't submit orders.

### Live Trading (Sandbox)
```bash
python main.py --once
```
Submits real orders to sandbox account.

### Scheduled Trading
```bash
python main.py
```
Runs on schedule (daily or weekly).

## Features

### Market Data
- Real-time quotes via Lumibot
- Option chains with all strikes
- Market hours checking
- Historical data access

### Order Execution
- Put credit spreads (sell put + buy put)
- Market and limit orders
- GTC (Good-Til-Canceled) support
- Multi-leg option strategies

### Account Management
- Cash balance tracking
- Buying power calculation
- Portfolio value monitoring
- Position tracking

## Lumibot-Specific Features

### Backtesting (Future Enhancement)

You can backtest strategies using Lumibot:

```python
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies import Strategy

class PutCreditSpreadStrategy(Strategy):
    def initialize(self):
        self.sleeptime = "1D"
    
    def on_trading_iteration(self):
        # Your strategy logic here
        pass

# Backtest
strategy = PutCreditSpreadStrategy()
results = strategy.backtest(
    YahooDataBacktesting,
    start_date="2023-01-01",
    end_date="2024-01-01"
)
```

### Live Strategy (Alternative Approach)

Instead of scheduled execution, you can run as a Lumibot strategy:

```python
from lumibot.strategies import Strategy
from lumibot.traders import Trader

class PutCreditSpreadStrategy(Strategy):
    def initialize(self):
        self.sleeptime = "1D"  # Run once per day
    
    def on_trading_iteration(self):
        # Your trading logic
        pass

# Run live
trader = Trader()
strategy = PutCreditSpreadStrategy(broker=tradier_broker)
trader.add_strategy(strategy)
trader.run_all()
```

## Troubleshooting

### "Module 'lumibot' not found"
```bash
pip install lumibot
```

### "Authentication failed"
- Verify API token is correct
- Check account ID matches your Tradier account
- Ensure you're using correct base URL (sandbox vs production)

### "Options not available"
- Tradier sandbox fully supports options
- Verify symbol has options (use major stocks like AAPL, MSFT)
- Check expiration date is valid (must be a Friday)

### "Order rejected"
- Check buying power is sufficient
- Verify strikes are available in option chain
- Ensure market is open (or use GTC orders)

## Documentation

- **Lumibot Docs**: https://lumibot.lumiwealth.com/
- **Lumibot GitHub**: https://github.com/Lumiwealth/lumibot
- **Tradier API**: https://documentation.tradier.com/
- **Tradier + Lumibot**: https://lumibot.lumiwealth.com/brokers.tradier.html

## Comparison

| Feature | Direct API | Lumibot |
|---------|-----------|---------|
| Setup Complexity | Medium | Easy |
| Order Management | Manual | Automatic |
| Error Handling | Custom | Built-in |
| Backtesting | Not Available | Built-in |
| Position Tracking | Manual | Automatic |
| Multi-Broker | No | Yes |
| Learning Curve | Steep | Gentle |

## Next Steps

1. **Test in Sandbox**: Verify everything works with sandbox account
2. **Monitor Orders**: Check Tradier dashboard for order status
3. **Review Logs**: Check `logs/trading_bot.log` for details
4. **Backtest Strategy**: Use Lumibot to test on historical data
5. **Go Live**: Switch to production when ready

## Support

- **Lumibot Discord**: https://discord.gg/lumibot
- **Tradier Support**: https://tradier.com/contact
- **GitHub Issues**: Report bugs and request features

## Migration from Direct API

The bot automatically uses Lumibot now. No code changes needed!

Key differences:
- Orders are managed by Lumibot
- Better error handling and retries
- Automatic position tracking
- Ready for backtesting

Everything else works the same way!
