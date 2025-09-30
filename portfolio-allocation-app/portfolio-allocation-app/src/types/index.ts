export interface AllocationInput {
    equity: number;
    etfs: number;
    bonds: number;
}

export interface AllocationResult {
    total: number;
    isEquityMajority: boolean;
}