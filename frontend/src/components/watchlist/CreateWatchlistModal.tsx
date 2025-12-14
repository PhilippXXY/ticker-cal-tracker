import React, { useState } from 'react';
import { X } from 'lucide-react';
import type { CreateWatchlistData } from '../../api/services/watchlistService';

interface CreateWatchlistModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (data: CreateWatchlistData) => Promise<void>;
    initialName?: string;
    title?: string;
    submitLabel?: string;
}

const CreateWatchlistModal: React.FC<CreateWatchlistModalProps> = ({
    isOpen,
    onClose,
    onSubmit,
    initialName = '',
    title = 'Create New Watchlist',
    submitLabel = 'Create Watchlist'
}) => {
    const [name, setName] = useState(initialName);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    // Reset name when modal opens/closes or initialName changes
    React.useEffect(() => {
        if (isOpen) {
            setName(initialName);
        }
    }, [isOpen, initialName]);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!name.trim()) return;

        setIsLoading(true);
        setError('');

        try {
            await onSubmit({ name });
            setName('');
            onClose();
        } catch (err) {
            setError('Failed to save watchlist. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="bg-gray-900 border border-gray-800 rounded-xl w-full max-w-md p-6 relative">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-500 hover:text-white transition-colors"
                >
                    <X size={20} />
                </button>

                <h2 className="text-xl font-bold text-white mb-6">{title}</h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-1">
                            Watchlist Name
                        </label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                            placeholder="e.g., Tech Stocks"
                            className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                            autoFocus
                        />
                    </div>

                    {error && (
                        <div className="text-red-400 text-sm bg-red-500/10 p-3 rounded-lg">
                            {error}
                        </div>
                    )}

                    <div className="flex justify-end space-x-3 mt-6">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isLoading || !name.trim()}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                        >
                            {isLoading ? 'Saving...' : submitLabel}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateWatchlistModal;
