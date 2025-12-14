import { Trash2 } from 'lucide-react';

interface StockCardProps {
    ticker: string;
    name: string;
    price?: number;
    change?: number;
    percentChange?: number;
    onRemove: () => void;
}

const StockCard: React.FC<StockCardProps> = ({
    ticker,
    name,
    price,
    change,
    percentChange,
    onRemove
}) => {
    const isUp = (change || 0) >= 0;
    const textColor = isUp ? 'text-green-400' : 'text-red-400';

    return (
        <div className="p-6 bg-slate-800 rounded shadow relative group transition hover:bg-slate-750 border border-slate-700">
            <div className="flex justify-between items-start mb-2 gap-4">
                <div className="flex-1 min-w-0 pr-2">
                    <h2 className="text-2xl font-bold truncate">{ticker}</h2>
                    <p className="text-gray-400 text-sm truncate">{name}</p>
                </div>

                {price !== undefined ? (
                    <div className={`text-right flex-shrink-0 ${price === 0 ? 'text-gray-400' : textColor}`}>
                        <div className="text-xl font-mono whitespace-nowrap">
                            {price === 0 ? 'N/A' : `$${price.toFixed(2)}`}
                        </div>
                        <div className="text-sm whitespace-nowrap">
                            {price === 0 ? 'Update Failed' : (
                                <>
                                    {isUp ? '+' : ''}{change?.toFixed(2)} ({percentChange?.toFixed(2)}%)
                                </>
                            )}
                        </div>
                    </div>
                ) : (
                    <div className="text-gray-500 text-sm animate-pulse flex-shrink-0">Loading...</div>
                )}
            </div>

            <button
                onClick={(e) => {
                    e.preventDefault();
                    onRemove();
                }}
                className="absolute top-1 right-1 z-10 text-gray-500 hover:text-red-500 transition-colors p-1.5 rounded-full hover:bg-red-500/10"
                aria-label="Remove stock"
                title="Remove stock from watchlist"
            >
                <Trash2 size={16} />
            </button>
        </div>
    );
};

export default StockCard;
