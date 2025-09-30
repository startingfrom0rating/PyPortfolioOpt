import express from 'express';
import { calculateAllocation } from './services/calculator';

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.json());

app.post('/allocate', (req, res) => {
    const { equity, etfs, bonds } = req.body;

    try {
        const allocation = calculateAllocation(equity, etfs, bonds);
        res.status(200).json(allocation);
    } catch (error) {
        res.status(400).json({ error: error.message });
    }
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});