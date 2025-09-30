"""
Estimator computation for MVO study.
"""
import numpy as np
import pandas as pd
from pypfopt import expected_returns, risk_models
from config import EMA_SPAN

# Compute EMA expected returns (annualized)
def compute_ema_returns(returns_df):
    # Treat input as returns data (not prices)
    ema = expected_returns.ema_historical_return(
        returns_df, returns_data=True, span=EMA_SPAN, frequency=12
    )
    return ema

# Compute mean expected returns (annualized)
def compute_mean_returns(returns_df):
    # Treat input as returns data (not prices)
    mean = expected_returns.mean_historical_return(
        returns_df, returns_data=True, frequency=12
    )
    return mean

# Compute sample covariance (annualized)
def compute_sample_cov(returns_df):
    cov = risk_models.sample_cov(
        returns_df, returns_data=True, frequency=12, fix_method="spectral"
    )
    return cov

# Compute Ledoit–Wolf shrinkage covariance (annualized)
def compute_ledoit_wolf_cov(returns_df):
    # Prefer constant-variance target; fall back to sample covariance if it fails
    try:
        cov = risk_models.CovarianceShrinkage(returns_df, frequency=12).ledoit_wolf(
            shrinkage_target="constant_variance"
        )
        return cov
    except Exception:
        return risk_models.sample_cov(returns_df, frequency=12)
