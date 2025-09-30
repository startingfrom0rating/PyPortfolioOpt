"""
Script to generate efficient frontier plot for report.
"""
import os
import numpy as np
import pandas as pd
from pypfopt import EfficientFrontier, objective_functions
from estimators import compute_ema_returns, compute_sample_cov
from data_loader import load_data, load_treasury_returns
from config import PLOT_EF, EQUITY_MIN, L2_GAMMA
from plots import plot_frontier_like_readme


def sanitize_cov(cov: pd.DataFrame, eps: float = 1e-4) -> pd.DataFrame:
	cov = cov.copy()
	cov_values = cov.values
	cov_values[~np.isfinite(cov_values)] = 0.0
	cov_values = 0.5 * (cov_values + cov_values.T)
	n = cov_values.shape[0]
	cov_values += eps * np.eye(n)
	return pd.DataFrame(cov_values, index=cov.index, columns=cov.columns)


def build_ef_with_constraints(mu: pd.Series, cov: pd.DataFrame, equity_cols: list):
	ef = EfficientFrontier(mu, cov)
	# Equity minimum constraint if we have any equity columns
	if equity_cols:
		equity_idx = [i for i, c in enumerate(mu.index) if c in equity_cols]
		if equity_idx:
			ef.add_constraint(lambda w, idx=equity_idx: w[idx].sum() >= EQUITY_MIN)
	ef.add_objective(objective_functions.L2_reg, gamma=L2_GAMMA)
	return ef


def select_best_single_treasury(all_returns: pd.DataFrame, equity_cols: list):
	"""
	Heuristic: enforce the policy "exactly one Treasury" by:
	- Identify treasury columns as those not in equity_cols and not classified as bond ETFs earlier.
	- For each treasury candidate, build EF on universe = equity ETFs + that treasury only.
	- Evaluate an anchor point (e.g., target vol = 0.12) and pick the treasury giving highest expected return.
	- Return the EF for the best treasury across full spectrum (using same mu/cov restricted to that universe).
	"""
	# Identify treasury candidates from the current data by checking which columns exist in the treasury file
	treas_in_data = set(load_treasury_returns().columns).intersection(set(all_returns.columns))
	if not treas_in_data:
		# No treasuries detected; fall back to full universe EF
		ema_mu_full = compute_ema_returns(all_returns)
		cov_full = sanitize_cov(compute_sample_cov(all_returns))
		return build_ef_with_constraints(ema_mu_full, cov_full, equity_cols)

	best_score = -np.inf
	best_ef = None
	target_vol = 0.12

	equity_set = set(equity_cols)
	for t in sorted(treas_in_data):
		universe_cols = list(equity_set.union({t}))
		sub_returns = all_returns[universe_cols]
		mu = compute_ema_returns(sub_returns)
		cov = sanitize_cov(compute_sample_cov(sub_returns))
		ef = build_ef_with_constraints(mu, cov, equity_cols=list(equity_set))
		try:
			_ = ef.efficient_risk(target_vol)
			mu_hat, sigma_hat, _ = ef.portfolio_performance()
			score = mu_hat  # highest return at target vol
			if score > best_score:
				best_score = score
				best_ef = ef
		except Exception:
			continue

	# Fallback to full universe if none succeeded
	if best_ef is None:
		ema_mu_full = compute_ema_returns(all_returns)
		cov_full = sanitize_cov(compute_sample_cov(all_returns))
		best_ef = build_ef_with_constraints(ema_mu_full, cov_full, equity_cols)
	return best_ef


def main():
	# Unified load
	all_returns, equity_cols = load_data()
	# Enforce the treasury cardinality via heuristic selection
	ef = select_best_single_treasury(all_returns, equity_cols)
	# For a clean, curved frontier, pass mu/cov directly and rebuild EF per point
	# Recompute mu/cov to ensure they align with the EF's asset universe
	# Note: select_best_single_treasury returns an EF pinned to a universe; extract its data
	assets = ef.tickers
	sub_returns = all_returns[assets]
	mu = compute_ema_returns(sub_returns)
	cov = sanitize_cov(compute_sample_cov(sub_returns))
	equity_cols_sub = [c for c in assets if c in equity_cols]
	plot_frontier_like_readme(
		mu,
		cov,
		equity_cols_sub,
		PLOT_EF,
		equity_min=EQUITY_MIN,
		l2_gamma=L2_GAMMA,
		n_samples=3000,
		random_state=42,
	)


if __name__ == "__main__":
	main()
