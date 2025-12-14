import api from '../axios';

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
        const response = await api.get('/api/watchlists/'); // Checked route: /api/watchlists
        return response.data;
    },

    getById: async (id: string): Promise<Watchlist> => {
        const response = await api.get(`/api/watchlists/${id}`);
        return response.data;
    },

    create: async (data: CreateWatchlistData): Promise<Watchlist> => {
        const response = await api.post('/api/watchlists/', data);
        return response.data;
    },

    update: async (id: string, data: CreateWatchlistData): Promise<Watchlist> => {
        // Backend might not support PUT /watchlists/{id} yet, but keeping for completeness
        const response = await api.put(`/api/watchlists/${id}`, data);
        return response.data;
    },

    delete: async (id: string): Promise<void> => {
        await api.delete(`/api/watchlists/${id}`);
    },

    getStocks: async (id: string): Promise<Stock[]> => {
        const response = await api.get(`/api/watchlists/${id}/stocks`);
        return response.data;
    },

    addStock: async (id: string, ticker: string): Promise<void> => {
        await api.post(`/api/watchlists/${id}/stocks/${ticker}`);
    },

    removeStock: async (id: string, ticker: string): Promise<void> => {
        await api.delete(`/api/watchlists/${id}/stocks/${ticker}`);
    },
};
