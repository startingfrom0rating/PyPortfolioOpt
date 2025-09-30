"""
PDF report generation for MVO study - Comprehensive Mathematical Analysis.
This module creates a detailed, well-formatted PDF report explaining all mathematical
operations in the Mean-Variance Optimization study.
"""
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
import pandas as pd
import os
from config import RESULTS_TABLE, PLOT_ALLOC, PLOT_EF, REPORT_PDF, OUTPUT_DIR, VOL_TARGET, EQUITY_MIN, L2_GAMMA, EMA_SPAN

# Initialize styles
styles = getSampleStyleSheet()

# Add custom styles for better formatting
styles.add(ParagraphStyle(
    name='CustomTitle',
    parent=styles['Title'],
    fontSize=24,
    textColor=colors.HexColor('#1a1a1a'),
    spaceAfter=30,
    alignment=TA_CENTER
))

styles.add(ParagraphStyle(
    name='CustomHeading1',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#2c3e50'),
    spaceAfter=12,
    spaceBefore=12,
    keepWithNext=True
))

styles.add(ParagraphStyle(
    name='CustomHeading2',
    parent=styles['Heading2'],
    fontSize=14,
    textColor=colors.HexColor('#34495e'),
    spaceAfter=10,
    spaceBefore=10,
    keepWithNext=True
))

styles.add(ParagraphStyle(
    name='CustomHeading3',
    parent=styles['Heading3'],
    fontSize=12,
    textColor=colors.HexColor('#34495e'),
    spaceAfter=8,
    spaceBefore=8,
    keepWithNext=True
))

styles.add(ParagraphStyle(
    name='Justified',
    parent=styles['Normal'],
    alignment=TA_JUSTIFY,
    fontSize=11,
    leading=14
))

styles.add(ParagraphStyle(
    name='CodeBlock',
    parent=styles['Normal'],
    fontSize=9,
    textColor=colors.HexColor('#c7254e'),
    backColor=colors.HexColor('#f9f2f4'),
    leftIndent=20,
    rightIndent=20,
    fontName='Courier'
))

styles.add(ParagraphStyle(
    name='Formula',
    parent=styles['Normal'],
    fontSize=11,
    textColor=colors.HexColor('#0066cc'),
    leftIndent=30,
    rightIndent=30,
    spaceAfter=8,
    spaceBefore=8
))

