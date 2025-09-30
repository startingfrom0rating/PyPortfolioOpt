"""
Configuration for MVO study analysis.
"""
import os
"""
Note: We treat the file 'etfs_invalid.csv' as the approved ETF whitelist for this study.
To rename physically later, add 'ETF_WHITELIST_FILE = os.path.join(DATA_DIR, "etfs_whitelist.csv")'
and adjust the loader accordingly.
"""

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..', 'data'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'output'))

ETF_RETURNS_FILE = os.path.join(DATA_DIR, 'etfs_returns.csv')
TREASURY_RETURNS_FILE = os.path.join(DATA_DIR, 'treasuries_returns_monthly.csv')
ETF_IDENTIFIERS_FILE = os.path.join(DATA_DIR, 'etfs_identifiers.csv')
# Explicit whitelist (rename-ready): duplicate of legacy 'etfs_invalid.csv'
ETF_WHITELIST_FILE = os.path.join(DATA_DIR, 'etfs_whitelist.csv')
ETF_INVALID_FILE = os.path.join(DATA_DIR, 'etfs_invalid.csv')  # legacy name retained for now
TREASURY_MAP_FILE = os.path.join(DATA_DIR, 'fred_mapping_treasuries.csv')

# Analysis parameters
VOL_TARGET = 0.12  # Target annualized volatility
EQUITY_MIN = 0.5   # Minimum equity allocation (fraction)
L2_GAMMA = 0.1     # L2 regularization strength
EMA_SPAN = 36      # EMA span (months)

# Output filenames
RESULTS_TABLE = os.path.join(OUTPUT_DIR, 'results_table.csv')
PLOT_ALLOC = os.path.join(OUTPUT_DIR, 'allocation_plot.png')
PLOT_EF = os.path.join(OUTPUT_DIR, 'efficient_frontier.png')
REPORT_PDF = os.path.join(OUTPUT_DIR, 'mvo_report.pdf')
