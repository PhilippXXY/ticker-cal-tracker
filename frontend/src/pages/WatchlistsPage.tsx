import React, { useState } from 'react';
import { Plus, Search } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { watchlistService } from '../api/services/watchlistService';
import type { Watchlist, CreateWatchlistData } from '../api/services/watchlistService';
import WatchlistCard from '../components/dashboard/WatchlistCard';
import CreateWatchlistModal from '../components/watchlist/CreateWatchlistModal';

const WatchlistsPage = () => {
    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const queryClient = useQueryClient();

    // Fetch watchlists
    const { data: watchlists, isLoading, error } = useQuery({
        queryKey: ['watchlists'],
        queryFn: watchlistService.getAll,
    });

    // Create mutation
    const createMutation = useMutation({
        mutationFn: watchlistService.create,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['watchlists'] });
        },
    });

    // Delete mutation
    const deleteMutation = useMutation({
        mutationFn: watchlistService.delete,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['watchlists'] });
        },
    });

    const handleCreate = async (data: CreateWatchlistData) => {
        await createMutation.mutateAsync(data);
    };

    const handleDelete = async (id: string) => {
        if (window.confirm('Are you sure you want to delete this watchlist?')) {
            await deleteMutation.mutateAsync(id);
        }
    };

    const handleEdit = (watchlist: Watchlist) => {
        // TODO: Implement edit functionality
        console.log('Edit watchlist:', watchlist);
    };

    const filteredWatchlists = watchlists?.filter(w =>
        w.name.toLowerCase().includes(searchQuery.toLowerCase())
    );

    if (isLoading) {
        return <div className="text-white">Loading watchlists...</div>;
    }

    if (error) {
        return <div className="text-red-400">Error loading watchlists</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white">My Watchlists</h1>
                    <p className="text-gray-400 mt-1">Manage your stock collections</p>
                </div>
                <button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors"
                >
                    <Plus size={20} />
                    <span>New Watchlist</span>
                </button>
            </div>

            {/* Search Bar */}
            <div className="relative max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
                <input
                    type="text"
                    placeholder="Search watchlists..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-gray-900 border border-gray-800 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                />
            </div>

            {/* Watchlists Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredWatchlists?.map((watchlist) => (
                    <WatchlistCard
                        key={watchlist.id}
                        watchlist={watchlist}
                        onDelete={handleDelete}
                        onEdit={handleEdit}
                    />
                ))}
            </div>

            {filteredWatchlists?.length === 0 && (
                <div className="text-center py-12 text-gray-500">
                    No watchlists found. Create one to get started!
                </div>
            )}

            <CreateWatchlistModal
                isOpen={isCreateModalOpen}
                onClose={() => setIsCreateModalOpen(false)}
                onSubmit={handleCreate}
            />
        </div>
    );
};

export default WatchlistsPage;
