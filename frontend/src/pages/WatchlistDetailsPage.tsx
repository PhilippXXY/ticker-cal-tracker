import React, { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Plus, Trash2, TrendingUp, TrendingDown, Calendar } from 'lucide-react';
import { watchlistService } from '../api/services/watchlistService';
import type { Stock } from '../api/services/watchlistService';

const WatchlistDetailsPage = () => {
    const { id } = useParams<{ id: string }>();
    const queryClient = useQueryClient();
    const [newTicker, setNewTicker] = useState('');
    const [addError, setAddError] = useState('');

    const { data: watchlist, isLoading: isLoadingWatchlist } = useQuery({
        queryKey: ['watchlist', id],
        queryFn: () => watchlistService.getById(id!),
        enabled: !!id,
    });

    const { data: stocks, isLoading: isLoadingStocks } = useQuery({
        queryKey: ['watchlist-stocks', id],
        queryFn: () => watchlistService.getStocks(id!),
        enabled: !!id,
    });

    const addStockMutation = useMutation({
        mutationFn: (ticker: string) => watchlistService.addStock(id!, ticker),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['watchlist-stocks', id] });
            queryClient.invalidateQueries({ queryKey: ['watchlists'] }); // Update counts
            setNewTicker('');
            setAddError('');
        },
        onError: (error: any) => {
            setAddError(error.response?.data?.message || 'Failed to add stock');
        },
    });

    const removeStockMutation = useMutation({
        mutationFn: (ticker: string) => watchlistService.removeStock(id!, ticker),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['watchlist-stocks', id] });
            queryClient.invalidateQueries({ queryKey: ['watchlists'] }); // Update counts
        },
    });

    const TOP_50_STOCKS = [
        { ticker: 'AAPL', name: 'Apple Inc.' },
        { ticker: 'MSFT', name: 'Microsoft Corporation' },
        { ticker: 'GOOGL', name: 'Alphabet Inc.' },
        { ticker: 'AMZN', name: 'Amazon.com, Inc.' },
        { ticker: 'NVDA', name: 'NVIDIA Corporation' },
        { ticker: 'TSLA', name: 'Tesla, Inc.' },
        { ticker: 'META', name: 'Meta Platforms, Inc.' },
        { ticker: 'BRK.B', name: 'Berkshire Hathaway Inc.' },
        { ticker: 'V', name: 'Visa Inc.' },
        { ticker: 'JNJ', name: 'Johnson & Johnson' },
        { ticker: 'WMT', name: 'Walmart Inc.' },
        { ticker: 'JPM', name: 'JPMorgan Chase & Co.' },
        { ticker: 'MA', name: 'Mastercard Incorporated' },
        { ticker: 'PG', name: 'Procter & Gamble Company' },
        { ticker: 'UNH', name: 'UnitedHealth Group Incorporated' },
        { ticker: 'DIS', name: 'The Walt Disney Company' },
        { ticker: 'HD', name: 'The Home Depot, Inc.' },
        { ticker: 'BAC', name: 'Bank of America Corporation' },
        { ticker: 'XOM', name: 'Exxon Mobil Corporation' },
        { ticker: 'KO', name: 'The Coca-Cola Company' },
        { ticker: 'CSCO', name: 'Cisco Systems, Inc.' },
        { ticker: 'VZ', name: 'Verizon Communications Inc.' },
        { ticker: 'CVX', name: 'Chevron Corporation' },
        { ticker: 'PEP', name: 'PepsiCo, Inc.' },
        { ticker: 'ADBE', name: 'Adobe Inc.' },
        { ticker: 'CRM', name: 'Salesforce, Inc.' },
        { ticker: 'NFLX', name: 'Netflix, Inc.' },
        { ticker: 'CMCSA', name: 'Comcast Corporation' },
        { ticker: 'AMD', name: 'Advanced Micro Devices, Inc.' },
        { ticker: 'PFE', name: 'Pfizer Inc.' },
        { ticker: 'ORCL', name: 'Oracle Corporation' },
        { ticker: 'NKE', name: 'NIKE, Inc.' },
        { ticker: 'INTC', name: 'Intel Corporation' },
        { ticker: 'T', name: 'AT&T Inc.' },
        { ticker: 'WFC', name: 'Wells Fargo & Company' },
        { ticker: 'ABT', name: 'Abbott Laboratories' },
        { ticker: 'MRK', name: 'Merck & Co., Inc.' },
        { ticker: 'TMO', name: 'Thermo Fisher Scientific Inc.' },
        { ticker: 'AVGO', name: 'Broadcom Inc.' },
        { ticker: 'DHR', name: 'Danaher Corporation' },
        { ticker: 'MCD', name: 'McDonald\'s Corporation' },
        { ticker: 'ABBV', name: 'AbbVie Inc.' },
        { ticker: 'ACN', name: 'Accenture plc' },
        { ticker: 'LIN', name: 'Linde plc' },
        { ticker: 'TXN', name: 'Texas Instruments Incorporated' },
        { ticker: 'NEE', name: 'NextEra Energy, Inc.' },
        { ticker: 'PM', name: 'Philip Morris International Inc.' },
        { ticker: 'MS', name: 'Morgan Stanley' },
        { ticker: 'HON', name: 'Honeywell International Inc.' },
        { ticker: 'UPS', name: 'United Parcel Service, Inc.' }
    ];

    const handleAddStock = (e: React.FormEvent) => {
        e.preventDefault();
        if (newTicker) {
            addStockMutation.mutate(newTicker);
        }
    };

    if (isLoadingWatchlist || isLoadingStocks) {
        return <div className="text-white">Loading details...</div>;
    }

    if (!watchlist) {
        return <div className="text-red-400">Watchlist not found</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center space-x-4">
                <Link to="/watchlists" className="text-gray-400 hover:text-white transition-colors">
                    <ArrowLeft size={24} />
                </Link>
                <div>
                    <h1 className="text-3xl font-bold text-white">{watchlist.name}</h1>
                    <p className="text-gray-400 mt-1">
                        {stocks?.length || 0} stocks tracked
                    </p>
                </div>
            </div>

            {/* Add Stock Form */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Add Stock</h2>
                <form onSubmit={handleAddStock} className="flex gap-4">
                    <div className="flex-1">
                        <select
                            value={newTicker}
                            onChange={(e) => setNewTicker(e.target.value)}
                            className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        >
                            <option value="">Select a stock...</option>
                            {TOP_50_STOCKS.map((stock) => (
                                <option key={stock.ticker} value={stock.ticker}>
                                    {stock.ticker} - {stock.name}
                                </option>
                            ))}
                        </select>
                        {addError && <p className="text-red-400 text-sm mt-2">{addError}</p>}
                    </div>
                    <button
                        type="submit"
                        disabled={!newTicker || addStockMutation.isPending}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                    >
                        {addStockMutation.isPending ? 'Adding...' : (
                            <>
                                <Plus size={20} className="mr-2" />
                                Add Stock
                            </>
                        )}
                    </button>
                </form>
            </div>

            {/* Stocks List */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl overflow-hidden">
                <div className="p-6 border-b border-gray-800">
                    <h2 className="text-lg font-semibold text-white">Tracked Stocks</h2>
                </div>

                {stocks?.length === 0 ? (
                    <div className="p-8 text-center text-gray-500">
                        No stocks in this watchlist yet. Add one above!
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead className="bg-gray-950 text-gray-400 uppercase text-xs">
                                <tr>
                                    <th className="px-6 py-4 font-medium">Ticker</th>
                                    <th className="px-6 py-4 font-medium">Name</th>
                                    <th className="px-6 py-4 font-medium">Price</th>
                                    <th className="px-6 py-4 font-medium">Change</th>
                                    <th className="px-6 py-4 font-medium text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-800">
                                {stocks?.map((stock) => (
                                    <tr key={stock.ticker} className="hover:bg-gray-800/50 transition-colors">
                                        <td className="px-6 py-4">
                                            <span className="font-bold text-white">{stock.ticker}</span>
                                        </td>
                                        <td className="px-6 py-4 text-gray-300">{stock.name}</td>
                                        <td className="px-6 py-4 text-white font-mono">
                                            {stock.current_price ? `$${stock.current_price.toFixed(2)}` : '-'}
                                        </td>
                                        <td className="px-6 py-4">
                                            {stock.change_percent !== undefined && stock.change_percent !== null ? (
                                                <span className={`flex items-center ${stock.change_percent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                                    {stock.change_percent >= 0 ? <TrendingUp size={16} className="mr-1" /> : <TrendingDown size={16} className="mr-1" />}
                                                    {Math.abs(stock.change_percent).toFixed(2)}%
                                                </span>
                                            ) : (
                                                <span className="text-gray-500">-</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    e.stopPropagation();
                                                    if (window.confirm(`Remove ${stock.ticker} from watchlist?`)) {
                                                        removeStockMutation.mutate(stock.ticker);
                                                    }
                                                }}
                                                className="text-gray-500 hover:text-red-400 transition-colors p-2 rounded-lg hover:bg-red-500/10"
                                                title="Remove stock"
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default WatchlistDetailsPage;
