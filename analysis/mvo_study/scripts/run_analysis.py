"""
Main analysis script for MVO study.
"""
import pandas as pd
import numpy as np
from pypfopt import EfficientFrontier, objective_functions
import os
from config import VOL_TARGET, EQUITY_MIN, L2_GAMMA, RESULTS_TABLE, PLOT_ALLOC, PLOT_EF, OUTPUT_DIR
from data_loader import load_data, load_treasury_returns
from estimators import compute_ema_returns, compute_mean_returns, compute_sample_cov
import matplotlib.pyplot as plt



# Load cleaned returns data and equity columns
all_returns, equity_cols = load_data()
# Final guard
all_returns = all_returns.dropna(axis=0, how="any")
print("All-returns shape:", all_returns.shape)

# Estimators
ema_mu = compute_ema_returns(all_returns)
mean_mu = compute_mean_returns(all_returns)
sample_cov = compute_sample_cov(all_returns)

def sanitize_cov(cov: pd.DataFrame, eps: float = 1e-4) -> pd.DataFrame:
    # Replace any non-finite with 0, then add ridge to diagonal
    cov = cov.copy()
    cov_values = cov.values
    cov_values[~np.isfinite(cov_values)] = 0.0
    # Symmetrize
    cov_values = 0.5 * (cov_values + cov_values.T)
    # Ridge
    n = cov_values.shape[0]
    cov_values += eps * np.eye(n)
    return pd.DataFrame(cov_values, index=cov.index, columns=cov.columns)

covariances = {
    'Sample': sanitize_cov(sample_cov, 1e-4),
}

results = []

# Precompute equity index set
equity_idx = [i for i, c in enumerate(all_returns.columns) if c in equity_cols]


def build_ef(mu: pd.Series, cov: pd.DataFrame, equity_cols_local: list):
    ef_local = EfficientFrontier(mu, cov)
    if equity_cols_local:
        idx = [i for i, c in enumerate(mu.index) if c in equity_cols_local]
        if idx:
            ef_local.add_constraint(lambda w, idx=idx: w[idx].sum() >= EQUITY_MIN)
    ef_local.add_objective(objective_functions.L2_reg, gamma=L2_GAMMA)
    return ef_local


def select_best_single_treasury_for_universe(base_returns: pd.DataFrame, equity_cols_local: list, mu_mode: str = 'EMA', target_vol: float = VOL_TARGET):
    # Identify treasuries present in the dataset
    treas_candidates = sorted(set(load_treasury_returns().columns).intersection(set(base_returns.columns)))
    equity_set = set(equity_cols_local)
    if not treas_candidates:
        # No treasury candidates; return EF on full universe
        mu_full = compute_ema_returns(base_returns) if mu_mode == 'EMA' else compute_mean_returns(base_returns)
        cov_full = sanitize_cov(compute_sample_cov(base_returns))
        return build_ef(mu_full, cov_full, equity_cols_local), None
    best_score = -np.inf
    best_ef = None
    best_t = None
    for t in treas_candidates:
        universe_cols = list(equity_set.union({t}))
        sub = base_returns[universe_cols]
        mu = compute_ema_returns(sub) if mu_mode == 'EMA' else compute_mean_returns(sub)
        cov = sanitize_cov(compute_sample_cov(sub))
        ef_try = build_ef(mu, cov, list(equity_set))
        try:
            _ = ef_try.efficient_risk(target_vol)
            mu_hat, sigma_hat, _ = ef_try.portfolio_performance()
            score = mu_hat
            if score > best_score:
                best_score = score
                best_ef = ef_try
                best_t = t
        except Exception:
            continue
    if best_ef is None:
        mu_full = compute_ema_returns(base_returns) if mu_mode == 'EMA' else compute_mean_returns(base_returns)
        cov_full = sanitize_cov(compute_sample_cov(base_returns))
        return build_ef(mu_full, cov_full, equity_cols_local), None
    return best_ef, best_t

for mu_name, mu in [('EMA', ema_mu), ('Mean', mean_mu)]:
    for cov_name, cov in covariances.items():
        # Enforce exactly-one-treasury via heuristic selection on the universe per estimator/cov combo
        # Build working returns subset matching mu/cov ordering
        universe_cols = list(mu.index)
        base_returns = all_returns[universe_cols]
        ef, selected_treasury = select_best_single_treasury_for_universe(base_returns, equity_cols, mu_mode=mu_name)
        # Optimize at target vol
        weights = ef.efficient_risk(VOL_TARGET)
        perf = ef.portfolio_performance()
        # Format weights: threshold tiny, round to 4 decimals
        # Convert to clean Series with 4dp, strip trailing commas/whitespace in labels
        w_series = pd.Series(weights).astype(float)
        w_series = w_series.where(w_series.abs() >= 1e-4, 0.0)
        w_series = w_series.round(4)
        w_series.index = [str(i).strip().rstrip(',') for i in w_series.index]
        # Save per-run weights CSV
        safe_mu = mu_name.replace(' ', '')
        safe_cov = cov_name.replace(' ', '')
        weights_path = os.path.join(OUTPUT_DIR, f'weights_{safe_mu}_{safe_cov}_efficient_risk.csv')
        w_series.to_csv(weights_path, header=['weight'], index_label='ticker', float_format='%.4f')
        results.append({
            'mu': mu_name,
            'cov': cov_name,
            'exp_return': perf[0],
            'volatility': perf[1],
            'sharpe': perf[2],
            'weights_file': os.path.basename(weights_path),
            'selected_treasury': selected_treasury if selected_treasury is not None else ''
        })
        # Save allocation plot (neat layout)
        nz = w_series[w_series.abs() > 0]
        plt.figure(figsize=(max(10, len(nz) * 0.3), 5), constrained_layout=True)
        plt.bar(nz.index.tolist(), nz.values.tolist())
        plt.title(f'Allocation: {mu_name} / {cov_name}')
        plt.ylabel('Weight')
        plt.xticks(rotation=60, ha='right', fontsize=8)
        plt.savefig(f'{PLOT_ALLOC[:-4]}_{mu_name}_{cov_name}.png', bbox_inches='tight')
        plt.close()

# Save results table
results_df = pd.DataFrame(results)
results_df.to_csv(RESULTS_TABLE, index=False)
