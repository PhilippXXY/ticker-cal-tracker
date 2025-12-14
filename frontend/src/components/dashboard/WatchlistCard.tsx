import React from 'react';
import { Trash2, Edit2 } from 'lucide-react';
import type { Watchlist } from '../../api/services/watchlistService';
import { Link } from 'react-router-dom';

interface WatchlistCardProps {
    watchlist: Watchlist;
    onDelete: (id: string) => void;
    onEdit: (watchlist: Watchlist) => void;
}

const WatchlistCard: React.FC<WatchlistCardProps> = ({ watchlist, onDelete, onEdit }) => {
    return (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-blue-500/50 transition-colors group relative">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-lg font-semibold text-white mb-1">{watchlist.name}</h3>
                    <p className="text-gray-400 text-sm">Created {new Date(watchlist.created_at).toLocaleDateString()}</p>
                </div>

                {/* Removed unused menu button */}
            </div>

            <div className="flex items-center justify-between mt-6">
                <div className="flex items-center space-x-4 text-sm text-gray-400">
                    <span className="flex items-center space-x-1">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        <span>{watchlist.stock_count || 0} Stocks</span>
                    </span>
                </div>

                <div className="flex space-x-2 relative z-20">
                    <button
                        onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            onEdit(watchlist);
                        }}
                        className="p-2 text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors"
                        title="Edit"
                    >
                        <Edit2 size={18} />
                    </button>
                    <button
                        onClick={(e) => {
                            e.preventDefault();
                            e.stopPropagation();
                            onDelete(watchlist.id);
                        }}
                        className="p-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                        title="Delete"
                    >
                        <Trash2 size={18} />
                    </button>
                </div>
            </div>

            <Link to={`/watchlists/${watchlist.id}`} className="absolute inset-0" />
        </div>
    );
};

export default WatchlistCard;
