"""
Plotting utilities for MVO study.
"""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pypfopt import EfficientFrontier, objective_functions
from matplotlib.ticker import PercentFormatter

def plot_efficient_frontier(ef, filename):
    risks = []
    returns = []
    for target_vol in np.linspace(0.05, 0.20, 20):
        try:
            weights = ef.efficient_risk(target_vol)
            mu, sigma, _ = ef.portfolio_performance()
            risks.append(sigma)
            returns.append(mu)
        except Exception:
            continue
    plt.figure(figsize=(8,6))
    plt.plot(risks, returns, marker='o')
    plt.xlabel('Volatility')
    plt.ylabel('Expected Return')
    plt.title('Efficient Frontier')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def plot_efficient_frontier_from_params(
    mu: pd.Series,
    cov: pd.DataFrame,
    equity_cols: list,
    filename: str,
    equity_min: float = 0.5,
    l2_gamma: float = 0.1,
    num_points: int = 40,
):
    """
    Plot the efficient frontier by rebuilding a fresh EF for each target volatility,
    spanning from the minimum-variance portfolio risk to a high-return portfolio risk.
    This avoids state carryover and produces a curved frontier.
    """

    def build_ef():
        ef_local = EfficientFrontier(mu, cov)
        if equity_cols:
            idx = [i for i, c in enumerate(mu.index) if c in equity_cols]
            if idx:
                ef_local.add_constraint(lambda w, idx=idx: w[idx].sum() >= equity_min)
        ef_local.add_objective(objective_functions.L2_reg, gamma=l2_gamma)
        return ef_local

    # Compute min-variance risk
    ef_min = build_ef()
    try:
        ef_min.min_volatility()
        _, sigma_min, _ = ef_min.portfolio_performance()
    except Exception:
        sigma_min = np.sqrt(np.diag(cov.values)).min()

    # Compute a high-return point to anchor the upper end
    mu_max = float(mu.max())
    target_return = max(mu_max * 0.95, float(mu.mean()) + 0.01)
    ef_high = build_ef()
    try:
        ef_high.efficient_return(target_return)
        _, sigma_high, _ = ef_high.portfolio_performance()
    except Exception:
        # Fallback to volatility of the highest-mean asset
        asset_max = mu.idxmax()
        sigma_high = float(np.sqrt(cov.loc[asset_max, asset_max]))
        sigma_high = max(sigma_high, sigma_min * 1.2)

    vols = np.linspace(max(1e-6, sigma_min * 1.01), sigma_high, num_points)
    risks, rets = [], []
    for v in vols:
        ef_i = build_ef()
        try:
            ef_i.efficient_risk(float(v))
            mu_i, sigma_i, _ = ef_i.portfolio_performance()
            risks.append(sigma_i)
            rets.append(mu_i)
        except Exception:
            continue

    plt.figure(figsize=(8, 6))
    plt.plot(risks, rets, marker='o')
    plt.xlabel('Volatility')
    plt.ylabel('Expected Return')
    plt.title('Efficient Frontier')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches='tight')
    plt.close()


def plot_frontier_like_readme(
    mu: pd.Series,
    cov: pd.DataFrame,
    equity_cols: list,
    filename: str,
    equity_min: float = 0.5,
    l2_gamma: float = 0.1,
    n_samples: int = 3000,
    random_state: int = 42,
    dpi: int = 180,
):
    """
    Plot an efficient frontier similar to the README style:
    - Background scatter of random long-only portfolios (color by Sharpe)
    - Curved efficient frontier
    - Highlight min-volatility and max-Sharpe portfolios
    Axes are annualized and formatted as percentages.
    """

    rng = np.random.default_rng(random_state)
    assets = list(mu.index)

    def build_ef():
        ef_local = EfficientFrontier(mu, cov)
        if equity_cols:
            idx = [i for i, c in enumerate(mu.index) if c in equity_cols]
            if idx:
                ef_local.add_constraint(lambda w, idx=idx: w[idx].sum() >= equity_min)
        ef_local.add_objective(objective_functions.L2_reg, gamma=l2_gamma)
        return ef_local

    # Min-vol and Max-Sharpe
    ef_min = build_ef()
    ef_min.min_volatility()
    mu_min, sigma_min, _ = ef_min.portfolio_performance()

    ef_ms = build_ef()
    ef_ms.max_sharpe()
    mu_ms, sigma_ms, _ = ef_ms.portfolio_performance()

    # Frontier curve by target returns
    mu_low = mu_min
    mu_high = max(mu_ms, float(mu.quantile(0.9)))
    mu_targets = np.linspace(mu_low, mu_high, 60)
    fr_risks, fr_rets = [], []
    for mt in mu_targets:
        ef_i = build_ef()
        try:
            ef_i.efficient_return(float(mt))
            mu_i, sigma_i, _ = ef_i.portfolio_performance()
            fr_risks.append(sigma_i)
            fr_rets.append(mu_i)
        except Exception:
            continue

    # Random portfolios
    # Rejection sampling to meet equity_min if provided
    eq_set = set(equity_cols)
    X, Y, C = [], [], []
    n = len(assets)
    attempts = 0
    accepted = 0
    while accepted < n_samples and attempts < n_samples * 50:
        attempts += 1
        w = rng.dirichlet(np.ones(n))
        if equity_cols:
            eq_idx = [i for i, a in enumerate(assets) if a in eq_set]
            if np.sum(w[eq_idx]) < equity_min:
                continue
        # metrics
        port_mu = float(np.dot(w, mu.values))
        port_sigma = float(np.sqrt(w @ cov.values @ w))
        if not np.isfinite(port_sigma) or port_sigma <= 0:
            continue
        X.append(port_sigma)
        Y.append(port_mu)
        C.append(port_mu / port_sigma)
        accepted += 1

    # Plot
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
