from __future__ import annotations

from .frontier_app import generate_frontier_output
from ..scripts.config import PLOT_EF, EQUITY_MIN, L2_GAMMA


def main():
    generate_frontier_output(PLOT_EF, equity_min=EQUITY_MIN, l2_gamma=L2_GAMMA, mu_mode='EMA', target_vol=0.12)


if __name__ == "__main__":
    main()
