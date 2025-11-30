# Migration to Tradier API

The bot has been successfully migrated from Alpaca to Tradier API.

## What Changed

### API Provider
- **Old**: Alpaca Markets API
- **New**: Tradier Brokerage API

### Credentials Required

Add these to your `.env` file:

```bash
TRADIER_API_TOKEN=your_api_token_here
TRADIER_ACCOUNT_ID=your_account_id_here
```

### Configuration File

Update `config/config.json`:

```json
{
  "tradier": {
    "api_token": "${TRADIER_API_TOKEN}",
    "account_id": "${TRADIER_ACCOUNT_ID}",
    "base_url": "https://sandbox.tradier.com"
  }
}
```

### Base URLs

- **Sandbox (Testing)**: `https://sandbox.tradier.com`
- **Production (Live Trading)**: `https://api.tradier.com`

## Getting Started with Tradier

### 1. Create Account

- **Sandbox Account**: https://sandbox.tradier.com/
  - Free for testing
  - No real money
  - Full API access

- **Production Account**: https://brokerage.tradier.com/
  - Real money trading
  - Requires account approval

### 2. Get API Credentials

1. Log into your Tradier account
2. Go to **Settings** → **API Access**
3. Create a new **Access Token**
4. Copy your **Account ID** from account settings

### 3. Configure Bot

Add to `.env`:
```bash
TRADIER_API_TOKEN=your_token_from_step_2
TRADIER_ACCOUNT_ID=your_account_id_from_step_2
```

Update `config/config.json`:
```json
{
  "tradier": {
    "api_token": "${TRADIER_API_TOKEN}",
    "account_id": "${TRADIER_ACCOUNT_ID}",
    "base_url": "https://sandbox.tradier.com"
  }
}
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Test

```bash
# Test with demo mode (no API needed)
python demo.py

# Test with real API in dry-run mode
python main.py --dry-run --once

# Run for real (sandbox account)
python main.py --once
```

## Key Differences from Alpaca

### Advantages of Tradier

1. **Better Options Support**: Tradier is designed for options trading
2. **Real Options Chains**: Full access to option chains in sandbox
3. **No Paper Trading Limitations**: Sandbox works like production
4. **Simpler Authentication**: Single API token instead of key + secret

### API Differences

| Feature | Alpaca | Tradier |
|---------|--------|---------|
| Authentication | API Key + Secret | Bearer Token |
| Options Support | Limited in paper | Full in sandbox |
| Market Data | Free | Free |
| Order Types | Limited | Full options support |

## Troubleshooting

### "Authentication failed"

- Check your API token is correct
- Verify you're using the right base URL (sandbox vs production)
- Make sure token hasn't expired

### "Account ID not found"

- Verify your account ID matches your Tradier account
- Check you're using the correct account (sandbox vs production)

### "Options chain unavailable"

- Tradier sandbox should support options
- Verify the symbol has options available
- Check expiration date is valid (must be a Friday)

## Documentation

- **Tradier API Docs**: https://documentation.tradier.com/brokerage-api
- **Getting Started**: https://documentation.tradier.com/brokerage-api/getting-started
- **Options Trading**: https://documentation.tradier.com/brokerage-api/trading/getting-started

## Support

- **Tradier Support**: https://tradier.com/contact
- **API Status**: https://status.tradier.com/
- **Developer Forum**: https://community.tradier.com/

## Migration Checklist

- [ ] Create Tradier sandbox account
- [ ] Get API token and account ID
- [ ] Update `.env` file with Tradier credentials
- [ ] Update `config/config.json` with Tradier settings
- [ ] Install new dependencies: `pip install -r requirements.txt`
- [ ] Test with demo mode: `python demo.py`
- [ ] Test with dry-run: `python main.py --dry-run --once`
- [ ] Verify orders in Tradier dashboard
- [ ] (Optional) Switch to production when ready
