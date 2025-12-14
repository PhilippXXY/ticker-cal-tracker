import { useState, useEffect } from 'react';
import { Mail, Save, AlertCircle, CheckCircle, Lock } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService } from '../api/services/userService';

const SettingsPage = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' } | null>(null);

    const { data: user, isLoading, error } = useQuery({
        queryKey: ['userProfile'],
        queryFn: userService.getProfile,
    });

    // Populate email field when user data is loaded
    useEffect(() => {
        if (user?.email) {
            setEmail(user.email);
        }
    }, [user]);

    const queryClient = useQueryClient();

    const updateProfileMutation = useMutation({
        mutationFn: userService.updateProfile,
        onSuccess: (updatedUser) => {
            queryClient.setQueryData(['userProfile'], updatedUser);
            setMessage({ text: 'Profile updated successfully!', type: 'success' });
            setPassword('');
            setConfirmPassword('');
            setTimeout(() => setMessage(null), 3000);
        },
        onError: (err: any) => {
            const errorMsg = err.response?.data?.message || 'Failed to update profile';
            setMessage({ text: errorMsg, type: 'error' });
        }
    });

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setMessage(null);

        const updateData: any = {};

        if (email && email !== user?.email) {
            updateData.email = email;
        }

        if (password) {
            if (password !== confirmPassword) {
                setMessage({ text: 'Passwords do not match', type: 'error' });
                return;
            }
            if (password.length < 6) {
                setMessage({ text: 'Password must be at least 6 characters', type: 'error' });
                return;
            }
            updateData.password = password;
        }

        if (Object.keys(updateData).length === 0) {
            setMessage({ text: 'No changes to save', type: 'error' });
            return;
        }

        updateProfileMutation.mutate(updateData);
    };

    if (isLoading) return <div className="text-white p-8">Loading settings...</div>;
    if (error) return <div className="text-red-400 p-8">Error loading profile</div>;

    return (
        <div className="space-y-6 max-w-2xl">
            <div>
                <h1 className="text-3xl font-bold text-white">Settings</h1>
                <p className="text-gray-400 mt-1">Manage your account preferences</p>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 space-y-6">
                <div className="flex items-center space-x-4 pb-6 border-b border-gray-800">
                    <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center text-2xl font-bold text-white">
                        {user?.username?.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h2 className="text-xl font-semibold text-white">{user?.username}</h2>
                        <p className="text-gray-400 text-sm">Member since {new Date(user?.created_at || Date.now()).toLocaleDateString()}</p>
                    </div>
                </div>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-1">
                            Email Address
                        </label>
                        <div className="relative">
                            <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={18} />
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="w-full bg-black/50 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                            />
                        </div>
                    </div>

                    <div className="pt-4 border-t border-gray-800">
                        <label className="block text-sm font-medium text-gray-400 mb-3">
                            Change Password
                        </label>
                        <div className="space-y-4">
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={18} />
                                <input
                                    type="password"
                                    placeholder="New Password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    className="w-full bg-black/50 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 placeholder-gray-600"
                                />
                            </div>
                            <div className="relative">
                                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500" size={18} />
                                <input
                                    type="password"
                                    placeholder="Confirm New Password"
                                    value={confirmPassword}
                                    onChange={(e) => setConfirmPassword(e.target.value)}
                                    className="w-full bg-black/50 border border-gray-700 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 placeholder-gray-600"
                                />
                            </div>
                        </div>
                    </div>

                    {message && (
                        <div className={`flex items-center space-x-2 text-sm p-3 rounded-lg ${message.type === 'success' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                            {message.type === 'success' ? <CheckCircle size={16} /> : <AlertCircle size={16} />}
                            <span>{message.text}</span>
                        </div>
                    )}

                    <div className="pt-2">
                        <button
                            type="submit"
                            disabled={updateProfileMutation.isPending}
                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center space-x-2 transition-colors disabled:opacity-50"
                        >
                            {updateProfileMutation.isPending ? (
                                <span className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                            ) : (
                                <Save size={18} />
                            )}
                            <span>Save Changes</span>
                        </button>
                    </div>
                </form>
            </div>

            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Application Info</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <span className="text-gray-500 block">Version</span>
                        <span className="text-white">0.1.0-beta</span>
                    </div>
                    <div>
                        <span className="text-gray-500 block">Environment</span>
                        <span className="text-white">Development</span>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SettingsPage;
