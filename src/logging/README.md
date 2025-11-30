# Structured Logging

This module provides the `BotLogger` class for comprehensive, secure logging throughout the bot. It automatically masks sensitive information (API keys, secrets, tokens) in all log messages, supports structured logging with context dictionaries, implements log rotation (10MB max, 5 backups), and provides specialized methods for logging trades and execution summaries. Logs are written to both file and console with configurable verbosity levels.
