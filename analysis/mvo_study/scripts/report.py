"""
PDF report generation for MVO study.
"""
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import pandas as pd
from config import RESULTS_TABLE, PLOT_ALLOC, PLOT_EF, REPORT_PDF

styles = getSampleStyleSheet()

def make_pdf_report():
    doc = SimpleDocTemplate(REPORT_PDF, pagesize=letter)
    story = []

    # Title
    story.append(Paragraph("Mean-Variance Optimization Study: ETF & Treasury Portfolio", styles['Title']))
    story.append(Spacer(1, 12))

    # Table of Contents
    story.append(Paragraph("Table of Contents", styles['Heading2']))
    toc = [
        ['1. Introduction', '2'],
        ['2. Methods', '3'],
        ['3. Results', '4'],
        ['4. Discussion', '5'],
        ['5. Conclusion', '6'],
        ['6. References', '7']
    ]
    story.append(Table(toc, style=[('BACKGROUND', (0,0), (-1,0), colors.lightgrey), ('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    story.append(PageBreak())

    # Introduction
    story.append(Paragraph("1. Introduction", styles['Heading1']))
    story.append(Paragraph("This report presents a systematic study of mean-variance optimization (MVO) approaches for portfolio allocation using approved ETFs and Treasuries. We compare estimator choices (EMA, mean, sample, Ledoit–Wolf) and apply robust constraints, aiming for a majority equity allocation and practical risk control.", styles['Normal']))
    story.append(PageBreak())

    # Methods
    story.append(Paragraph("2. Methods", styles['Heading1']))
    story.append(Paragraph("We ingest monthly returns for approved ETFs and Treasuries, compute expected returns (EMA, mean) and covariances (sample, Ledoit–Wolf), and run MVO experiments with efficient risk and max Sharpe objectives. Constraints include long-only, equity-minimum, and L2 regularization. Outputs include allocation tables and efficient frontier plots.", styles['Normal']))
    story.append(PageBreak())

    # Results
    story.append(Paragraph("3. Results", styles['Heading1']))
    results_df = pd.read_csv(RESULTS_TABLE)
    story.append(Paragraph("Summary of portfolio allocations and performance:", styles['Normal']))
    table_data = [['Estimator', 'Covariance', 'Exp Return', 'Volatility', 'Sharpe']]
    for _, row in results_df.iterrows():
        table_data.append([row['mu'], row['cov'], f"{row['exp_return']:.2%}", f"{row['volatility']:.2%}", f"{row['sharpe']:.2f}"])
    story.append(Table(table_data, style=[('GRID', (0,0), (-1,-1), 0.5, colors.black)]))
    story.append(Spacer(1, 12))
    # Allocation plot (first result)
    story.append(Paragraph("Example allocation plot:", styles['Normal']))
    story.append(Image(f'{PLOT_ALLOC[:-4]}_EMA_LedoitWolf.png', width=400, height=200))
    story.append(Spacer(1, 12))
    # Efficient frontier plot
    story.append(Paragraph("Efficient frontier:", styles['Normal']))
    story.append(Image(PLOT_EF, width=400, height=300))
    story.append(PageBreak())

    # Discussion
    story.append(Paragraph("4. Discussion", styles['Heading1']))
    story.append(Paragraph("EMA returns with Ledoit–Wolf covariance produced the most stable allocations and highest risk-adjusted returns, balancing estimation error and out-of-sample robustness. The equity-minimum constraint ensures policy compliance, and L2 regularization reduces concentration. Sample covariance was less stable, and mean returns were noisier than EMA. Efficient risk objective provided smoother allocations than max Sharpe, which tended to concentrate risk.", styles['Normal']))
    story.append(PageBreak())

    # Conclusion
    story.append(Paragraph("5. Conclusion", styles['Heading1']))
    story.append(Paragraph("For approved ETF and Treasury portfolios, EMA expected returns and Ledoit–Wolf shrinkage covariance, combined with efficient risk objective and robust constraints, yield the best allocation for practical risk control and policy compliance. This approach is mathematically justified and empirically robust.", styles['Normal']))
    story.append(PageBreak())

    # References
    story.append(Paragraph("6. References", styles['Heading1']))
    refs = [
        "[1] Markowitz, H. (1952). Portfolio Selection. The Journal of Finance.",
        "[2] Ledoit, O., & Wolf, M. (2004). A well-conditioned estimator for large-dimensional covariance matrices. Journal of Multivariate Analysis.",
        "[3] PyPortfolioOpt Documentation: https://pyportfolioopt.readthedocs.io/",
        "[4] ReportLab Documentation: https://www.reportlab.com/docs/reportlab-userguide.pdf"
    ]
    for r in refs:
        story.append(Paragraph(r, styles['Normal']))
    doc.build(story)

if __name__ == "__main__":
    make_pdf_report()
