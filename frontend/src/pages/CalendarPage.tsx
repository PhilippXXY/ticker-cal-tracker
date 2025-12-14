import { useState } from 'react';
import { Calendar as CalendarIcon, Copy, RefreshCw, Check } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { watchlistService } from '../api/services/watchlistService';
import { calendarService } from '../api/services/calendarService';

const CalendarPage = () => {
    const { data: watchlists, isLoading } = useQuery({
        queryKey: ['watchlists'],
        queryFn: watchlistService.getAll,
    });

    if (isLoading) {
        return <div className="text-white p-8">Loading calendars...</div>;
    }

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white">Calendar Subscriptions</h1>
                <p className="text-gray-400 mt-1">Subscribe to your watchlist events in your favorite calendar app (Google Calendar, Outlook, etc.)</p>
            </div>

            <div className="grid grid-cols-1 gap-6">
                {watchlists?.map((watchlist) => (
                    <CalendarSubscriptionCard key={watchlist.id} watchlist={watchlist} />
                ))}

                {watchlists?.length === 0 && (
                    <div className="text-center py-12 text-gray-500 bg-gray-900 rounded-xl border border-gray-800">
                        No watchlists found. Create a watchlist first to generate a calendar.
                    </div>
                )}
            </div>
        </div>
    );
};

const CalendarSubscriptionCard = ({ watchlist }: { watchlist: any }) => {
    const [copied, setCopied] = useState(false);

    const { data: calendarData, isLoading } = useQuery({
        queryKey: ['calendar', watchlist.id],
        queryFn: () => calendarService.getCalendarUrl(watchlist.id),
    });

    const queryClient = useQueryClient();

    const rotateMutation = useMutation({
        mutationFn: () => calendarService.rotateCalendarToken(watchlist.id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['calendar', watchlist.id] });
        },
    });

    const handleCopy = () => {
        if (calendarData?.calendar_url) {
            navigator.clipboard.writeText(calendarData.calendar_url);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    return (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
            <div className="flex items-start justify-between mb-4">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-blue-500/10 rounded-lg">
                        <CalendarIcon className="text-blue-400" size={24} />
                    </div>
                    <div>
                        <h3 className="text-lg font-semibold text-white">{watchlist.name}</h3>
                        <p className="text-sm text-gray-400">
                            {watchlist.stock_count || 0} stocks · Events: Earnings, Dividends, Splits
                        </p>
                    </div>
                </div>
            </div>

            <div className="bg-black/30 rounded-lg p-4 space-y-3">
                <label className="text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Subscription URL
                </label>

                <div className="flex space-x-2">
                    <input
                        type="text"
                        readOnly
                        value={isLoading ? 'Loading...' : calendarData?.calendar_url || ''}
                        className="flex-1 bg-black/50 border border-gray-700 rounded-lg px-4 py-2 text-gray-300 text-sm focus:outline-none focus:border-blue-500"
                    />

                    <button
                        onClick={handleCopy}
                        disabled={isLoading || !calendarData}
                        className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors disabled:opacity-50"
                    >
                        {copied ? <Check size={18} className="text-green-400" /> : <Copy size={18} />}
                        <span>{copied ? 'Copied' : 'Copy'}</span>
                    </button>

                    <button
                        onClick={() => {
                            if (window.confirm('Are you sure? This will invalidate the old URL.')) {
                                rotateMutation.mutate();
                            }
                        }}
                        disabled={rotateMutation.isPending || isLoading}
                        className="bg-gray-800 hover:bg-red-900/30 text-gray-400 hover:text-red-400 px-3 py-2 rounded-lg transition-colors"
                        title="Reset URL"
                    >
                        <RefreshCw size={18} className={rotateMutation.isPending ? 'animate-spin' : ''} />
                    </button>
                </div>

                <p className="text-xs text-gray-500">
                    Paste this URL into your calendar app to subscribe. Updates are automatic.
                </p>
            </div>
        </div>
    );
};

export default CalendarPage;
