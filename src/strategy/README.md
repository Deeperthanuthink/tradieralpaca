# Strategy Calculator

This module contains the `StrategyCalculator` class for calculating put credit spread parameters. It calculates short strike prices (percentage below market price), long strike prices (short strike minus spread width), expiration dates (Friday of target week), finds nearest available strikes from option chains, and validates all spread parameters to ensure they meet trading requirements. The calculator ensures all calculations are mathematically sound and within configured risk parameters.
