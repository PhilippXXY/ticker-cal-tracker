import React from 'react';
import { User as UserIcon, Bell } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const TopBar = () => {
    const { user } = useAuth();

    return (
        <header className="bg-gray-900 border-b border-gray-800 h-16 flex items-center justify-between px-8">
            <div className="flex items-center space-x-4">
                <h2 className="text-xl font-semibold text-white">
                    Welcome back, <span className="text-blue-400">{user?.username}</span>
                </h2>
            </div>

            <div className="flex items-center space-x-6">
                <button className="text-gray-400 hover:text-white transition-colors relative">
                    <Bell size={20} />
                    <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
                </button>

                <div className="flex items-center space-x-3 pl-6 border-l border-gray-800">
                    <div className="w-8 h-8 bg-gray-800 rounded-full flex items-center justify-center text-blue-400">
                        <UserIcon size={18} />
                    </div>
                    <div className="text-sm">
                        <p className="text-white font-medium">{user?.username}</p>
                        <p className="text-gray-500 text-xs">{user?.email || 'No email'}</p>
                    </div>
                </div>
            </div>
        </header>
    );
};

export default TopBar;
