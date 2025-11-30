# Multi-Broker Setup Guide

The bot now supports **both Alpaca and Tradier** brokers through Lumibot! You can easily switch between them by changing one configuration setting.

## Supported Brokers

1. **Alpaca** - Popular broker with paper trading
2. **Tradier** - Options-focused broker with sandbox

Both use the **Lumibot framework** for unified trading interface.

## Quick Start

### 1. Choose Your Broker

Edit `config/config.json` and set `broker_type`:

```json
{
  "broker_type": "tradier",  // or "alpaca"
  ...
}
```

### 2. Set Credentials

Add to `.env`:

**For Alpaca:**
```bash
ALPACA_API_KEY=your_key
ALPACA_API_SECRET=your_secret
```

**For Tradier:**
```bash
TRADIER_API_TOKEN=your_token
TRADIER_ACCOUNT_ID=your_account_id
```

### 3. Run

```bash
python main.py --once
```

The bot automatically uses the broker you specified!

## Configuration

### Using Alpaca

`config/config.json`:
```json
{
  "broker_type": "alpaca",
  "alpaca": {
    "api_key": "${ALPACA_API_KEY}",
    "api_secret": "${ALPACA_API_SECRET}",
    "paper": true
  }
}
```

`.env`:
```bash
ALPACA_API_KEY=PK...
ALPACA_API_SECRET=...
```

### Using Tradier

`config/config.json`:
```json
{
  "broker_type": "tradier",
  "tradier": {
    "api_token": "${TRADIER_API_TOKEN}",
    "account_id": "${TRADIER_ACCOUNT_ID}",
    "base_url": "https://sandbox.tradier.com"
  }
}
```

`.env`:
```bash
TRADIER_API_TOKEN=...
TRADIER_ACCOUNT_ID=...
```

## Switching Brokers

To switch from one broker to another:

1. Update `broker_type` in `config/config.json`
2. Ensure credentials are in `.env`
3. Restart the bot

That's it! No code changes needed.

## Broker Comparison

| Feature | Alpaca | Tradier |
|---------|--------|---------|
| **Paper Trading** | Yes (free) | Sandbox (free) |
| **Options Support** | Limited | Full |
| **Market Data** | Free | Free |
| **Setup Difficulty** | Easy | Easy |
| **Best For** | Stock trading | Options trading |

## Getting Credentials

### Alpaca

1. Sign up at https://alpaca.markets/
2. Go to Paper Trading dashboard
3. Generate API keys
4. Copy Key ID and Secret Key

### Tradier

1. Sign up at https://sandbox.tradier.com/
2. Go to Settings → API Access
3. Create Access Token
4. Copy Token and Account ID

## Example Configurations

### Development (Paper/Sandbox)

```json
{
  "broker_type": "alpaca",  // or "tradier"
  "alpaca": {
    "paper": true  // Use paper trading
  },
  "tradier": {
    "base_url": "https://sandbox.tradier.com"  // Use sandbox
  }
}
```

### Production (Live Trading)

```json
{
  "broker_type": "tradier",
  "tradier": {
    "base_url": "https://api.tradier.com"  // Live trading
  }
}
```

## Testing Both Brokers

You can keep credentials for both brokers in `.env`:

```bash
# Alpaca
ALPACA_API_KEY=...
ALPACA_API_SECRET=...

# Tradier
TRADIER_API_TOKEN=...
TRADIER_ACCOUNT_ID=...
```

Then switch by changing `broker_type` in config!

## Architecture

The bot uses a **broker factory pattern**:

```
Config → BrokerFactory → AlpacaClient or TradierClient
                              ↓
                         BaseBrokerClient
                              ↓
                         Lumibot Framework
```

All brokers implement the same interface, so the rest of the code doesn't need to know which broker is being used!

## Benefits

1. **Flexibility**: Switch brokers anytime
2. **Unified Interface**: Same code works with both
3. **Easy Testing**: Test with different brokers
4. **Future-Proof**: Easy to add more brokers
5. **Lumibot Power**: Get all Lumibot features with any broker

## Troubleshooting

### "Unsupported broker type"

Check `broker_type` in config.json. Must be "alpaca" or "tradier".

### "Credentials required"

Ensure credentials for your chosen broker are in `.env`.

### "Authentication failed"

- Verify credentials are correct
- Check broker type matches credentials
- For Alpaca: Verify paper trading is enabled
- For Tradier: Verify using sandbox URL for sandbox account

## Advanced: Adding More Brokers

To add a new broker:

1. Create `src/brokers/newbroker_client.py`
2. Inherit from `BaseBrokerClient`
3. Implement all abstract methods
4. Add to `BrokerFactory.create_broker()`
5. Update config models

The framework makes it easy to support any broker Lumibot supports!

## Summary

✅ **Two brokers supported**: Alpaca and Tradier  
✅ **Easy switching**: Change one config setting  
✅ **Unified interface**: Same code for both  
✅ **Lumibot powered**: Best-in-class trading framework  
✅ **Future-ready**: Easy to add more brokers  

Choose the broker that works best for you!
