# Configuration Management

This module handles loading, validation, and access to bot configuration. The `ConfigManager` loads JSON configuration files, substitutes environment variables (for secure credential management), and validates all parameters. The `models.py` file defines data classes for configuration structure (`Config`, `AlpacaCredentials`, `LoggingConfig`) with built-in validation rules ensuring all trading parameters, API credentials, and logging settings are valid before the bot starts.
