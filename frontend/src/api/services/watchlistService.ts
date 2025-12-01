import axios from '../axios';

export interface Watchlist {
    id: string;
    name: string;
    created_at: string;
    stock_count?: number;
}

export interface CreateWatchlistData {
    name: string;
}

export interface Stock {
    ticker: string;
    name: string;
    last_updated: string;
    current_price?: number;
    change_percent?: number;
}

export const watchlistService = {
    getAll: async (): Promise<Watchlist[]> => {
        const response = await axios.get('/watchlists/');
        return response.data;
    },

    getById: async (id: string): Promise<Watchlist> => {
        const response = await axios.get(`/watchlists/${id}`);
        return response.data;
    },

    create: async (data: CreateWatchlistData): Promise<Watchlist> => {
        const response = await axios.post('/watchlists/', data);
        return response.data;
    },

    update: async (id: string, data: CreateWatchlistData): Promise<Watchlist> => {
        const response = await axios.put(`/watchlists/${id}`, data);
        return response.data;
    },

    delete: async (id: string): Promise<void> => {
        await axios.delete(`/watchlists/${id}`);
    },

    getStocks: async (id: string): Promise<Stock[]> => {
        const response = await axios.get(`/watchlists/${id}/stocks`);
        return response.data;
    },

    addStock: async (id: string, ticker: string): Promise<void> => {
        await axios.post(`/watchlists/${id}/stocks/${ticker}`);
    },

    removeStock: async (id: string, ticker: string): Promise<void> => {
        await axios.delete(`/watchlists/${id}/stocks/${ticker}`);
    },
};
