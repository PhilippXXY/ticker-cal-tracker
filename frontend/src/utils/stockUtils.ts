import api from '../api/axios';

interface StockQuote {
    c: number; // Current price
    d: number; // Change
    dp: number; // Percent change
    h: number; // High
    l: number; // Low
    o: number; // Open
    pc: number; // Previous close
}

export const fetchStockQuote = async (symbol: string): Promise<StockQuote | null> => {
    try {
        const response = await api.get<StockQuote>(`/api/stocks/${symbol}/quote`);
        return response.data;
    } catch (error) {
        console.error(`Error fetching quote for ${symbol}:`, error);
        return null;
    }
};
