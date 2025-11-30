# Deployment Guide

This guide provides detailed instructions for deploying the Options Trading Bot in various environments, including running it as a background service and implementing security best practices.

## Table of Contents

1. [Environment Setup](#environment-setup)
2. [Running as a Background Service](#running-as-a-background-service)
3. [Security Best Practices](#security-best-practices)
4. [Monitoring and Maintenance](#monitoring-and-maintenance)
5. [Troubleshooting Deployment Issues](#troubleshooting-deployment-issues)

## Environment Setup

### Prerequisites

- **Python**: Version 3.9 or higher
- **Operating System**: Linux (Ubuntu/Debian recommended), macOS, or Windows
- **Alpaca Account**: Paper trading or live trading account with API access
- **Network**: Stable internet connection for API communication

### Step 1: System Preparation

#### Linux (Ubuntu/Debian)

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+ and pip
sudo apt install python3 python3-pip python3-venv -y

# Install system dependencies
sudo apt install git -y
```

#### macOS

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.9+
brew install python@3.9

# Verify installation
python3 --version
```

#### Windows

1. Download Python 3.9+ from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Verify installation: `python --version`

### Step 2: Clone and Setup Project

```bash
# Clone the repository (or download the source code)
cd /opt  # Or your preferred installation directory
git clone <repository-url> options-trading-bot
cd options-trading-bot

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 3: Configuration

```bash
# Create configuration from example
cp config/config.example.json config/config.json
cp .env.example .env

# Edit configuration files
nano config/config.json  # Or use your preferred editor
nano .env
```

#### Configure API Credentials

Edit `.env` file:

```bash
ALPACA_API_KEY=your_paper_trading_api_key_here
ALPACA_API_SECRET=your_paper_trading_api_secret_here
```

#### Configure Trading Parameters

Edit `config/config.json`:

```json
{
  "symbols": ["NVDA", "GOOGL", "AAPL", "MSFT"],
  "strike_offset_percent": 5.0,
  "spread_width": 5.0,
  "contract_quantity": 1,
  "execution_day": "Tuesday",
  "execution_time_offset_minutes": 30,
  "expiration_offset_weeks": 1,
  "alpaca": {
    "api_key": "${ALPACA_API_KEY}",
    "api_secret": "${ALPACA_API_SECRET}",
    "base_url": "https://paper-api.alpaca.markets"
  },
  "logging": {
    "level": "INFO",
    "file_path": "logs/trading_bot.log"
  }
}
```

### Step 4: Test Installation

```bash
# Test with dry-run mode
python main.py --dry-run --once

# Verify logs
cat logs/trading_bot.log
```

## Running as a Background Service

### Option 1: systemd Service (Linux - Recommended)

systemd is the standard init system for most modern Linux distributions and provides robust process management.

#### Create Service File

Create `/etc/systemd/system/options-trading-bot.service`:

```bash
sudo nano /etc/systemd/system/options-trading-bot.service
```

Add the following content:

```ini
[Unit]
Description=Options Trading Bot
After=network.target

[Service]
Type=simple
User=your_username
Group=your_username
WorkingDirectory=/opt/options-trading-bot
Environment="PATH=/opt/options-trading-bot/venv/bin"
ExecStart=/opt/options-trading-bot/venv/bin/python main.py --config /opt/options-trading-bot/config/config.json
Restart=on-failure
RestartSec=10
StandardOutput=append:/opt/options-trading-bot/logs/service.log
StandardError=append:/opt/options-trading-bot/logs/service_error.log

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/options-trading-bot/logs

[Install]
WantedBy=multi-user.target
```

#### Configure and Start Service

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable options-trading-bot

# Start the service
sudo systemctl start options-trading-bot

# Check service status
sudo systemctl status options-trading-bot

# View service logs
sudo journalctl -u options-trading-bot -f
```

#### Service Management Commands

```bash
# Stop the service
sudo systemctl stop options-trading-bot

# Restart the service
sudo systemctl restart options-trading-bot

# Disable auto-start on boot
sudo systemctl disable options-trading-bot

# View recent logs
sudo journalctl -u options-trading-bot -n 100

# View logs since specific time
sudo journalctl -u options-trading-bot --since "2025-01-01 00:00:00"
```

### Option 2: Docker Container

Docker provides isolation and portability for deployment.

#### Create Dockerfile

Create `Dockerfile` in project root:

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Run as non-root user
RUN useradd -m -u 1000 botuser && chown -R botuser:botuser /app
USER botuser

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]
```

#### Create docker-compose.yml

```yaml
version: '3.8'

services:
  trading-bot:
    build: .
    container_name: options-trading-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
    environment:
      - TZ=America/New_York
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

#### Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down

# Restart the container
docker-compose restart
```

### Option 3: Screen/tmux (Quick Setup)

For quick deployment or testing, use screen or tmux.

#### Using screen

```bash
# Install screen
sudo apt install screen -y  # Linux
brew install screen         # macOS

# Start a new screen session
screen -S trading-bot

# Activate virtual environment and run bot
cd /opt/options-trading-bot
source venv/bin/activate
python main.py

# Detach from screen: Press Ctrl+A, then D

# Reattach to screen
screen -r trading-bot

# List all screen sessions
screen -ls

# Kill screen session
screen -X -S trading-bot quit
```

#### Using tmux

```bash
# Install tmux
sudo apt install tmux -y  # Linux
brew install tmux         # macOS

# Start a new tmux session
tmux new -s trading-bot

# Activate virtual environment and run bot
cd /opt/options-trading-bot
source venv/bin/activate
python main.py

# Detach from tmux: Press Ctrl+B, then D

# Reattach to tmux
tmux attach -t trading-bot

# List all tmux sessions
tmux ls

# Kill tmux session
tmux kill-session -t trading-bot
```

### Option 4: Supervisor (Alternative Process Manager)

Supervisor is a process control system for Unix-like operating systems.

#### Install Supervisor

```bash
sudo apt install supervisor -y
```

#### Create Supervisor Configuration

Create `/etc/supervisor/conf.d/options-trading-bot.conf`:

```ini
[program:options-trading-bot]
command=/opt/options-trading-bot/venv/bin/python main.py
directory=/opt/options-trading-bot
user=your_username
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/options-trading-bot/logs/supervisor.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=5
environment=PATH="/opt/options-trading-bot/venv/bin"
```

#### Manage with Supervisor

```bash
# Reload supervisor configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start the program
sudo supervisorctl start options-trading-bot

# Stop the program
sudo supervisorctl stop options-trading-bot

# Restart the program
sudo supervisorctl restart options-trading-bot

# Check status
sudo supervisorctl status options-trading-bot

# View logs
sudo supervisorctl tail -f options-trading-bot
```

## Security Best Practices

### 1. Credential Management

#### Never Commit Credentials

```bash
# Verify .gitignore includes sensitive files
cat .gitignore

# Should include:
# .env
# config/config.json
# *.log
```

#### Use Environment Variables

Always store API credentials in `.env` file, never hardcode them:

```bash
# Good: Using environment variables
ALPACA_API_KEY=your_key_here
ALPACA_API_SECRET=your_secret_here

# Bad: Hardcoding in config.json
# "api_key": "PKXXXXXXXXXXXXXXXX"  # DON'T DO THIS
```

#### Restrict File Permissions

```bash
# Set restrictive permissions on sensitive files
chmod 600 .env
chmod 600 config/config.json

# Verify permissions
ls -la .env config/config.json

# Should show: -rw------- (only owner can read/write)
```

### 2. API Key Security

#### Use Separate Keys for Paper and Live Trading

- Create separate API keys for paper trading and live trading
- Never use live trading keys during development/testing
- Rotate keys regularly (every 90 days recommended)

#### Limit API Key Permissions

In your Alpaca account:
1. Create API keys with minimum required permissions
2. Enable IP whitelisting if possible
3. Set appropriate rate limits

#### Rotate Keys Regularly

```bash
# Steps to rotate API keys:
# 1. Generate new keys in Alpaca dashboard
# 2. Update .env file with new keys
# 3. Restart the bot
# 4. Verify bot is working with new keys
# 5. Delete old keys from Alpaca dashboard
```

### 3. System Security

#### Run as Non-Root User

```bash
# Create dedicated user for the bot
sudo useradd -r -s /bin/false tradingbot

# Change ownership of bot directory
sudo chown -R tradingbot:tradingbot /opt/options-trading-bot

# Update systemd service to use this user
# Edit /etc/systemd/system/options-trading-bot.service
# User=tradingbot
# Group=tradingbot
```

#### Enable Firewall

```bash
# Ubuntu/Debian
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow out 443/tcp  # HTTPS for Alpaca API

# Verify firewall status
sudo ufw status
```

#### Keep System Updated

```bash
# Regular system updates
sudo apt update && sudo apt upgrade -y

# Update Python packages
source venv/bin/activate
pip list --outdated
pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

### 4. Logging Security

#### Ensure Credentials Are Not Logged

The bot automatically masks sensitive information in logs, but verify:

```bash
# Check logs for exposed credentials
grep -i "api_key\|api_secret\|password" logs/trading_bot.log

# Should show ***MASKED*** instead of actual values
```

#### Implement Log Rotation

Log rotation is built-in (10MB max, 5 backups), but you can also use logrotate:

Create `/etc/logrotate.d/options-trading-bot`:

```
/opt/options-trading-bot/logs/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 tradingbot tradingbot
    sharedscripts
    postrotate
        systemctl reload options-trading-bot > /dev/null 2>&1 || true
    endscript
}
```

### 5. Network Security

#### Use HTTPS Only

The bot is configured to use HTTPS by default. Verify in config:

```json
"base_url": "https://paper-api.alpaca.markets"  // Note: https://
```

#### Monitor Network Traffic

```bash
# Monitor outgoing connections
sudo netstat -tupn | grep python

# Should only show connections to Alpaca API endpoints
```

## Monitoring and Maintenance

### 1. Log Monitoring

#### View Real-Time Logs

```bash
# systemd service
sudo journalctl -u options-trading-bot -f

# Direct log file
tail -f logs/trading_bot.log

# Docker
docker-compose logs -f
```

#### Search Logs for Errors

```bash
# Find all errors
grep -i "error" logs/trading_bot.log

# Find failed trades
grep -i "failed" logs/trading_bot.log

# Find specific symbol
grep "AAPL" logs/trading_bot.log
```

### 2. Health Checks

#### Create Health Check Script

Create `scripts/health_check.sh`:

```bash
#!/bin/bash

LOG_FILE="/opt/options-trading-bot/logs/trading_bot.log"
MAX_AGE_MINUTES=120  # Alert if no log entries in last 2 hours

# Check if log file exists
if [ ! -f "$LOG_FILE" ]; then
    echo "ERROR: Log file not found"
    exit 1
fi

# Check last log entry timestamp
LAST_LOG=$(tail -n 1 "$LOG_FILE" | grep -oP '\[\K[^\]]+')
LAST_LOG_EPOCH=$(date -d "$LAST_LOG" +%s 2>/dev/null)
CURRENT_EPOCH=$(date +%s)

if [ -z "$LAST_LOG_EPOCH" ]; then
    echo "WARNING: Could not parse last log timestamp"
    exit 1
fi

AGE_MINUTES=$(( ($CURRENT_EPOCH - $LAST_LOG_EPOCH) / 60 ))

if [ $AGE_MINUTES -gt $MAX_AGE_MINUTES ]; then
    echo "ERROR: Bot appears inactive (last log: $AGE_MINUTES minutes ago)"
    exit 1
fi

# Check for recent errors
RECENT_ERRORS=$(tail -n 100 "$LOG_FILE" | grep -c "ERROR")

if [ $RECENT_ERRORS -gt 5 ]; then
    echo "WARNING: $RECENT_ERRORS errors in last 100 log entries"
    exit 1
fi

echo "OK: Bot is healthy"
exit 0
```

#### Schedule Health Checks

```bash
# Make script executable
chmod +x scripts/health_check.sh

# Add to crontab (run every hour)
crontab -e

# Add line:
0 * * * * /opt/options-trading-bot/scripts/health_check.sh >> /opt/options-trading-bot/logs/health_check.log 2>&1
```

### 3. Backup Strategy

#### Backup Configuration

```bash
# Create backup script
cat > scripts/backup_config.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/trading-bot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Backup configuration (excluding sensitive .env)
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" \
    config/config.json \
    --exclude=.env

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "config_*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/config_$DATE.tar.gz"
EOF

chmod +x scripts/backup_config.sh

# Schedule daily backups
crontab -e
# Add: 0 2 * * * /opt/options-trading-bot/scripts/backup_config.sh
```

### 4. Performance Monitoring

#### Monitor Resource Usage

```bash
# Check CPU and memory usage
ps aux | grep python

# Monitor with htop
htop -p $(pgrep -f "python main.py")

# Check disk usage
df -h /opt/options-trading-bot
du -sh /opt/options-trading-bot/logs
```

### 5. Alerting

#### Email Alerts on Failures

Install and configure mail utility:

```bash
# Install mailutils
sudo apt install mailutils -y

# Test email
echo "Test email" | mail -s "Trading Bot Test" your-email@example.com
```

Modify systemd service to send email on failure:

```ini
[Unit]
Description=Options Trading Bot
After=network.target
OnFailure=trading-bot-failure@%n.service

[Service]
# ... existing configuration ...
```

Create failure notification service `/etc/systemd/system/trading-bot-failure@.service`:

```ini
[Unit]
Description=Trading Bot Failure Notification

[Service]
Type=oneshot
ExecStart=/bin/bash -c 'echo "Trading bot service %i failed" | mail -s "Trading Bot Alert" your-email@example.com'
```

## Troubleshooting Deployment Issues

### Service Won't Start

```bash
# Check service status
sudo systemctl status options-trading-bot

# View detailed logs
sudo journalctl -u options-trading-bot -n 100 --no-pager

# Check for Python errors
python main.py --config config/config.json --once

# Verify file permissions
ls -la /opt/options-trading-bot
ls -la /opt/options-trading-bot/config
```

### Permission Denied Errors

```bash
# Fix ownership
sudo chown -R tradingbot:tradingbot /opt/options-trading-bot

# Fix permissions
chmod 755 /opt/options-trading-bot
chmod 644 /opt/options-trading-bot/main.py
chmod 600 /opt/options-trading-bot/.env
chmod 600 /opt/options-trading-bot/config/config.json
chmod 755 /opt/options-trading-bot/logs
```

### Bot Not Executing on Schedule

```bash
# Verify system time and timezone
date
timedatectl

# Set timezone to US/Eastern
sudo timedatectl set-timezone America/New_York

# Check scheduler logs
grep -i "scheduler" logs/trading_bot.log

# Test manual execution
python main.py --once
```

### High Memory Usage

```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Restart service to clear memory
sudo systemctl restart options-trading-bot

# Consider adding memory limits to systemd service:
# MemoryMax=512M
# MemoryHigh=400M
```

### Log Files Growing Too Large

```bash
# Check log file sizes
du -sh logs/*

# Manually rotate logs
cd logs
mv trading_bot.log trading_bot.log.$(date +%Y%m%d)
gzip trading_bot.log.$(date +%Y%m%d)

# Restart bot to create new log file
sudo systemctl restart options-trading-bot
```

## Production Deployment Checklist

Before deploying to production with live trading:

- [ ] Test thoroughly in paper trading environment for at least 2 weeks
- [ ] Verify all trades execute correctly and at expected times
- [ ] Review and understand all configuration parameters
- [ ] Set up monitoring and alerting
- [ ] Configure log rotation and backups
- [ ] Implement security best practices (file permissions, firewall, etc.)
- [ ] Create separate API keys for production
- [ ] Update `base_url` to live trading endpoint: `https://api.alpaca.markets`
- [ ] Start with small position sizes (contract_quantity: 1)
- [ ] Monitor first few executions closely
- [ ] Have a plan for emergency shutdown
- [ ] Document your deployment configuration
- [ ] Set up regular review schedule for bot performance

## Support and Resources

- **Alpaca API Documentation**: https://alpaca.markets/docs/
- **Python Documentation**: https://docs.python.org/3/
- **systemd Documentation**: https://www.freedesktop.org/software/systemd/man/
- **Docker Documentation**: https://docs.docker.com/

## License

This deployment guide is provided as-is for educational and personal use.
