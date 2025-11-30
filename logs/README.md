# Log Files

This directory stores all bot log files. The main log file `trading_bot.log` contains detailed execution logs including initialization, authentication, market checks, price retrieval, strike calculations, order submissions, and execution summaries. Logs automatically rotate when they reach 10MB (keeping 5 backups). All sensitive information (API keys, secrets) is automatically masked in logs. Review logs here to monitor bot activity, debug issues, and track trading performance.
