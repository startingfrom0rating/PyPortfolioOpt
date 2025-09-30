# MVO Study Comprehensive Documentation

## Overview

This directory contains a complete mathematical analysis and documentation of the Mean-Variance Optimization (MVO) study for ETF and Treasury portfolio allocation.

## Documentation Files

### 1. **PDF Report** (`output/mvo_report.pdf`)
A professionally formatted, comprehensive PDF report including:
- **Executive Summary** with key findings
- **Table of Contents** for easy navigation
- **Introduction to MVO** with mathematical framework
- **Data Processing Pipeline** with all mathematical operations explained
- **Estimator Details**: EMA returns, arithmetic mean, sample covariance, Ledoit-Wolf shrinkage
- **Optimization Framework**: Portfolio variance, Sharpe ratio, efficient risk, L2 regularization
- **Constraints**: Long-only, equity minimum, volatility target
- **Results & Analysis** with tables and visualizations
- **Discussion** of findings and trade-offs
- **References** to academic literature

### 2. **Markdown Documentation** (`MATHEMATICAL_DOCUMENTATION.md`)
A detailed technical reference document covering:
- Complete mathematical formulas for every operation
- Step-by-step derivations and explanations
- Code snippets with mathematical annotations
- Comparison tables for different methods
- Practical interpretation guide
- Mathematical proofs in appendix

### 3. **Source Code** (`scripts/`)
Implementation of all mathematical operations:
- `data_loader.py`: Data preprocessing pipeline
- `estimators.py`: Return and covariance estimators
- `run_analysis.py`: Main optimization workflow
- `report.py`: PDF report generation
- `config.py`: Parameters and settings

## Quick Start

### Generate the Comprehensive Report

```bash
# 1. Navigate to the scripts directory
cd analysis/mvo_study/scripts

# 2. Run the analysis (if not already done)
python run_analysis.py

# 3. Generate the enhanced PDF report
python report.py
```

The PDF will be generated at: `analysis/mvo_study/output/mvo_report.pdf`

### View the Mathematical Documentation

```bash
# Open the markdown file
cat ../MATHEMATICAL_DOCUMENTATION.md

# Or view in your browser/markdown viewer
```

## What's Inside the Reports

### Mathematical Operations Documented

1. **Data Processing**:
   - Monthly return compounding: R_month = ∏(1 + r_daily) - 1
   - Winsorization: r_clipped = clip(r, Q_0.005, Q_0.995)
   - Covariance sanitization: Σ_clean = (Σ + Σᵀ)/2 + ε·I

2. **Return Estimators**:
   - **EMA**: μ_EMA = [(1 + EMA_span(r))^frequency - 1]
   - **Mean**: μ_mean = mean(r) × frequency

3. **Covariance Estimators**:
   - **Sample**: Σ_sample = (1/(T-1)) Σ_t (r_t - r̄)(r_t - r̄)ᵀ × frequency
   - **Ledoit-Wolf**: Σ_LW = δ·F + (1-δ)·S

4. **Optimization Objectives**:
   - **Min Volatility**: minimize wᵀΣw
   - **Max Sharpe**: maximize (wᵀμ) / √(wᵀΣw)
   - **Efficient Risk**: maximize wᵀμ s.t. √(wᵀΣw) ≤ σ_target
   - **L2 Regularization**: penalty = γ·||w||²

5. **Constraints**:
   - Fully invested: Σw = 1
   - Long-only: w ≥ 0
   - Equity minimum: Σ_(equity) w ≥ 0.50
   - Volatility target: √(wᵀΣw) ≤ 0.12

## Understanding the Results

### Performance Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| Expected Return | μ_p = wᵀμ | Annualized expected portfolio return |
| Volatility | σ_p = √(wᵀΣw) | Annualized standard deviation (risk) |
| Sharpe Ratio | SR = μ_p / σ_p | Risk-adjusted return (higher is better) |

### Portfolio Weights

