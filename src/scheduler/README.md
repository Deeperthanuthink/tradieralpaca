# Automated Scheduler

This module provides the `Scheduler` class for automated weekly execution of the trading bot. It calculates execution time based on market open (9:30 AM ET) plus a configurable offset, schedules the bot to run on a specific day of the week, handles execution errors gracefully without stopping the scheduler, and provides start/stop controls for the continuous execution loop. The scheduler runs in the background and checks for pending jobs every minute.
