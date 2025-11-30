# Demo Mode

The demo mode (`demo.py`) provides a complete simulation of the trading bot's workflow using realistic data, without making actual API calls or placing real orders. This is perfect for understanding how the bot works, especially when the market is closed.

## Running Demo Mode

```bash
python demo.py
```

Or with a custom configuration:

```bash
python demo.py --config path/to/config.json
```

## What Demo Mode Shows

### 1. Configuration Display
- All configured trading parameters
- Symbols to trade
- Strike offsets and spread widths
- Execution schedule
- API endpoint

### 2. Market Status Check
- Current market status (open/closed)
- Next market open time if closed
- Explanation of market hours

### 3. Complete Trading Workflow for Each Symbol

For each configured symbol, the demo shows:

- **Current Price**: Simulated current market price
- **Strike Calculation**: 
  - Short put strike (X% below market)
  - Long put strike (short strike - spread width)
  - Actual spread width
- **Expiration Date**: Calculated Friday of target week
- **Days to Expiration**: Time until options expire
- **Option Chain Lookup**: Simulated available strikes
- **Strike Adjustment**: Shows if calculated strikes need adjustment to nearest available
- **Trade Details**:
  - Strategy type (Put Credit Spread)
  - Exact strikes for sell and buy puts
  - Number of contracts
  - Estimated credit received (premium)
  - Maximum risk and profit
  - Probability of profit estimate
- **Order Submission**: Simulated order with success/failure

### 4. Execution Summary

- Total symbols processed
- Success/failure counts
- Success rate percentage
- Total credit received across all trades
- Detailed results for each symbol

## Example Output

```
======================================================================
DEMO MODE - Simulating Trading Cycle
======================================================================

CONFIGURATION:
  Symbols: NVDA, GOOGL, AAPL, MSFT
  Strike Offset: 5.0% below market
  Spread Width: $5.0
  Contract Quantity: 1
  Execution Day: Tuesday
  Execution Time: Market open + 30 minutes
  Expiration: 1 week(s) out

MARKET STATUS CHECK:
  Market is CLOSED (Outside trading hours)
  [DEMO MODE: Proceeding with simulation regardless of market status]

──────────────────────────────────────────────────────────────────────
Processing: AAPL
──────────────────────────────────────────────────────────────────────
  Current Price: $185.50
  Calculated Short Strike: $176.00
  Calculated Long Strike: $171.00
  Spread Width: $5.00
  Expiration Date: 2025-12-05 (Friday)
  Days to Expiration: 10

  Simulating option chain lookup...
  Found 26 available strikes
  Adjusted to nearest available strikes:
    Short Strike: $176.00 → $175.00
    Long Strike: $171.00 → $170.00

  TRADE DETAILS:
    Strategy: Put Credit Spread
    Sell Put: $175.00 (higher strike)
    Buy Put: $170.00 (lower strike)
    Spread Width: $5.00
    Contracts: 1
    Estimated Credit: $1.32 per spread
    Total Credit: $1.32
    Max Risk: $500.00
    Max Profit: $132.00
    Short Strike OTM: 5.7%
    Est. Probability of Profit: ~78%

  Simulating order submission...
  ✓ Order submitted successfully
    Order ID: DEMO-AAPL-20251125200436
    Status: FILLED (simulated)
    Fill Price: $1.32

[... continues for each symbol ...]

EXECUTION SUMMARY
  Total Symbols: 4
  Successful: 3
  Failed: 1
  Success Rate: 75.0%
  Total Credit Received: $513.00

DETAILED RESULTS:
  ✓ AAPL: $175.00/$170.00 spread for $132.00 credit
  ✓ MSFT: $400.00/$395.00 spread for $381.00 credit
  ✗ GOOGL: Failed - Insufficient buying power
  ✓ NVDA: $830.00/$825.00 spread for $0.00 credit
```

## Use Cases

### Learning
- Understand how put credit spreads work
- See the complete decision-making process
- Learn about strike selection and option chains
- Understand risk/reward calculations

### Testing Configuration
- Verify your configuration is correct
- See what strikes would be selected for your parameters
- Check if spread widths are appropriate
- Validate symbol selections

### Development
- Test changes without API calls
- Debug workflow issues
- Verify calculations
- Test error handling

### Demonstrations
- Show others how the bot works
- Explain the trading strategy
- Present without needing market hours
- Educational purposes

## Differences from Real Execution

Demo mode differs from real execution in these ways:

1. **No API Calls**: Doesn't connect to Alpaca API
2. **Simulated Prices**: Uses pre-defined or generated prices
3. **Simulated Option Chains**: Generates realistic but fake option strikes
4. **Simulated Orders**: Order submission is simulated (95% success rate)
5. **No Authentication**: Doesn't require valid API credentials
6. **Works Anytime**: Runs even when market is closed

## Transitioning to Real Trading

After running demo mode and understanding the workflow:

1. **Test with Dry-Run**: `python main.py --dry-run --once`
   - Uses real API and real market data
   - Doesn't submit actual orders
   - Requires valid API credentials

2. **Test with Paper Trading**: `python main.py --once`
   - Uses real API with paper trading account
   - Submits real orders to paper account
   - No real money at risk

3. **Live Trading**: Update config to live endpoint
   - Only after thorough testing
   - Start with small position sizes
   - Monitor closely

## Notes

- Demo mode automatically sets dummy API credentials if none are configured
- All data is simulated and for demonstration purposes only
- Success/failure rates in demo are randomized (95% success)
- Estimated premiums are calculated using typical ranges
- No actual financial transactions occur in demo mode

## See Also

- [Main README](README.md) - Full bot documentation
- [Deployment Guide](DEPLOYMENT.md) - Production deployment
- [Configuration Guide](config/README.md) - Configuration options
