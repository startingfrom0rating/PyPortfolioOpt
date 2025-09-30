class Allocation {
    equity: number;
    etfs: number;
    bonds: number;

    constructor(equity: number, etfs: number, bonds: number) {
        this.equity = equity;
        this.etfs = etfs;
        this.bonds = bonds;
    }

    totalAllocation(): number {
        return this.equity + this.etfs + this.bonds;
    }

    validatePercentages(): boolean {
        const total = this.totalAllocation();
        return total === 100 && this.equity > (this.etfs + this.bonds);
    }
}

export default Allocation;