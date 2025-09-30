# Mean-Variance Optimization Study: Mathematical Documentation

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Mathematical Framework](#mathematical-framework)
3. [Data Processing Pipeline](#data-processing-pipeline)
4. [Return Estimators](#return-estimators)
5. [Covariance Estimators](#covariance-estimators)
6. [Optimization Objectives](#optimization-objectives)
7. [Constraints](#constraints)
8. [Complete Workflow](#complete-workflow)
9. [Interpretation Guide](#interpretation-guide)

---

## Executive Summary

This document provides a comprehensive mathematical analysis of every operation in the Mean-Variance Optimization (MVO) study. The analysis covers:

- **Data preprocessing**: Monthly return compounding, outlier handling, winsorization
- **Return estimation**: EMA and arithmetic mean calculations
- **Covariance estimation**: Sample covariance and Ledoit-Wolf shrinkage
- **Optimization**: Portfolio variance minimization, Sharpe ratio maximization, efficient risk
- **Regularization**: L2 penalty for diversification
- **Constraints**: Long-only, equity minimum, volatility targets

All mathematical operations are documented with formulas, explanations, and practical interpretations.

---

## Mathematical Framework

### Core Variables

| Symbol | Description | Dimension |
|--------|-------------|-----------|
| **w** | Portfolio weight vector | N × 1 |
| **μ** | Expected returns vector | N × 1 |
| **Σ** | Covariance matrix | N × N |
| σₚ | Portfolio volatility | scalar |
| μₚ | Portfolio expected return | scalar |
| SR | Sharpe ratio | scalar |

### Fundamental Equations

**Portfolio Expected Return:**
```
μₚ = wᵀμ = Σᵢ wᵢμᵢ
```

**Portfolio Variance:**
```
σₚ² = wᵀΣw = Σᵢ Σⱼ wᵢwⱼΣᵢⱼ
```

**Portfolio Volatility (Risk):**
```
σₚ = √(wᵀΣw)
```

**Sharpe Ratio:**
```
SR = (μₚ - rₑ) / σₚ = (wᵀμ - rₑ) / √(wᵀΣw)
```
where rₑ is the risk-free rate.

---

## Data Processing Pipeline

### 1. Monthly Return Compounding

**Formula:**
```
Rₘₒₙₜₕ = ∏ₜ₌₁ᵀ (1 + rₜ) - 1
```

**Explanation:**
- Input: Daily returns rₜ within a month
- Process: Geometric compounding of (1 + r) terms
- Output: Month-end return

**Example:**
```python
daily_returns = [0.01, -0.005, 0.002]
monthly_return = (1.01) × (0.995) × (1.002) - 1 = 0.007079 ≈ 0.71%
```

### 2. Missing Data Handling

**Rule:**
```
Keep asset i if: (# NaN values / # total observations) < 0.30
```

**Implementation:**
```python
# Drop columns with >30% missing data
threshold = 0.30
valid_cols = returns.columns[returns.isnull().mean() < threshold]
returns = returns[valid_cols]
```

### 3. Winsorization

**Formula:**
```
rᵢ,ₜ = clip(rᵢ,ₜ, Q₀.₀₀₅, Q₀.₉₉₅)
```

**Explanation:**
- Cap extreme values at 0.5th and 99.5th percentiles
- Reduces impact of outliers on covariance estimation
- Preserves majority of data distribution

**Code:**
```python
lower_q = returns.quantile(0.005)
upper_q = returns.quantile(0.995)
returns_clipped = returns.clip(lower=lower_q, upper=upper_q, axis=1)
```

### 4. Covariance Sanitization

**Formula:**
```
Σ_sanitized = (Σ + Σᵀ)/2 + ε·I
```

**Parameters:**
- ε = 10⁻⁴ (ridge parameter)
- I = identity matrix

**Purpose:**
1. **Symmetrization**: (Σ + Σᵀ)/2 ensures exact symmetry
2. **Ridge regularization**: ε·I ensures positive definiteness
3. **Numerical stability**: Prevents singular matrices in optimization

**Implementation:**
```python
def sanitize_cov(cov, eps=1e-4):
    cov_values = cov.values
    # Replace non-finite with 0
    cov_values[~np.isfinite(cov_values)] = 0.0
    # Symmetrize
    cov_values = 0.5 * (cov_values + cov_values.T)
    # Add ridge
    n = cov_values.shape[0]
    cov_values += eps * np.eye(n)
    return pd.DataFrame(cov_values, index=cov.index, columns=cov.columns)
```

---

## Return Estimators

### 1. Exponential Moving Average (EMA) Returns

**Formula:**
```
μᵢ,EMA = [(1 + r̄ᵢ,EMA)^frequency - 1]
```

where:
```
r̄ᵢ,EMA = Σₜ wₜ · rᵢ,ₜ / Σₜ wₜ

with weights: wₜ = (1 - α)^(T-t)
and: α = 2/(span + 1)
```

**Parameters in this study:**
- span = 36 months
- frequency = 12 (monthly → annual conversion)
- α = 2/(36 + 1) ≈ 0.054

**Characteristics:**
- Recent observations weighted more heavily
- Adapts to regime changes
- Responsive to market trends

**Mathematical Properties:**
1. **Exponential decay**: Weights decay exponentially with age
2. **Compounding adjustment**: Geometric mean for accurate annualization
3. **Adaptive**: More sensitive to recent data than arithmetic mean

**Code:**
```python
def compute_ema_returns(returns_df, span=36, frequency=12):
    ema = expected_returns.ema_historical_return(
        returns_df, 
        returns_data=True, 
        span=span, 
        frequency=frequency
    )
    return ema
```

### 2. Arithmetic Mean Returns

**Formula:**
```
μᵢ,mean = (1/T) · Σₜ rᵢ,ₜ · frequency
```

**Parameters:**
- T = number of periods
- frequency = 12 (annualization)

**Characteristics:**
- All observations weighted equally
- Simple, stable estimator
- Slower to adapt to changes

**Code:**
```python
def compute_mean_returns(returns_df, frequency=12):
    mean = expected_returns.mean_historical_return(
        returns_df, 
        returns_data=True, 
        frequency=frequency
    )
    return mean
```

### Comparison Table

| Property | EMA | Arithmetic Mean |
|----------|-----|-----------------|
| Weighting | Recent data emphasized | All data equal |
| Adaptability | High | Low |
| Stability | Moderate | High |
| Best for | Trending markets | Stable markets |
| Lag | Low | High |

---

## Covariance Estimators

### 1. Sample Covariance Matrix

**Formula:**
```
Σᵢⱼ = [1/(T-1)] · Σₜ (rᵢ,ₜ - r̄ᵢ)(rⱼ,ₜ - r̄ⱼ) · frequency
```

**Components:**
- rᵢ,ₜ: Return of asset i at time t
- r̄ᵢ: Mean return of asset i
- T: Number of observations
- frequency = 12 (annualization)

**Properties:**
1. **Unbiased**: E[Σ̂] = Σ (expected value equals true covariance)
2. **Maximum likelihood**: MLE estimator under normality
3. **High variance**: Especially when N (assets) approaches T (periods)

**Code:**
```python
def compute_sample_cov(returns_df, frequency=12):
    cov = risk_models.sample_cov(
        returns_df, 
        returns_data=True, 
        frequency=frequency,
        fix_method="spectral"
    )
    return cov
```

### 2. Ledoit-Wolf Shrinkage Covariance

**Formula:**
```
Σ_LW = δ·F + (1-δ)·S
```

**Components:**
- S: Sample covariance matrix
- F: Shrinkage target (structured estimator)
- δ: Shrinkage intensity (0 ≤ δ ≤ 1)

**Shrinkage Target (Constant Variance):**
```
F = diag(σ₁², σ₂², ..., σₙ²) with σᵢ² = (1/N) Σⱼ σⱼ²
```

**Optimal Shrinkage Intensity:**
The optimal δ minimizes the expected loss:
```
δ* = argmin E[||Σ_LW - Σ_true||²]
```

**Mathematical Derivation:**

1. **Bias-Variance Tradeoff:**
   - As δ → 0: Approaches sample covariance (high variance, low bias)
   - As δ → 1: Approaches target F (low variance, higher bias)
   - Optimal δ balances this tradeoff

2. **Oracle Approximating Shrinkage:**
   ```
   δ* ≈ (Σᵢⱼ Var(Sᵢⱼ)) / (Σᵢⱼ (Sᵢⱼ - Fᵢⱼ)²)
   ```

**Properties:**
1. **Reduced estimation error**: Lower MSE than sample covariance
2. **Better conditioning**: Eigenvalues bounded away from zero
3. **Stability**: More robust to noisy data

**Code:**
```python
def compute_ledoit_wolf_cov(returns_df, frequency=12):
    try:
        cov = risk_models.CovarianceShrinkage(
            returns_df, 
            frequency=frequency
        ).ledoit_wolf(shrinkage_target="constant_variance")
        return cov
    except Exception:
        # Fallback to sample covariance
        return risk_models.sample_cov(returns_df, frequency=frequency)
```

### Eigenvalue Analysis

**Sample Covariance Issues:**
- Smallest eigenvalues can be near zero → numerical instability
- Eigenvalue spread can be very large

**Ledoit-Wolf Benefits:**
- Shrinkage increases smallest eigenvalues
- Reduces condition number: κ(Σ) = λₘₐₓ / λₘᵢₙ
- Better conditioned for optimization

---

## Optimization Objectives

### 1. Minimum Volatility

**Objective Function:**
```
minimize: σₚ² = wᵀΣw
```

**Constraints:**
```
Σᵢ wᵢ = 1  (fully invested)
wᵢ ≥ 0     (long-only)
```

**Solution Method:**
- Quadratic programming
- Convex optimization (global minimum guaranteed)

**Interpretation:**
- Finds the least risky portfolio
- Ignores expected returns
- Often concentrated in low-volatility assets

### 2. Maximum Sharpe Ratio

**Objective Function:**
```
maximize: SR = (wᵀμ - rₑ) / √(wᵀΣw)
```

**Equivalent Formulation:**
```
minimize: -SR = -(wᵀμ - rₑ) / √(wᵀΣw)
```

**Constraints:**
```
Σᵢ wᵢ = 1
wᵢ ≥ 0
```

**Properties:**
1. **Tangency portfolio**: Tangent point on efficient frontier
2. **Optimal leverage point**: Best risk-adjusted return
3. **Scale invariant**: Homogeneous of degree 0 in weights

**Mathematical Form (Convexified):**

CVXPY implements this as:
```python
mu_portfolio = w @ expected_returns
sigma_portfolio = cp.sqrt(cp.quad_form(w, cov_matrix))
objective = -(mu_portfolio - risk_free_rate) / sigma_portfolio
```

### 3. Efficient Risk (Primary Method)

**Objective Function:**
```
maximize: wᵀμ
```

**Constraints:**
```
√(wᵀΣw) ≤ σ_target
Σᵢ wᵢ = 1
wᵢ ≥ 0
```

**In this study:**
- σ_target = 0.12 (12% annual volatility)

**Formulation:**
```python
objective = cp.Maximize(w @ expected_returns)
constraints = [
    cp.sum(w) == 1,
    w >= 0,
    cp.norm(cp.sqrt(cov_matrix) @ w, 2) <= target_vol
]
```

**Interpretation:**
- Find highest return subject to risk limit
- Risk-constrained optimization
- Practical for risk budgeting

### 4. L2 Regularization

**Penalty Term:**
```
L2 = γ · ||w||² = γ · Σᵢ wᵢ²
```

**Modified Objective:**
```
minimize: -wᵀμ + γ·Σᵢ wᵢ²
```

**In this study:**
- γ = 0.1

**Effects:**
1. **Diversification**: Penalizes concentrated positions
2. **Shrinkage**: Pulls weights toward equal weighting
3. **Stability**: Reduces sensitivity to estimation error

**Mathematical Insight:**

The L2 term is the Euclidean norm squared:
```
||w||² = wᵀw = Σᵢ wᵢ²
```

Minimizing this encourages:
- Smaller individual weights
- More uniform distribution
- Less extreme allocations

**Gradient:**
```
∇_w (γ·||w||²) = 2γw
```

This creates a force pulling weights toward zero, balanced against the return-maximizing force.

---

## Constraints

### 1. Fully Invested (Equality Constraint)

**Mathematical Form:**
```
Σᵢ wᵢ = 1
```

**CVXPY Implementation:**
```python
constraints.append(cp.sum(w) == 1)
```

**Meaning:**
- All capital allocated
- No cash position
- Weights sum to 100%

### 2. Long-Only (Inequality Constraint)

**Mathematical Form:**
```
wᵢ ≥ 0 for all i
```

**CVXPY Implementation:**
```python
constraints.append(w >= 0)
```

**Meaning:**
- No short selling
- All positions are long
- Practical for most retail investors

### 3. Weight Bounds (Box Constraints)

**Mathematical Form:**
```
0 ≤ wᵢ ≤ 1 for all i
```

**CVXPY Implementation:**
```python
# Already implied by w >= 0 and Σw = 1
```

**Meaning:**
- No single asset can exceed 100%
- Combined with long-only and fully-invested

### 4. Equity Minimum (Custom Constraint)

**Mathematical Form:**
```
Σ_(i ∈ equity) wᵢ ≥ equity_min
```

**In this study:**
- equity_min = 0.50 (50% minimum equity allocation)

**CVXPY Implementation:**
```python
equity_indices = [i for i, asset in enumerate(assets) if asset in equity_cols]
constraints.append(
    cp.sum([w[i] for i in equity_indices]) >= EQUITY_MIN
)
```

**Meaning:**
- Ensures minimum growth asset exposure
- Policy/strategic requirement
- Balances growth vs. stability

### 5. Risk Target (Volatility Constraint)

**Mathematical Form:**
```
√(wᵀΣw) ≤ σ_target
```

**Equivalent (Second-Order Cone):**
```
||Lw||₂ ≤ σ_target where LLᵀ = Σ
```

**In this study:**
- σ_target = 0.12 (12% annual volatility)

**CVXPY Implementation:**
```python
# Using Cholesky decomposition
L = np.linalg.cholesky(cov_matrix)
constraints.append(cp.norm(L @ w, 2) <= VOL_TARGET)
```

**Meaning:**
- Hard limit on portfolio risk
- Ensures downside protection
- Regulatory or policy requirement

---

## Complete Workflow

### Step-by-Step Mathematical Pipeline

#### Step 1: Data Loading and Cleaning

1. **Load monthly returns**: R ∈ ℝ^(T×N)
2. **Remove assets with >30% missing data**
3. **Drop rows with any NaN**
4. **Winsorize at 0.5% and 99.5% quantiles**
5. **Apply covariance sanitization**

#### Step 2: Estimator Computation

**Expected Returns:**
- EMA: μ_EMA = [(1 + EMA_36(r))^12 - 1]
- Mean: μ_mean = mean(r) × 12

**Covariance:**
- Sample: Σ_sample = cov(r) × 12
- Ledoit-Wolf: Σ_LW = δ·F + (1-δ)·S

#### Step 3: Universe Selection

For each estimator pair (μ, Σ):
1. Identify equity assets vs. treasuries
2. Select one treasury via heuristic:
   - Try each treasury
   - Optimize with equity + treasury
   - Select treasury giving highest return at target vol

#### Step 4: Optimization

**Construct Problem:**
```python
w = cp.Variable(n_assets)
objective = cp.Maximize(w @ mu)
constraints = [
    cp.sum(w) == 1,
    w >= 0,
    cp.norm(L @ w, 2) <= VOL_TARGET,
    cp.sum([w[i] for i in equity_idx]) >= EQUITY_MIN
]
# Add L2 regularization to objective
objective += -L2_GAMMA * cp.sum_squares(w)
```

**Solve:**
```python
problem = cp.Problem(objective, constraints)
problem.solve()
w_optimal = w.value
```

#### Step 5: Performance Calculation

**Expected Return:**
```
μ_p = wᵀμ
```

**Volatility:**
```
σ_p = √(wᵀΣw)
```

**Sharpe Ratio:**
```
SR = μ_p / σ_p  (assuming r_f = 0)
```

#### Step 6: Output Generation

1. **Weights CSV**: Optimal asset allocations
2. **Results table**: Performance metrics
3. **Allocation plots**: Bar charts of weights
4. **Efficient frontier**: Risk-return trade-off visualization

---

## Interpretation Guide

### Understanding the Results

#### 1. Portfolio Weights

**What they mean:**
- wᵢ = 0.25 → 25% of capital in asset i
- Σᵢ wᵢ = 1.00 → Fully invested
- wᵢ > 0.50 → Concentrated position (potential risk)

**How to read:**
```
Asset    Weight    Interpretation
SPY      0.35      35% in S&P 500 (large-cap equities)
TLT      0.15      15% in long-term treasuries (duration risk)
Cash     0.00      No cash allocation (fully invested)
```

#### 2. Performance Metrics

**Expected Return (μ_p):**
- Annualized expected portfolio return
- Based on historical estimation
- Forward-looking (not guaranteed)

**Volatility (σ_p):**
- Annualized standard deviation
- Risk measure (1 std dev moves)
- Higher σ → more uncertainty

**Sharpe Ratio (SR):**
- Risk-adjusted return: SR = μ_p / σ_p
- SR > 1: Good risk-adjusted return
- SR > 2: Excellent performance
- Higher is better

#### 3. Estimator Impact

**EMA vs. Mean Returns:**
- EMA: Responsive to recent trends, may overfit
- Mean: Stable but slow to adapt, may underfit

**Sample vs. Ledoit-Wolf Covariance:**
- Sample: Unbiased but noisy, especially with many assets
- Ledoit-Wolf: Biased but lower variance, more stable

#### 4. Constraint Effects

**Equity Minimum (50%):**
- Ensures growth exposure
- May reduce Sharpe ratio vs. unconstrained
- Policy/strategic requirement

**Volatility Target (12%):**
- Risk budget constraint
- Limits downside exposure
- May cap upside potential

**L2 Regularization (γ=0.1):**
- Encourages diversification
- Slightly reduces theoretical Sharpe
- Improves out-of-sample robustness

### Practical Recommendations

1. **Use EMA + Ledoit-Wolf** for balance of adaptability and stability
2. **Monitor out-of-sample performance** to detect overfitting
3. **Rebalance periodically** (monthly/quarterly) as estimates update
4. **Stress test** with different γ, σ_target values
5. **Validate** with rolling window backtests

---

## Appendix: Mathematical Proofs

### A. Markowitz Mean-Variance Framework

**Theorem (Markowitz):**
The set of mean-variance efficient portfolios forms a hyperbola in (σ, μ) space.

**Proof Sketch:**
1. Efficient frontier: {w : μ(w) ≥ μ* for all w' with σ(w') = σ(w)}
2. This defines an optimization: max μ(w) s.t. σ²(w) = c
3. Lagrangian: L = wᵀμ - λ(wᵀΣw - c)
4. FOC: μ - 2λΣw = 0 → w = (1/2λ)Σ⁻¹μ
5. Substituting back: μ_p = (1/2λ)μᵀΣ⁻¹μ, σ²_p = (1/4λ²)μᵀΣ⁻¹μ
6. Eliminating λ: μ²_p / σ²_p = μᵀΣ⁻¹μ (constant)
7. This is a hyperbola: μ_p = k·σ_p

### B. Ledoit-Wolf Optimal Shrinkage

**Theorem (Ledoit-Wolf):**
The optimal shrinkage intensity minimizing expected squared loss is:
```
δ* = min(π̂ / ρ̂, 1)
```
where π̂ estimates E[||S - Σ||²] and ρ̂ estimates E[||F - Σ||²].

**Intuition:**
- π̂: Variance of sample covariance estimator
- ρ̂: Bias of shrinkage target
- δ* balances bias and variance optimally

### C. L2 Regularization Effect

**Theorem:**
Adding L2 regularization γ||w||² to objective is equivalent to ridge regression in dual space.

**Effect on solution:**
```
w_L2 = argmin[-wᵀμ + (λ/2)wᵀΣw + γwᵀw]
     = (Σ + 2γI)⁻¹μ / C
```
where C ensures Σw = 1.

**Interpretation:**
- Shrinks toward equal weighting
- Reduces condition number of Σ
- Improves numerical stability

---

## References

1. Markowitz, H. (1952). Portfolio Selection. *The Journal of Finance*, 7(1), 77-91.
2. Ledoit, O., & Wolf, M. (2004). A well-conditioned estimator for large-dimensional covariance matrices. *Journal of Multivariate Analysis*, 88(2), 365-411.
3. Sharpe, W. F. (1966). Mutual Fund Performance. *Journal of Business*, 39(1), 119-138.
4. Boyd, S., & Vandenberghe, L. (2004). *Convex Optimization*. Cambridge University Press.
5. PyPortfolioOpt Documentation: https://pyportfolioopt.readthedocs.io/

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Authors:** PyPortfolioOpt MVO Study Team
