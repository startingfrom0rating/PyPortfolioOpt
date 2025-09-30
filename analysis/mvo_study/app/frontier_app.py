"""
App-side efficient frontier plotting using patterns from PyPortfolioOpt's efficient_frontier module.
We DO NOT modify core pypfopt files; this module consumes our cleaned data pipeline.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from pypfopt import EfficientFrontier, objective_functions

from ..scripts.estimators import compute_ema_returns, compute_sample_cov
from ..scripts.data_loader import load_data, load_treasury_returns


def sanitize_cov(cov: pd.DataFrame, eps: float = 1e-4) -> pd.DataFrame:
    cov = cov.copy()
    vals = cov.values
    vals[~np.isfinite(vals)] = 0.0
    vals = 0.5 * (vals + vals.T)
    n = vals.shape[0]
    vals += eps * np.eye(n)
    return pd.DataFrame(vals, index=cov.index, columns=cov.columns)


def build_ef(mu: pd.Series, cov: pd.DataFrame, equity_cols: list, equity_min: float, l2_gamma: float) -> EfficientFrontier:
    ef = EfficientFrontier(mu, cov)
    if equity_cols:
        idx = [i for i, c in enumerate(mu.index) if c in equity_cols]
        if idx:
            ef.add_constraint(lambda w, idx=idx: w[idx].sum() >= equity_min)
    ef.add_objective(objective_functions.L2_reg, gamma=l2_gamma)
    return ef


def select_one_treasury_heuristic(returns: pd.DataFrame, equity_cols: list, mu_mode: str, equity_min: float, l2_gamma: float, target_vol: float = 0.12):
    """Choose exactly one Treasury via heuristic best-at-target-vol approach."""
    treas_candidates = sorted(set(load_treasury_returns().columns).intersection(set(returns.columns)))
    eq_set = set(equity_cols)
    if not treas_candidates:
        mu = compute_ema_returns(returns) if mu_mode == 'EMA' else returns.mean() * 12
        cov = sanitize_cov(compute_sample_cov(returns))
        return build_ef(mu, cov, equity_cols, equity_min, l2_gamma), list(returns.columns)
    best = None
    best_score = -np.inf
    best_assets = None
    for t in treas_candidates:
        cols = list(eq_set.union({t}))
        sub = returns[cols]
        mu = compute_ema_returns(sub) if mu_mode == 'EMA' else sub.mean() * 12
        cov = sanitize_cov(compute_sample_cov(sub))
        ef = build_ef(mu, cov, list(eq_set), equity_min, l2_gamma)
        try:
            ef.efficient_risk(target_vol)
            m, s, _ = ef.portfolio_performance()
            if m > best_score:
                best_score = m
                best = ef
                best_assets = cols
        except Exception:
            continue
    if best is None:
        mu = compute_ema_returns(returns) if mu_mode == 'EMA' else returns.mean() * 12
        cov = sanitize_cov(compute_sample_cov(returns))
        return build_ef(mu, cov, equity_cols, equity_min, l2_gamma), list(returns.columns)
    return best, best_assets


def plot_frontier_readme_style(mu: pd.Series, cov: pd.DataFrame, equity_cols: list, filename: str, equity_min: float, l2_gamma: float, n_samples: int = 12000, seed: int = 42, dpi: int = 180):
    rng = np.random.default_rng(seed)
    assets = list(mu.index)

    def make_ef():
        return build_ef(mu, cov, equity_cols, equity_min, l2_gamma)

    # Min-vol
    ef_min = make_ef()
    ef_min.min_volatility()
    mu_min, sigma_min, _ = ef_min.portfolio_performance()

    # Max Sharpe
    ef_ms = make_ef()
    ef_ms.max_sharpe()
    mu_ms, sigma_ms, _ = ef_ms.portfolio_performance()

    # Frontier curve via target returns
    mu_low = mu_min
    mu_high = max(mu_ms, float(mu.quantile(0.9)))
    rt_targets = np.linspace(mu_low, mu_high, 60)
    fr_risks, fr_rets = [], []
    for rt in rt_targets:
        ef_i = make_ef()
        try:
            ef_i.efficient_return(float(rt))
            m_i, s_i, _ = ef_i.portfolio_performance()
            fr_risks.append(s_i)
            fr_rets.append(m_i)
        except Exception:
            continue

    # Random portfolios (biased towards equities to satisfy equity_min more often)
    eq_set = set(equity_cols)
    X, Y, C = [], [], []
    n = len(assets)
    alpha = np.ones(n)
    if equity_cols:
        idx_eq = [i for i, a in enumerate(assets) if a in eq_set]
        # Slightly overweight equities in the Dirichlet prior to reduce rejections
        alpha[idx_eq] = 2.0
    attempts, accepted = 0, 0
    max_attempts = n_samples * 30
    while accepted < n_samples and attempts < max_attempts:
        attempts += 1
        w = rng.dirichlet(alpha)
        if equity_cols:
            idx = [i for i, a in enumerate(assets) if a in eq_set]
            if np.sum(w[idx]) < equity_min:
                continue
        port_mu = float(np.dot(w, mu.values))
        port_sigma = float(np.sqrt(w @ cov.values @ w))
        if not np.isfinite(port_sigma) or port_sigma <= 0:
            continue
        X.append(port_sigma)
        Y.append(port_mu)
        C.append(port_mu / port_sigma)
        accepted += 1

    fig, ax = plt.subplots(figsize=(9, 6), dpi=dpi)
    if X:
        sc = ax.scatter(X, Y, c=C, cmap='viridis', s=8, alpha=0.35, edgecolors='none')
        cbar = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.04)
        cbar.ax.set_ylabel('Sharpe ratio', rotation=90)
    ax.plot(fr_risks, fr_rets, color='tab:red', linewidth=2.0, label='Efficient frontier')
    ax.scatter([sigma_min], [mu_min], marker='*', color='gold', s=180, label='Min volatility')
    ax.scatter([sigma_ms], [mu_ms], marker='^', color='dodgerblue', s=100, label='Max Sharpe')
    ax.set_xlabel('Annualized volatility')
    ax.set_ylabel('Annualized return')
    ax.xaxis.set_major_formatter(PercentFormatter(1.0))
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='best')
    fig.tight_layout()
    fig.savefig(filename, bbox_inches='tight')
    plt.close(fig)


def generate_frontier_output(output_path: str, equity_min: float = 0.5, l2_gamma: float = 0.1, mu_mode: str = 'EMA', target_vol: float = 0.12):
    # Use our cleaned data
    all_returns, equity_cols = load_data()
    # Select one Treasury instrument via heuristic
    ef_sel, assets = select_one_treasury_heuristic(all_returns, equity_cols, mu_mode, equity_min, l2_gamma, target_vol)
    # Recompute mu/cov on selected universe
    sub = all_returns[assets]
    mu = compute_ema_returns(sub) if mu_mode == 'EMA' else sub.mean() * 12
    cov = sanitize_cov(compute_sample_cov(sub))
    eq_cols_sub = [a for a in assets if a in equity_cols]
    # Plot
    plot_frontier_readme_style(mu, cov, eq_cols_sub, output_path, equity_min, l2_gamma)
