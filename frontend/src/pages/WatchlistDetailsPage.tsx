import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../api/axios';
import { fetchStockQuote } from '../utils/stockUtils';
import StockCard from '../components/StockCard';

// -- Types --
interface Stock {
    ticker: string;
    name: string;
}

interface StockQuoteData {
    c: number;  // Current Price
    d: number;  // Change
    dp: number; // Percent Change
}

const WatchlistDetailsPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();

    // -- State --
    const [stocks, setStocks] = useState<Stock[]>([]);
    const [quotes, setQuotes] = useState<Record<string, StockQuoteData>>({});
    const [tickerInput, setTickerInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isAdding, setIsAdding] = useState(false);

    // -- Effects --

    // 1. Fetch stocks when ID changes
    useEffect(() => {
        if (id) fetchStocksInWatchlist();
    }, [id]);

    // 2. Fetch prices when stocks list changes
    useEffect(() => {
        const loadRealtimeQuotes = async () => {
            const newQuotes: Record<string, StockQuoteData> = {};

            for (const stock of stocks) {
                // Avoid re-fetching if we already have data (simple cache)
                if (quotes[stock.ticker]) continue;

                const quote = await fetchStockQuote(stock.ticker);
                if (quote) {
                    newQuotes[stock.ticker] = {
                        c: quote.c,
                        d: quote.d,
                        dp: quote.dp
                    };
                } else {
                    // Fallback if API fails (e.g., missing key or bad ticker)
                    // We set 'c' to -1 or 0 to indicate invalid data, avoiding infinite "Loading..."
                    newQuotes[stock.ticker] = {
                        c: 0,
                        d: 0,
                        dp: 0
                    };
                }
            }

            // Only update state if we fetched something new
            if (Object.keys(newQuotes).length > 0) {
                setQuotes(prev => ({ ...prev, ...newQuotes }));
            }
        };

        if (stocks.length > 0) {
            loadRealtimeQuotes();
        }
    }, [stocks]); // Note: We deliberately exclude 'quotes' to avoid infinite loops

    // -- Actions --

    const fetchStocksInWatchlist = async () => {
        try {
            setIsLoading(true);
            const response = await api.get<Stock[]>(`/api/watchlists/${id}/stocks`);
            setStocks(response.data);
        } catch (err) {
            console.error("Failed to load stocks:", err);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAddStock = async () => {
        if (!tickerInput.trim()) return;

        try {
            setIsAdding(true);
            const symbol = tickerInput.trim().toUpperCase();
            await api.post(`/api/watchlists/${id}/stocks/${symbol}`);

            // Clear input and reload list
            setTickerInput('');
            fetchStocksInWatchlist();
        } catch (err) {
            console.error("Add stock error:", err);
            alert('Failed to add stock. Please verify the ticker symbol.');
        } finally {
            setIsAdding(false);
        }
    };

    const handleRemoveStock = async (ticker: string) => {
        if (!window.confirm(`Are you sure you want to remove ${ticker}?`)) return;

        try {
            await api.delete(`/api/watchlists/${id}/stocks/${ticker}`);
            fetchStocksInWatchlist(); // Reload list
        } catch (err) {
            console.error("Remove stock error:", err);
            alert(`Failed to remove ${ticker}. Check console for details.`);
        }
    }

    // -- Render --
    return (
        <div className="min-h-screen bg-slate-900 p-8 text-white">
            {/* Header / Nav */}
            <Link to="/watchlists" className="text-gray-400 hover:text-white mb-8 inline-flex items-center transition-colors">
                <span className="mr-2">←</span> Back to Watchlists
            </Link>

            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10 gap-6">
                <div>
                    <h1 className="text-4xl font-bold tracking-tight mb-2">Watchlist Details</h1>
                    <p className="text-gray-400">Track your favorite stocks in real-time.</p>
                </div>

                {/* Add Stock Input */}
                <div className="flex gap-3 w-full md:w-auto">
                    <input
                        value={tickerInput}
                        onChange={(e) => setTickerInput(e.target.value)}
                        placeholder="Symbol (e.g. MSFT)"
                        className="p-3 rounded-lg bg-slate-800 border border-slate-700 focus:outline-none focus:border-blue-500 transition-colors w-full md:w-64 uppercase font-medium tracking-wide placeholder-gray-500"
                        onKeyDown={(e) => e.key === 'Enter' && handleAddStock()}
                        disabled={isAdding}
                    />
                    <button
                        onClick={handleAddStock}
                        disabled={isAdding}
                        className="bg-blue-600 px-6 py-3 rounded-lg hover:bg-blue-500 transition-all font-semibold disabled:opacity-50 flex-shrink-0"
                    >
                        {isAdding ? 'Adding...' : 'Add Stock'}
                    </button>
                </div>
            </div>

            {/* Loading State */}
            {isLoading && (
                <div className="flex justify-center py-20">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                </div>
            )}

            {/* Stock Grid */}
            {!isLoading && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {stocks.map(stock => (
                        <StockCard
                            key={stock.ticker}
                            ticker={stock.ticker}
                            name={stock.name}
                            // Pass down price data if available
                            price={quotes[stock.ticker]?.c}
                            change={quotes[stock.ticker]?.d}
                            percentChange={quotes[stock.ticker]?.dp}
                            onRemove={() => handleRemoveStock(stock.ticker)}
                        />
                    ))}

                    {/* Empty State */}
                    {stocks.length === 0 && (
                        <div className="col-span-full py-20 text-center border-2 border-dashed border-slate-800 rounded-xl bg-slate-800/20">
                            <p className="text-gray-500 text-lg">No stocks in this watchlist yet.</p>
                            <p className="text-gray-600 text-sm mt-2">Add a symbol above to start tracking.</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default WatchlistDetailsPage;
