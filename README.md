Optiflow is a Python project for studying options market activity and positioning using live data from the Schwab API (via schwab-py). It is organized around a shared data pipeline, with analysis modules built on top of it.

# Modules

Data pipeline: pulls and stores SPY option chains (working)
Volume flow: per-strike changes in cumulative volume, compared with a time-of-day baseline (in progress)
Greek exposure: gamma and delta exposure and call/put walls (planned / in progress)
Pricing models: Black-Scholes and implied volatility, validated against the API's values (planned)
