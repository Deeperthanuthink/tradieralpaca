# Order Management

This module manages order creation, validation, and execution with robust error handling. The `OrderManager` creates put credit spread orders, validates all parameters before submission, implements retry logic with exponential backoff for transient failures, distinguishes between retryable and non-retryable errors, and ensures that order failures are properly logged and reported. It supports dry-run mode for testing without submitting actual orders.
