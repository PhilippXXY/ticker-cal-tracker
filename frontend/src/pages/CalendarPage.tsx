import React, { useState } from 'react';
import { Calendar as CalendarIcon, Copy, RefreshCw, ExternalLink } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { watchlistService } from '../api/services/watchlistService';
import { calendarService } from '../api/services/calendarService';

const CalendarPage = () => {
    const { data: watchlists, isLoading } = useQuery({
        queryKey: ['watchlists'],
        queryFn: watchlistService.getAll,
    });

    const [calendarUrls, setCalendarUrls] = useState<Record<number, string>>({});
    const [loadingIds, setLoadingIds] = useState<number[]>([]);

    const handleGetUrl = async (watchlistId: number) => {
        if (calendarUrls[watchlistId]) return;

        setLoadingIds(prev => [...prev, watchlistId]);
        try {
            const data = await calendarService.getCalendarUrl(watchlistId);
            setCalendarUrls(prev => ({ ...prev, [watchlistId]: data.calendar_url }));
        } catch (error) {
            console.error('Failed to get calendar URL', error);
            alert('Failed to get calendar URL');
        } finally {
            setLoadingIds(prev => prev.filter(id => id !== watchlistId));
        }
    };

    const handleCopy = (url: string) => {
        navigator.clipboard.writeText(url);
        alert('Calendar URL copied to clipboard!');
    };

    if (isLoading) {
        return <div className="text-white">Loading...</div>;
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white">Calendar Integration</h1>
                <p className="text-gray-400 mt-1">Subscribe to your stock events in your favorite calendar app</p>
            </div>

            <div className="grid grid-cols-1 gap-6">
                {watchlists?.map((watchlist) => (
                    <div key={watchlist.id} className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center space-x-3">
                                <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
                                    <CalendarIcon size={24} />
                                </div>
                                <div>
                                    <h3 className="text-lg font-semibold text-white">{watchlist.name}</h3>
                                    <p className="text-sm text-gray-400">Syncs earnings, dividends, and splits</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-gray-950 rounded-lg p-4 border border-gray-800">
                            {calendarUrls[watchlist.id] ? (
                                <div className="flex items-center space-x-3">
                                    <input
                                        type="text"
                                        readOnly
                                        value={calendarUrls[watchlist.id]}
                                        className="flex-1 bg-transparent text-gray-300 text-sm focus:outline-none"
                                    />
                                    <button
                                        onClick={() => handleCopy(calendarUrls[watchlist.id])}
                                        className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                                        title="Copy URL"
                                    >
                                        <Copy size={18} />
                                    </button>
                                    <a
                                        href={calendarUrls[watchlist.id]}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="p-2 text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 rounded-lg transition-colors"
                                        title="Open"
                                    >
                                        <ExternalLink size={18} />
                                    </a>
                                </div>
                            ) : (
                                <div className="flex justify-center">
                                    <button
                                        onClick={() => handleGetUrl(watchlist.id)}
                                        disabled={loadingIds.includes(watchlist.id)}
                                        className="text-blue-400 hover:text-blue-300 text-sm font-medium flex items-center space-x-2"
                                    >
                                        {loadingIds.includes(watchlist.id) ? (
                                            <>
                                                <RefreshCw size={16} className="animate-spin" />
                                                <span>Generating Link...</span>
                                            </>
                                        ) : (
                                            <>
                                                <CalendarIcon size={16} />
                                                <span>Get Calendar Link</span>
                                            </>
                                        )}
                                    </button>
                                </div>
                            )}
                        </div>

                        <div className="mt-4 text-xs text-gray-500">
                            <p>Instructions:</p>
                            <ul className="list-disc list-inside mt-1 space-y-1">
                                <li>Google Calendar: Add calendar &gt; From URL</li>
                                <li>Apple Calendar: File &gt; New Calendar Subscription</li>
                                <li>Outlook: Add Calendar &gt; Subscribe from web</li>
                            </ul>
                        </div>
                    </div>
                ))}

                {watchlists?.length === 0 && (
                    <div className="text-center py-12 text-gray-500">
                        No watchlists found. Create one first to get a calendar link.
                    </div>
                )}
            </div>
        </div>
    );
};

export default CalendarPage;