def make_pdf_report():
    """
    Generate a comprehensive PDF report with detailed mathematical explanations
    of all operations in the Mean-Variance Optimization study.
    """
    doc = SimpleDocTemplate(REPORT_PDF, pagesize=letter,
                           leftMargin=0.75*inch, rightMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []

    # ========================
    # TITLE PAGE
    # ========================
    story.append(Spacer(1, 1.5*inch))
    story.append(Paragraph("Mean-Variance Optimization Study", styles['CustomTitle']))
    story.append(Paragraph("ETF & Treasury Portfolio Analysis", styles['CustomTitle']))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("A Comprehensive Mathematical Analysis", styles['Heading2']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph("Detailed Explanation of Data Processing, Estimators, and Optimization", styles['Normal']))
    story.append(PageBreak())

    # ========================
    # TABLE OF CONTENTS
    # ========================
    story.append(Paragraph("Table of Contents", styles['CustomHeading1']))
    story.append(Spacer(1, 12))
    
    toc_data = [
        ['Section', 'Title', 'Page'],
        ['1', 'Executive Summary', '3'],
        ['2', 'Introduction to Mean-Variance Optimization', '4'],
        ['3', 'Data Loading and Preprocessing', '5'],
        ['4', 'Mathematical Estimators', '7'],
        ['4.1', 'Expected Returns Calculation', '7'],
        ['4.2', 'Covariance Matrix Estimation', '9'],
        ['5', 'Optimization Framework', '11'],
        ['5.1', 'Portfolio Variance', '11'],
        ['5.2', 'Sharpe Ratio Maximization', '12'],
        ['5.3', 'Efficient Risk Optimization', '13'],
        ['5.4', 'L2 Regularization', '14'],
        ['6', 'Constraints and Bounds', '15'],
        ['7', 'Results and Analysis', '16'],
        ['8', 'Discussion and Interpretation', '18'],
        ['9', 'Conclusion', '19'],
        ['10', 'References', '20']
    ]
    
    toc_table = Table(toc_data, colWidths=[0.6*inch, 4.5*inch, 0.8*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('TOPPADDING', (0,0), (-1,0), 12),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8f9fa')])
    ]))
    story.append(toc_table)
    story.append(PageBreak())

    # ========================
    # 1. EXECUTIVE SUMMARY
    # ========================
    story.append(Paragraph("1. Executive Summary", styles['CustomHeading1']))
    story.append(Spacer(1, 12))
    
    summary_text = """
    This report provides an in-depth mathematical analysis of the Mean-Variance Optimization (MVO) study 
    conducted on a portfolio of Exchange-Traded Funds (ETFs) and Treasury securities. The study implements 
    Harry Markowitz's Modern Portfolio Theory to construct optimal portfolios that balance expected returns 
    against risk (volatility).
    """
    story.append(Paragraph(summary_text, styles['Justified']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Key Findings:</b>", styles['Normal']))
    story.append(Spacer(1, 6))
    
    try:
        results_df = pd.read_csv(RESULTS_TABLE)
        if not results_df.empty:
            best_sharpe_idx = results_df['sharpe'].idxmax()
            best_result = results_df.loc[best_sharpe_idx]
            
            summary_points = [
                f"• Best performing strategy: {best_result['mu']} returns with {best_result['cov']} covariance",
                f"• Achieved Sharpe ratio: {best_result['sharpe']:.3f}",
                f"• Expected annual return: {best_result['exp_return']:.2%}",
                f"• Target volatility: {best_result['volatility']:.2%}",
                f"• Minimum equity allocation constraint: {EQUITY_MIN:.1%}",
                f"• L2 regularization parameter: {L2_GAMMA}"
            ]
            for point in summary_points:
                story.append(Paragraph(point, styles['Normal']))
                story.append(Spacer(1, 4))
    except Exception as e:
        story.append(Paragraph(f"Note: Results table not yet generated. Run analysis first.", styles['Normal']))
    
    story.append(PageBreak())

    # ========================
    # 2. INTRODUCTION
    # ========================
    story.append(Paragraph("2. Introduction to Mean-Variance Optimization", styles['CustomHeading1']))
    story.append(Spacer(1, 12))
    
    intro_text = """
    Mean-Variance Optimization (MVO), introduced by Harry Markowitz in 1952, is the cornerstone of Modern 
    Portfolio Theory. The fundamental principle is that investors are risk-averse and seek to maximize 
    expected returns for a given level of risk, or equivalently, minimize risk for a target return level.
    """
    story.append(Paragraph(intro_text, styles['Justified']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Core Mathematical Framework:</b>", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    framework_text = """
    The portfolio optimization problem can be formulated as a quadratic programming problem. 
    Given N assets, we seek to find the optimal weight vector <b>w = [w₁, w₂, ..., wₙ]ᵀ</b> where wᵢ 
    represents the fraction of capital allocated to asset i.
    """
    story.append(Paragraph(framework_text, styles['Justified']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Key Variables:</b>", styles['Normal']))
    story.append(Spacer(1, 6))
    
    var_data = [
        ['Symbol', 'Description', 'Dimension'],
        ['<b>w</b>', 'Portfolio weight vector', 'N × 1'],
        ['<b>μ</b>', 'Expected returns vector', 'N × 1'],
        ['<b>Σ</b>', 'Covariance matrix', 'N × N'],
        ['σₚ', 'Portfolio volatility (standard deviation)', 'scalar'],
        ['μₚ', 'Portfolio expected return', 'scalar'],
        ['SR', 'Sharpe ratio', 'scalar']
    ]
    
    var_table = Table(var_data, colWidths=[1*inch, 3.5*inch, 1.5*inch])
    var_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#ecf0f1')])
    ]))
    story.append(var_table)
    story.append(PageBreak())

    # ========================
    # 3. DATA LOADING AND PREPROCESSING
    # ========================
    story.append(Paragraph("3. Data Loading and Preprocessing", styles['CustomHeading1']))
    story.append(Spacer(1, 12))
    
    data_text = """
    The data pipeline processes historical monthly returns for ETFs and Treasury securities. This section 
    details each mathematical transformation applied to ensure data quality and consistency.
    """
    story.append(Paragraph(data_text, styles['Justified']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("3.1 Data Sources", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    sources_text = """
    • <b>ETF Returns:</b> Monthly returns from approved equity and bond ETFs
    <br/>• <b>Treasury Returns:</b> Monthly returns from various maturity U.S. Treasury securities
    <br/>• <b>Frequency:</b> Monthly data, annualized to yearly equivalents
    """
    story.append(Paragraph(sources_text, styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("3.2 Mathematical Data Cleaning Operations", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>Step 1: Monthly Return Compounding</b>", styles['CustomHeading3']))
    story.append(Paragraph("Daily returns are resampled to month-end using geometric compounding:", styles['Normal']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("R_monthly = ∏(1 + r_daily) - 1", styles['Formula']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("where r_daily are the daily returns within each month.", styles['Normal']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Step 2: Missing Data Removal</b>", styles['CustomHeading3']))
    story.append(Paragraph("Assets with >30% missing data are removed to ensure estimation quality:", styles['Normal']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Keep asset i if: (# NaN values / # total observations) < 0.30", styles['Formula']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Step 3: Winsorization</b>", styles['CustomHeading3']))
    story.append(Paragraph("Extreme returns are capped at the 0.5th and 99.5th percentiles to reduce outlier impact:", styles['Normal']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("r_i,t = clip(r_i,t, Q_0.005, Q_0.995)", styles['Formula']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("where Q_p denotes the p-th quantile of returns for asset i.", styles['Normal']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Step 4: Covariance Matrix Sanitization</b>", styles['CustomHeading3']))
    story.append(Paragraph("To ensure positive semi-definiteness, a ridge regularization is applied:", styles['Normal']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("Σ_sanitized = (Σ + Σᵀ)/2 + ε·I", styles['Formula']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("where ε = 10⁻⁴ and I is the identity matrix. This symmetrizes and adds a small diagonal ridge.", styles['Normal']))
    
    story.append(PageBreak())

    # ========================
    # 4. MATHEMATICAL ESTIMATORS
    # ========================
    story.append(Paragraph("4. Mathematical Estimators", styles['CustomHeading1']))
    story.append(Spacer(1, 12))
    
    estimator_intro = """
    Estimating expected returns and covariances from historical data is crucial for portfolio optimization. 
    This study implements multiple estimators to compare their effectiveness.
    """
    story.append(Paragraph(estimator_intro, styles['Justified']))
    story.append(Spacer(1, 12))
    
    # Expected Returns
    story.append(Paragraph("4.1 Expected Returns Calculation", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("<b>4.1.1 Exponential Moving Average (EMA) Returns</b>", styles['CustomHeading3']))
    story.append(Spacer(1, 6))
    
    ema_text = """
    The EMA method gives more weight to recent observations, making it adaptive to changing market conditions. 
    The formula for the EMA expected return of asset i is:
    """
    story.append(Paragraph(ema_text, styles['Normal']))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("μ_i,EMA = [(1 + r̄_i,EMA)^frequency - 1]", styles['Formula']))
    story.append(Spacer(1, 6))
    
    ema_detail = f"""
    where r̄_i,EMA is the exponentially-weighted mean of monthly returns, computed as:
    <br/><br/>
    r̄_i,EMA = Σ_t w_t · r_i,t  /  Σ_t w_t
    <br/><br/>
    with weights w_t = (1 - α)^(T-t), α = 2/(span + 1), and span = {EMA_SPAN} months in this study.
    The frequency parameter = 12 for monthly data (annualization factor).
    """
    story.append(Paragraph(ema_detail, styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>4.1.2 Arithmetic Mean Returns</b>", styles['CustomHeading3']))
    story.append(Spacer(1, 6))
    
    mean_text = """
    The simple arithmetic mean treats all historical observations equally:
    """
    story.append(Paragraph(mean_text, styles['Normal']))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("μ_i,mean = (1/T) · Σ_t r_i,t · frequency", styles['Formula']))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("where T is the number of time periods and frequency = 12 for annualization.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Comparison table
    story.append(Paragraph("<b>Comparison of Return Estimators:</b>", styles['Normal']))
    story.append(Spacer(1, 8))
    
    comp_data = [
        ['Method', 'Weighting', 'Advantages', 'Disadvantages'],
        ['EMA', 'Recent data weighted higher', 'Adapts to regime changes', 'Sensitive to recent volatility'],
        ['Arithmetic Mean', 'All data weighted equally', 'Simple, stable', 'Slow to adapt to changes']
    ]
    
    comp_table = Table(comp_data, colWidths=[1.2*inch, 1.5*inch, 2*inch, 2*inch])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16a085')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#e8f8f5')])
    ]))
    story.append(comp_table)
    
    story.append(PageBreak())
    
    # Covariance Estimation
    story.append(Paragraph("4.2 Covariance Matrix Estimation", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    cov_intro = """
    The covariance matrix Σ captures the relationships between asset returns. It's a critical input 
    for measuring portfolio risk.
    """
    story.append(Paragraph(cov_intro, styles['Justified']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>4.2.1 Sample Covariance Matrix</b>", styles['CustomHeading3']))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("The sample covariance between assets i and j is calculated as:", styles['Normal']))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("Σ_ij = [1/(T-1)] · Σ_t (r_i,t - r̄_i)(r_j,t - r̄_j) · frequency", styles['Formula']))
    story.append(Spacer(1, 6))
    
    story.append(Paragraph("where r̄_i is the mean return of asset i, T is the sample size, and frequency = 12 for annualization.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>4.2.2 Ledoit-Wolf Shrinkage Covariance</b>", styles['CustomHeading3']))
    story.append(Spacer(1, 6))
    
    lw_text = """
    The Ledoit-Wolf estimator addresses the instability of sample covariance matrices, especially when 
    the number of assets is large relative to the number of observations. It shrinks the sample covariance 
    toward a structured target:
    """
    story.append(Paragraph(lw_text, styles['Justified']))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("Σ_LW = δ·F + (1-δ)·S", styles['Formula']))
    story.append(Spacer(1, 6))
    
    lw_detail = """
    where:
    <br/>• S = sample covariance matrix
    <br/>• F = shrinkage target (constant variance structure)
    <br/>• δ = shrinkage intensity (0 ≤ δ ≤ 1), optimally chosen to minimize expected loss
    <br/><br/>
    The constant variance target F is a diagonal matrix with equal variances, providing a more stable estimate.
    """
    story.append(Paragraph(lw_detail, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Properties comparison
    story.append(Paragraph("<b>Covariance Estimator Properties:</b>", styles['Normal']))
    story.append(Spacer(1, 8))
    
    cov_prop_data = [
        ['Property', 'Sample Covariance', 'Ledoit-Wolf'],
        ['Estimation error', 'Higher (especially with many assets)', 'Lower (shrinkage reduces noise)'],
        ['Stability', 'Less stable', 'More stable'],
        ['Eigenvalue spectrum', 'Can have very small eigenvalues', 'Better conditioned'],
        ['Best used when', 'T >> N (many observations)', 'N comparable to T']
    ]
    
    cov_prop_table = Table(cov_prop_data, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
    cov_prop_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#8e44ad')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f4ecf7')])
    ]))
    story.append(cov_prop_table)
    
    story.append(PageBreak())

    # ========================
    # 5. OPTIMIZATION FRAMEWORK
    # ========================
    story.append(Paragraph("5. Optimization Framework", styles['CustomHeading1']))
    story.append(Spacer(1, 12))
    
    opt_intro = """
    The portfolio optimization framework uses convex optimization to find optimal asset weights. 
    This section details the mathematical formulations of each objective function used in the study.
    """
    story.append(Paragraph(opt_intro, styles['Justified']))
    story.append(Spacer(1, 12))
    
    # Portfolio Variance
    story.append(Paragraph("5.1 Portfolio Variance (Risk Measure)", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    var_text = """
    Portfolio variance is the fundamental measure of risk in mean-variance optimization. 
    It represents the expected squared deviation of portfolio returns from their mean:
    """
    story.append(Paragraph(var_text, styles['Justified']))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("σ²_p = w<sup>T</sup>Σw = Σ_i Σ_j w_i w_j Σ_ij", styles['Formula']))
    story.append(Spacer(1, 6))
    
    var_detail = """
    where:
    <br/>• σ²_p = portfolio variance
    <br/>• w = N×1 weight vector
    <br/>• Σ = N×N covariance matrix
    <br/>• Σ_ij = covariance between assets i and j
    <br/><br/>
    Portfolio volatility (standard deviation) is: σ_p = √(w<sup>T</sup>Σw)
    """
    story.append(Paragraph(var_detail, styles['Normal']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Minimum Volatility Problem:</b>", styles['Normal']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("minimize: w<sup>T</sup>Σw", styles['Formula']))
    story.append(Paragraph("subject to: Σ_i w_i = 1, w_i ≥ 0", styles['Formula']))
    
    story.append(Spacer(1, 12))
    
    # Sharpe Ratio
    story.append(Paragraph("5.2 Sharpe Ratio Maximization", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    sharpe_text = """
    The Sharpe ratio measures risk-adjusted returns. It represents the excess return per unit of risk:
    """
    story.append(Paragraph(sharpe_text, styles['Normal']))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("SR = (μ_p - r_f) / σ_p = (w<sup>T</sup>μ - r_f) / √(w<sup>T</sup>Σw)", styles['Formula']))
    story.append(Spacer(1, 6))
    
    sharpe_detail = """
    where:
    <br/>• μ_p = w<sup>T</sup>μ = portfolio expected return
    <br/>• r_f = risk-free rate (typically set to 0 in this study)
    <br/>• σ_p = portfolio volatility
    <br/><br/>
    Higher Sharpe ratios indicate better risk-adjusted performance.
    """
    story.append(Paragraph(sharpe_detail, styles['Normal']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("<b>Maximum Sharpe Ratio Problem:</b>", styles['Normal']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("maximize: (w<sup>T</sup>μ - r_f) / √(w<sup>T</sup>Σw)", styles['Formula']))
    story.append(Paragraph("subject to: Σ_i w_i = 1, w_i ≥ 0", styles['Formula']))
    
    story.append(PageBreak())
    
    # Efficient Risk
    story.append(Paragraph("5.3 Efficient Risk Optimization", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    eff_risk_text = """
    The efficient risk objective finds the portfolio with maximum expected return for a given target volatility. 
    This is the approach used primarily in this study.
    """
    story.append(Paragraph(eff_risk_text, styles['Justified']))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(f"<b>Efficient Risk Problem (Target Volatility = {VOL_TARGET:.1%}):</b>", styles['Normal']))
    story.append(Spacer(1, 6))
    story.append(Paragraph("maximize: w<sup>T</sup>μ", styles['Formula']))
    story.append(Paragraph(f"subject to: √(w<sup>T</sup>Σw) ≤ {VOL_TARGET}", styles['Formula']))
    story.append(Paragraph("           Σ_i w_i = 1, w_i ≥ 0", styles['Formula']))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph("This formulation constrains the portfolio volatility while maximizing expected returns.", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # L2 Regularization
    story.append(Paragraph("5.4 L2 Regularization", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    l2_text = """
    L2 regularization is added to the objective function to encourage diversification and reduce 
    over-concentration in individual assets. It penalizes the squared magnitude of weights:
    """
    story.append(Paragraph(l2_text, styles['Justified']))
    story.append(Spacer(1, 8))
    
    story.append(Paragraph(f"L2 penalty = γ · ||w||² = γ · Σ_i w_i²  (γ = {L2_GAMMA})", styles['Formula']))
    story.append(Spacer(1, 6))
    
    l2_detail = """
    The L2 term is added to the optimization objective:
    <br/><br/>
    minimize: -w<sup>T</sup>μ + γ·Σ_i w_i²
    <br/><br/>
    A higher γ leads to more diversified portfolios with smaller individual position sizes. 
    In this study, γ = 0.1 provides a balance between concentration and diversification.
    """
    story.append(Paragraph(l2_detail, styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Mathematical interpretation
    story.append(Paragraph("<b>Mathematical Interpretation:</b>", styles['Normal']))
    story.append(Spacer(1, 6))
    
    interpretation = """
    • Without L2: Solution may concentrate heavily in few assets<br/>
    • With L2: Solution spreads weights more evenly<br/>
    • Trade-off: Slightly lower theoretical Sharpe ratio but more robust out-of-sample performance
    """
    story.append(Paragraph(interpretation, styles['Normal']))
    
    story.append(PageBreak())

    # ========================
    # 6. CONSTRAINTS AND BOUNDS
    # ========================
    story.append(Paragraph("6. Constraints and Bounds", styles['CustomHeading1']))
    story.append(Spacer(1, 12))
    
    constraint_intro = """
    Constraints are mathematical conditions that must be satisfied by the optimal solution. 
    This study implements several practical constraints to ensure realistic and policy-compliant portfolios.
    """
    story.append(Paragraph(constraint_intro, styles['Justified']))
    story.append(Spacer(1, 12))
    
    constraint_data = [
        ['Constraint Type', 'Mathematical Form', 'Purpose'],
        ['<b>Fully Invested</b>', 'Σ_i w_i = 1', 'All capital is allocated'],
        ['<b>Long-Only</b>', 'w_i ≥ 0 for all i', 'No short selling allowed'],
        ['<b>Upper Bound</b>', 'w_i ≤ 1 for all i', 'No single asset can exceed 100%'],
        ['<b>Equity Minimum</b>', f'Σ_(i∈equity) w_i ≥ {EQUITY_MIN}', 'Maintain minimum equity exposure'],
        ['<b>Risk Target</b>', f'√(w<sup>T</sup>Σw) ≤ {VOL_TARGET}', 'Constrain portfolio volatility']
    ]
    
    constraint_table = Table(constraint_data, colWidths=[1.5*inch, 2.5*inch, 2.5*inch])
    constraint_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e74c3c')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#fadbd8')])
    ]))
    story.append(constraint_table)
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("<b>Practical Implications:</b>", styles['Normal']))
    story.append(Spacer(1, 8))
    
    implications = f"""
    The equity minimum constraint (≥{EQUITY_MIN:.0%}) ensures the portfolio maintains significant exposure 
    to growth assets. This is a policy requirement that balances long-term growth objectives with risk management. 
    Combined with the volatility constraint (≤{VOL_TARGET:.0%}), the optimization finds the highest expected 
    return portfolio that satisfies all practical requirements.
    """
    story.append(Paragraph(implications, styles['Justified']))
    
    story.append(PageBreak())

    # ========================
    # 7. RESULTS AND ANALYSIS
    # ========================
    story.append(Paragraph("7. Results and Analysis", styles['CustomHeading1']))
    story.append(Spacer(1, 12))
    
    try:
        results_df = pd.read_csv(RESULTS_TABLE)
        
        story.append(Paragraph("7.1 Portfolio Performance Summary", styles['CustomHeading2']))
        story.append(Spacer(1, 8))
        
        # Results table
        table_data = [['Return Estimator', 'Covariance Method', 'Expected Return', 'Volatility', 'Sharpe Ratio', 'Treasury Bond']]
        for _, row in results_df.iterrows():
            treasury_short = str(row.get('selected_treasury', ''))[:30] + '...' if len(str(row.get('selected_treasury', ''))) > 30 else str(row.get('selected_treasury', ''))
            table_data.append([
                row['mu'], 
                row['cov'], 
                f"{row['exp_return']:.2%}", 
                f"{row['volatility']:.2%}", 
                f"{row['sharpe']:.3f}",
                treasury_short
            ])
        
        results_table = Table(table_data, colWidths=[1*inch, 1*inch, 1*inch, 0.9*inch, 0.9*inch, 1.8*inch])
        results_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 8),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#ecf0f1')])
        ]))
        story.append(results_table)
        story.append(Spacer(1, 12))
        
        # Analysis text
        best_idx = results_df['sharpe'].idxmax()
        best = results_df.loc[best_idx]
        
        analysis_text = f"""
        The results demonstrate that the <b>{best['mu']}</b> expected returns estimator combined with 
        <b>{best['cov']}</b> covariance estimation produces the best risk-adjusted performance with a 
        Sharpe ratio of <b>{best['sharpe']:.3f}</b>. This portfolio achieves an expected annual return 
        of <b>{best['exp_return']:.2%}</b> with volatility constrained at <b>{VOL_TARGET:.1%}</b>.
        """
        story.append(Paragraph(analysis_text, styles['Justified']))
        story.append(Spacer(1, 12))
        
        # Add plots if they exist
        story.append(Paragraph("7.2 Portfolio Allocation Visualizations", styles['CustomHeading2']))
        story.append(Spacer(1, 8))
        
        # Try to add allocation plots
        for _, row in results_df.iterrows():
            plot_file = f"{PLOT_ALLOC[:-4]}_{row['mu']}_{row['cov']}.png"
            if os.path.exists(plot_file):
                story.append(Paragraph(f"<b>{row['mu']} Returns / {row['cov']} Covariance:</b>", styles['Normal']))
                story.append(Spacer(1, 6))
                story.append(Image(plot_file, width=5.5*inch, height=2.5*inch))
                story.append(Spacer(1, 12))
        
        story.append(PageBreak())
        
        # Efficient Frontier
        story.append(Paragraph("7.3 Efficient Frontier", styles['CustomHeading2']))
        story.append(Spacer(1, 8))
        
        ef_text = """
        The efficient frontier represents the set of optimal portfolios that offer the highest expected 
        return for each level of risk. Points on the frontier dominate all other portfolios in the 
        risk-return space.
        """
        story.append(Paragraph(ef_text, styles['Justified']))
        story.append(Spacer(1, 12))
        
        if os.path.exists(PLOT_EF):
            story.append(Image(PLOT_EF, width=5.5*inch, height=4*inch))
            story.append(Spacer(1, 12))
        
        ef_explain = """
        The plot shows:
        <br/>• The efficient frontier curve (optimal portfolios)
        <br/>• Individual asset positions
        <br/>• Random portfolios (for comparison)
        <br/>• The maximum Sharpe ratio portfolio (if computed)
        <br/><br/>
        Portfolios above the frontier are not achievable, while those below are sub-optimal.
        """
        story.append(Paragraph(ef_explain, styles['Normal']))
        
    except Exception as e:
        story.append(Paragraph(f"Results not available. Please run the analysis script first. Error: {e}", styles['Normal']))
    
    story.append(PageBreak())

    # ========================
    # 8. DISCUSSION
    # ========================
    story.append(Paragraph("8. Discussion and Interpretation", styles['CustomHeading1']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("8.1 Estimator Choice and Performance", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    discussion1 = """
    The choice of estimators significantly impacts portfolio performance. The Exponential Moving Average (EMA) 
    approach for expected returns provides better adaptation to recent market conditions compared to simple 
    arithmetic means. By assigning higher weights to recent observations, EMA captures momentum and regime 
    changes more effectively.
    """
    story.append(Paragraph(discussion1, styles['Justified']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("8.2 Covariance Matrix Stability", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    discussion2 = """
    The Ledoit-Wolf shrinkage estimator addresses a fundamental challenge in covariance estimation: when the 
    number of assets (N) approaches the number of observations (T), sample covariance matrices become 
    ill-conditioned and noisy. Shrinkage toward a structured target improves conditioning and reduces 
    estimation error, leading to more stable optimal portfolios.
    """
    story.append(Paragraph(discussion2, styles['Justified']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("8.3 Regularization Effects", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    discussion3 = f"""
    L2 regularization (γ = {L2_GAMMA}) prevents over-concentration in a few assets. While this may slightly 
    reduce the theoretical in-sample Sharpe ratio, it improves out-of-sample robustness by:
    <br/>• Reducing sensitivity to estimation errors
    <br/>• Encouraging diversification
    <br/>• Limiting extreme positions that may arise from data mining
    """
    story.append(Paragraph(discussion3, styles['Justified']))
    story.append(Spacer(1, 12))
    
    story.append(Paragraph("8.4 Constraint Trade-offs", styles['CustomHeading2']))
    story.append(Spacer(1, 8))
    
    discussion4 = f"""
    The equity minimum constraint ({EQUITY_MIN:.0%}) reflects a strategic asset allocation decision, 
    balancing growth objectives against risk management. This constraint may reduce the achievable 
    Sharpe ratio compared to an unconstrained optimization, but ensures the portfolio aligns with 
    long-term investment goals and policy requirements.
    """
    story.append(Paragraph(discussion4, styles['Justified']))
    
    story.append(PageBreak())

    # ========================
    # 9. CONCLUSION
    # ========================
    story.append(Paragraph("9. Conclusion", styles['CustomHeading1']))
    story.append(Spacer(1, 12))
    
    conclusion = """
    This comprehensive mathematical analysis of the Mean-Variance Optimization study demonstrates the 
    effectiveness of modern portfolio theory in constructing efficient portfolios from ETFs and Treasury 
    securities. The key findings are:
    """
    story.append(Paragraph(conclusion, styles['Justified']))
    story.append(Spacer(1, 12))
    
    key_findings = """
    <b>1. Estimator Selection Matters:</b> EMA returns with Ledoit-Wolf covariance provides superior 
    risk-adjusted performance by balancing responsiveness with stability.
    <br/><br/>
    <b>2. Regularization Improves Robustness:</b> L2 regularization reduces over-fitting and 
    encourages practical diversification.
    <br/><br/>
    <b>3. Constraints Ensure Practicality:</b> The equity minimum and volatility constraints 
    align mathematical optimization with real-world investment policies.
    <br/><br/>
    <b>4. Mathematical Rigor:</b> Each operation—from data cleaning through optimization—follows 
    established mathematical principles, ensuring reproducibility and interpretability.
    <br/><br/>
    <b>5. Comprehensive Framework:</b> The combination of multiple estimators, robust covariance 
    estimation, and thoughtful constraints creates a practical and theoretically sound approach 
    to portfolio construction.
    """
    story.append(Paragraph(key_findings, styles['Normal']))
    story.append(Spacer(1, 12))
    
    final_text = """
    This report provides a complete mathematical foundation for understanding the MVO study. 
    Every computational step—from exponentially-weighted means to quadratic programming 
    solutions—is grounded in established financial mathematics. The framework is both rigorous 
    and practical, suitable for institutional portfolio management.
    """
    story.append(Paragraph(final_text, styles['Justified']))
    
    story.append(PageBreak())

    # ========================
    # 10. REFERENCES
    # ========================
    story.append(Paragraph("10. References", styles['CustomHeading1']))
    story.append(Spacer(1, 12))
    
    refs = [
        ("<b>[1]</b> Markowitz, H. (1952). Portfolio Selection. <i>The Journal of Finance</i>, 7(1), 77-91.", 
         "The foundational paper introducing mean-variance optimization."),
        
        ("<b>[2]</b> Ledoit, O., & Wolf, M. (2004). A well-conditioned estimator for large-dimensional "
         "covariance matrices. <i>Journal of Multivariate Analysis</i>, 88(2), 365-411.", 
         "Introduces the shrinkage estimator used in this study."),
        
        ("<b>[3]</b> Sharpe, W. F. (1966). Mutual Fund Performance. <i>Journal of Business</i>, 39(1), 119-138.", 
         "Defines the Sharpe ratio used for performance evaluation."),
        
        ("<b>[4]</b> Boyd, S., & Vandenberghe, L. (2004). <i>Convex Optimization</i>. Cambridge University Press.", 
         "Comprehensive reference for the optimization methods used."),
        
        ("<b>[5]</b> PyPortfolioOpt Documentation. https://pyportfolioopt.readthedocs.io/", 
         "Official documentation for the portfolio optimization library."),
        
        ("<b>[6]</b> CVXPY: A Python-embedded modeling language for convex optimization. "
         "https://www.cvxpy.org/", 
         "The convex optimization solver used in this implementation.")
    ]
    
    for ref, description in refs:
        story.append(Paragraph(ref, styles['Normal']))
        story.append(Spacer(1, 4))
        story.append(Paragraph(f"<i>{description}</i>", styles['Normal']))
        story.append(Spacer(1, 10))

    # Build the PDF
    doc.build(story)
    print(f"PDF report generated successfully: {REPORT_PDF}")

if __name__ == "__main__":
    make_pdf_report()
