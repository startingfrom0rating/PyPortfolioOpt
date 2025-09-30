# MVO Study Workspace

This workspace contains a reproducible analysis pipeline for determining the best mean-variance optimization (MVO) approach for portfolio allocation using the provided ETF and Treasury data.

## Structure
- `scripts/`: All code for config, data loading, analysis, plotting, and report generation
- `output/`: Results tables, plots, and the final PDF report
- `README.md`: This file

## Workflow
1. Data ingestion and cleaning
2. Estimator computation (EMA, mean, sample, Ledoit–Wolf)
3. MVO experiments (efficient risk, max Sharpe, constraints)
4. Output generation (tables, plots)
5. PDF report with TOC, figures, citations, and conclusion

## How to run
See `scripts/run_analysis.py` for the main entry point.
