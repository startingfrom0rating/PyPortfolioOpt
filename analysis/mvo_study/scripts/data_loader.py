"""
Data loading and preprocessing for MVO study.
"""
import pandas as pd
import numpy as np
from config import ETF_RETURNS_FILE, TREASURY_RETURNS_FILE, ETF_IDENTIFIERS_FILE, ETF_INVALID_FILE, TREASURY_MAP_FILE, ETF_WHITELIST_FILE

# Helper: Load ETF returns and filter to approved

def load_etf_returns():
    etf_returns = pd.read_csv(ETF_RETURNS_FILE, index_col=0, parse_dates=True)
    # Use explicit whitelist if present; fallback to legacy file; else identifiers or all
    approved = None
    for candidate in [ETF_WHITELIST_FILE, ETF_INVALID_FILE, ETF_IDENTIFIERS_FILE, None]:
        try:
            if candidate is None:
                break
            df = pd.read_csv(candidate)
            if 'ticker' in df.columns:
                wl = set(str(x).strip() for x in df['ticker'].dropna().unique())
                if len(wl) > 0:
                    approved = wl
                    break
        except Exception:
            continue
    if approved is None:
        approved = set(etf_returns.columns)
    if approved is None:
        # Fallback to identifiers list if available; else keep all
        try:
            identifiers = pd.read_csv(ETF_IDENTIFIERS_FILE)
            idset = set(str(x).strip() for x in identifiers['ticker'].dropna().unique())
            approved = idset if len(idset) > 0 else set(etf_returns.columns)
        except Exception:
            approved = set(etf_returns.columns)
    # Filter to approved list and also existing columns
    cols = [c for c in etf_returns.columns if c in approved]
    etf_returns = etf_returns[cols]
    # Resample to month-end compounded returns
    etf_returns = (1 + etf_returns).resample('ME').prod() - 1
    # Clean: drop columns with >30% NaN, replace infs with NaN; leave NaNs for strict row-wise drop later
    etf_returns = etf_returns.loc[:, etf_returns.isnull().mean() < 0.3]
    etf_returns = etf_returns.replace([np.inf, -np.inf], np.nan)
    return etf_returns

# Helper: Load Treasury returns and map to approved

def load_treasury_returns():
    treas_returns = pd.read_csv(TREASURY_RETURNS_FILE, index_col=0, parse_dates=True)
    mapping = pd.read_csv(TREASURY_MAP_FILE)
    approved = set(mapping['symbol'])
    # Standardize column names (strip whitespace/trailing commas) before filtering
    treas_returns.columns = [str(c).strip().rstrip(',') for c in treas_returns.columns]
    mapping['symbol'] = mapping['symbol'].astype(str).str.strip().str.rstrip(',')
    approved = set(mapping['symbol'])
    treas_returns = treas_returns[[c for c in treas_returns.columns if c in approved]]
    # Clean: drop columns with >30% NaN, replace infs with NaN; leave NaNs for strict row-wise drop later
    treas_returns = treas_returns.loc[:, treas_returns.isnull().mean() < 0.3]
    treas_returns = treas_returns.replace([np.inf, -np.inf], np.nan)
    return treas_returns

# Helper: Tag equity ETFs (simple: contains 'SPY', 'IVV', 'VOO', or by identifier type)

def tag_equity_etfs(etf_returns):
    # Curated list of bond ETF tickers seen in dataset; treat all others as equity ETFs
    bond_etf_tickers = {
        'AGG','BIL','BND','BNDX','BSV','CORP','HYG','HYLS','IEF','IGSB','JNK','LQD','MBB',
        'MUB','GOVT','TLT','TIP','TIPS','SHV','SHY','USFR','VCIT','VCSH','VTIP'
    }
    equity_cols = [c for c in etf_returns.columns if c not in bond_etf_tickers]
    bond_cols = [c for c in etf_returns.columns if c in bond_etf_tickers]
    return equity_cols, bond_cols

# Main loader

def load_data():
    etf_returns = load_etf_returns()
    treas_returns = load_treasury_returns()
    equity_cols, bond_etf_cols = tag_equity_etfs(etf_returns)
    # Combine all bonds: bond ETFs + treasuries
    bond_returns = pd.concat([etf_returns[bond_etf_cols], treas_returns], axis=1)
    # Merge returns
    all_returns = pd.concat([etf_returns, treas_returns], axis=1)
    # Drop columns with all NaNs
    all_returns = all_returns.dropna(axis=1, how="all")
    # Drop columns with zero variance
    all_returns = all_returns.loc[:, all_returns.std() > 0]
    # Replace inf/-inf with NaN
    all_returns = all_returns.replace([np.inf, -np.inf], np.nan)
    # Drop any rows with NaNs (strict cleaning)
    all_returns = all_returns.dropna(axis=0, how="any")
    # Drop columns with all NaNs again (in case)
    all_returns = all_returns.dropna(axis=1, how="all")
    # Drop columns with zero variance again (in case)
    all_returns = all_returns.loc[:, all_returns.std() > 0]
    # Ensure all values are finite
    all_returns = all_returns.astype(float)
    # Diagnostics (compact)
    print("Shape after cleaning:", all_returns.shape)
    # Drop any columns with NaNs (final check)
    all_returns = all_returns.loc[:, ~all_returns.isnull().any()]
    print("Final shape after dropping NaN columns:", all_returns.shape)
    # Winsorize extremes per asset by 0.5% tails to stabilize covariance
    lower_q = all_returns.quantile(0.005)
    upper_q = all_returns.quantile(0.995)
    for col in all_returns.columns:
        lo = lower_q[col]
        hi = upper_q[col]
        if np.isfinite(lo) and np.isfinite(hi) and lo < hi:
            all_returns[col] = all_returns[col].clip(lower=lo, upper=hi)
    assert np.isfinite(all_returns.values).all(), "Returns data contains non-finite values after cleaning."
    return all_returns, equity_cols
    all_returns = all_returns.replace([np.inf, -np.inf], np.nan)
    # Drop any rows with NaNs (strict cleaning)
    all_returns = all_returns.dropna(axis=0, how="any")
    # Drop columns with all NaNs again (in case)
    all_returns = all_returns.dropna(axis=1, how="all")
    # Drop columns with zero variance again (in case)
    all_returns = all_returns.loc[:, all_returns.std() > 0]
    # Ensure all values are finite
    all_returns = all_returns.astype(float)
    print("Shape after cleaning:", all_returns.shape)
    print("Any NaNs left?", all_returns.isnull().any().any())
    print("Columns with NaNs:", all_returns.columns[all_returns.isnull().any()].tolist())
    print("Any infs left?", np.isinf(all_returns.values).any())
    # Drop any columns with NaNs (final check)
    all_returns = all_returns.loc[:, ~all_returns.isnull().any()]
    print("Final shape after dropping NaN columns:", all_returns.shape)
    # Remove columns with extreme values (outliers)
    max_abs = all_returns.abs().max()
    extreme_cols = max_abs[max_abs > 2].index.tolist()
    if extreme_cols:
        print("Dropping columns with extreme values:", extreme_cols)
        all_returns = all_returns.drop(columns=extreme_cols)
    assert np.isfinite(all_returns.values).all(), "Returns data contains non-finite values after cleaning."
    return all_returns, equity_cols
