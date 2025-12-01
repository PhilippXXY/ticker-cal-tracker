import React from 'react';
import { User, Mail, Shield, Bell } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const SettingsPage = () => {
    const { user } = useAuth();
    const [isPasswordModalOpen, setIsPasswordModalOpen] = React.useState(false);
    const [passwordData, setPasswordData] = React.useState({ old_password: '', new_password: '', confirm_password: '' });
    const [passwordError, setPasswordError] = React.useState('');
    const [passwordSuccess, setPasswordSuccess] = React.useState('');
    const [notifications, setNotifications] = React.useState({ email: true, push: false });

    const handleChangePassword = async (e: React.FormEvent) => {
        e.preventDefault();
        setPasswordError('');
        setPasswordSuccess('');

        if (passwordData.new_password !== passwordData.confirm_password) {
            setPasswordError("New passwords don't match");
            return;
        }

        try {
            const token = localStorage.getItem('token');
            const response = await fetch('http://localhost:5001/api/auth/change-password', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    old_password: passwordData.old_password,
                    new_password: passwordData.new_password
                })
            });

            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'Failed to change password');
            }

            setPasswordSuccess('Password changed successfully');
            setPasswordData({ old_password: '', new_password: '', confirm_password: '' });
            setTimeout(() => setIsPasswordModalOpen(false), 2000);
        } catch (err: any) {
            setPasswordError(err.message);
        }
    };

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-3xl font-bold text-white">Settings</h1>
                <p className="text-gray-400 mt-1">Manage your account and preferences</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Profile Section */}
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                        <User size={20} className="text-blue-400" />
                        <span>Profile Information</span>
                    </h2>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-500 mb-1">Username</label>
                            <div className="flex items-center space-x-3 bg-gray-950 p-3 rounded-lg border border-gray-800">
                                <User size={18} className="text-gray-400" />
                                <span className="text-white">{user?.username || 'Loading...'}</span>
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-500 mb-1">Email Address</label>
                            <div className="flex items-center space-x-3 bg-gray-950 p-3 rounded-lg border border-gray-800">
                                <Mail size={18} className="text-gray-400" />
                                <span className="text-white">{user?.email || 'No email provided'}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Security Section */}
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                        <Shield size={20} className="text-green-400" />
                        <span>Security</span>
                    </h2>
                    <p className="text-gray-400 text-sm mb-4">
                        Update your password to keep your account secure.
                    </p>
                    <button
                        onClick={() => setIsPasswordModalOpen(true)}
                        className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg w-full transition-colors"
                    >
                        Change Password
                    </button>
                </div>

                {/* Notifications Section */}
                <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                    <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
                        <Bell size={20} className="text-yellow-400" />
                        <span>Notifications</span>
                    </h2>
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <span className="text-gray-300">Email Notifications</span>
                            <button
                                onClick={() => setNotifications(prev => ({ ...prev, email: !prev.email }))}
                                className={`w-12 h-6 rounded-full transition-colors relative ${notifications.email ? 'bg-blue-600' : 'bg-gray-700'}`}
                            >
                                <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${notifications.email ? 'translate-x-6' : ''}`} />
                            </button>
                        </div>
                        <div className="flex items-center justify-between">
                            <span className="text-gray-300">Push Notifications</span>
                            <button
                                onClick={() => setNotifications(prev => ({ ...prev, push: !prev.push }))}
                                className={`w-12 h-6 rounded-full transition-colors relative ${notifications.push ? 'bg-blue-600' : 'bg-gray-700'}`}
                            >
                                <span className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${notifications.push ? 'translate-x-6' : ''}`} />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            {/* Change Password Modal */}
            {isPasswordModalOpen && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                    <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 w-full max-w-md m-4">
                        <h2 className="text-xl font-bold text-white mb-4">Change Password</h2>
                        <form onSubmit={handleChangePassword} className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-1">Current Password</label>
                                <input
                                    type="password"
                                    value={passwordData.old_password}
                                    onChange={e => setPasswordData({ ...passwordData, old_password: e.target.value })}
                                    className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-1">New Password</label>
                                <input
                                    type="password"
                                    value={passwordData.new_password}
                                    onChange={e => setPasswordData({ ...passwordData, new_password: e.target.value })}
                                    className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-400 mb-1">Confirm New Password</label>
                                <input
                                    type="password"
                                    value={passwordData.confirm_password}
                                    onChange={e => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
                                    className="w-full bg-gray-950 border border-gray-800 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                                    required
                                />
                            </div>

                            {passwordError && <p className="text-red-400 text-sm">{passwordError}</p>}
                            {passwordSuccess && <p className="text-green-400 text-sm">{passwordSuccess}</p>}

                            <div className="flex justify-end space-x-3 mt-6">
                                <button
                                    type="button"
                                    onClick={() => setIsPasswordModalOpen(false)}
                                    className="px-4 py-2 text-gray-400 hover:text-white transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
                                >
                                    Update Password
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SettingsPage;