- Sum to 100% (fully invested)
- All ≥ 0 (long-only)
- Equity weights sum to ≥ 50% (policy requirement)

### Interpretation Tips

1. **High Sharpe Ratio (> 1.5)**: Excellent risk-adjusted performance
2. **Concentrated weights**: Few assets dominate (check diversification)
3. **EMA vs Mean**: EMA adapts to trends, Mean is more stable
4. **Sample vs Ledoit-Wolf**: Ledoit-Wolf more stable with many assets

## Report Features

### PDF Report Highlights

✓ **Professional formatting** with colors, headers, and spacing  
✓ **Table of Contents** with page numbers  
✓ **Mathematical formulas** clearly displayed  
✓ **Comparison tables** for estimators and methods  
✓ **Visualizations** of allocations and efficient frontier  
✓ **Non-technical explanations** suitable for all audiences  
✓ **Technical rigor** for quantitative professionals  

### Markdown Documentation Highlights

✓ **Complete formula reference** for every operation  
✓ **Code snippets** with mathematical annotations  
✓ **Step-by-step workflow** from data to results  
✓ **Comparison tables** and trade-off analysis  
✓ **Practical interpretation guide**  
✓ **Mathematical proofs** in appendix  

## Configuration Parameters

Key parameters used in the study (from `config.py`):

```python
VOL_TARGET = 0.12      # 12% annual volatility target
EQUITY_MIN = 0.50      # 50% minimum equity allocation
L2_GAMMA = 0.1         # L2 regularization strength
EMA_SPAN = 36          # 36-month EMA window
```

## File Structure

```
analysis/mvo_study/
├── MATHEMATICAL_DOCUMENTATION.md  # Technical reference (this file's counterpart)
├── README.md                      # This file
├── scripts/
│   ├── config.py                  # Parameters and paths
│   ├── data_loader.py            # Data preprocessing
│   ├── estimators.py             # Return/covariance estimators
│   ├── run_analysis.py           # Main optimization
│   ├── report.py                 # Enhanced PDF generation
│   └── plots.py                  # Visualization utilities
└── output/
    ├── mvo_report.pdf            # Comprehensive PDF report ★
    ├── results_table.csv         # Performance summary
    ├── allocation_plot_*.png     # Weight visualizations
    ├── efficient_frontier.png    # Risk-return frontier
    └── weights_*.csv             # Optimal allocations
```

## For Non-Technical Readers

The PDF report is designed to be accessible to readers without a strong mathematical background:

- **Executive Summary** provides high-level findings
- **Introduction** explains concepts in plain language
- **Visual tables** summarize comparisons
- **Graphs and charts** illustrate key insights
- **Discussion** interprets results practically
- **Conclusion** summarizes recommendations

Mathematical formulas are included for completeness but are not required to understand the main findings.

## For Technical Readers

The mathematical documentation provides:

- **Rigorous formulas** for every operation
- **Derivations** of key results
- **Implementation details** with code
- **Proofs** of important theorems
- **References** to academic literature
- **Complete mathematical framework**

## Dependencies

Required Python packages:
- `reportlab` - PDF generation
- `pandas` - Data manipulation
- `numpy` - Numerical operations
- `matplotlib` - Plotting
- `pypfopt` - Portfolio optimization
- `cvxpy` - Convex optimization solver

## Questions?

For questions about:
- **Mathematical formulas**: See `MATHEMATICAL_DOCUMENTATION.md`
- **Report content**: Open `output/mvo_report.pdf`
- **Implementation**: Check source files in `scripts/`
- **Results interpretation**: See "Understanding the Results" section above

## Citation

If using this analysis in academic or professional work, please cite:

```bibtex
@techreport{mvo_study_2024,
  title={Mean-Variance Optimization Study: ETF \& Treasury Portfolio Analysis},
  author={PyPortfolioOpt MVO Study Team},
  year={2024},
  institution={PyPortfolioOpt Project}
}
```

## License

This documentation is part of the PyPortfolioOpt project.
See the main repository LICENSE for terms of use.
