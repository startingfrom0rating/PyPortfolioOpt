export function calculateAllocation(equity: number, etfs: number, bonds: number): { allocation: { equity: number; etfs: number; bonds: number }; valid: boolean; message: string } {
    const total = equity + etfs + bonds;

    if (total !== 100) {
        return {
            allocation: { equity, etfs, bonds },
            valid: false,
            message: "Total allocation must equal 100%",
        };
    }

    if (equity <= 50) {
        return {
            allocation: { equity, etfs, bonds },
            valid: false,
            message: "Equity must be the majority (more than 50%)",
        };
    }

    return {
        allocation: { equity, etfs, bonds },
        valid: true,
        message: "Allocation is valid",
    };
}