import React from 'react';
import { BarChart2, Calendar, TrendingUp } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { watchlistService } from '../api/services/watchlistService';

const DashboardHome = () => {
    const { data: watchlists } = useQuery({
        queryKey: ['watchlists'],
        queryFn: watchlistService.getAll,
    });

    const watchlistCount = watchlists?.length || 0;
    const totalStocks = watchlists?.reduce((sum, watchlist) => sum + (watchlist.stock_count || 0), 0) || 0;

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white">Welcome back, User!</h1>
                <p className="text-gray-400 mt-1">Here's what's happening with your tracked stocks today.</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
                            <BarChart2 size={24} />
                        </div>
                    </div>
                    <h3 className="text-gray-400 text-sm font-medium">Total Watchlists</h3>
                    <p className="text-3xl font-bold text-white">{watchlistCount}</p>
                </div>

                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-purple-500/10 text-purple-400 rounded-lg">
                            <TrendingUp size={24} />
                        </div>
                    </div>
                    <h3 className="text-gray-400 text-sm font-medium">Tracked Stocks</h3>
                    <p className="text-3xl font-bold text-white">{totalStocks}</p>
                </div>

                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <div className="p-2 bg-orange-500/10 text-orange-400 rounded-lg">
                            <Calendar size={24} />
                        </div>
                        <span className="text-gray-500 text-sm">Next 7 Days</span>
                    </div>
                    <h3 className="text-gray-400 text-sm font-medium">Upcoming Events</h3>
                    <p className="text-3xl font-bold text-white">0</p>
                </div>
            </div>

            {/* Recent Activity / Empty State */}
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-white mb-4">Recent Activity</h2>
                {watchlistCount === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                        <p>No activity yet. Create a watchlist to get started!</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {/* Placeholder for recent activity */}
                        <div className="flex items-center justify-between p-4 bg-gray-950 rounded-lg border border-gray-800">
                            <div className="flex items-center space-x-3">
                                <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                                <span className="text-gray-300">You have {watchlistCount} active watchlists.</span>
                            </div>
                            <span className="text-xs text-gray-500">Just now</span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default DashboardHome;
