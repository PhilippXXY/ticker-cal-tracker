import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/axios';

const LoginPage: React.FC = () => {
    // State for form inputs and status
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const navigate = useNavigate();

    const handleLogin = async (event: React.FormEvent) => {
        event.preventDefault();
        setError(''); // Clear previous errors
        setIsLoading(true);

        try {
            // Attempt login
            const response = await api.post('/api/auth/login', { username, password });

            // Success: Save token and redirect
            localStorage.setItem('token', response.data.access_token);
            window.location.href = '/watchlists'; // Force refresh to update auth state
        } catch (err: any) {
            console.error('Login error:', err);
            // Extract meaningful error message
            const errorMessage = err.response?.data?.message || err.message || 'Login failed. Please check your connection.';
            setError(errorMessage);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-slate-900">
            <form onSubmit={handleLogin} className="p-8 bg-slate-800 rounded-lg shadow-xl w-96 border border-slate-700">
                <h2 className="text-3xl font-bold mb-8 text-white text-center tracking-tight">Welcome Back</h2>

                {error && (
                    <div className="bg-red-500/10 border border-red-500/50 rounded p-3 mb-6">
                        <p className="text-red-400 text-sm text-center font-medium">{error}</p>
                    </div>
                )}

                <div className="mb-5">
                    <label className="block text-gray-400 mb-2 text-sm font-medium">Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full p-3 rounded bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-blue-500 transition-colors"
                        placeholder="Enter your username"
                        required
                    />
                </div>

                <div className="mb-8">
                    <label className="block text-gray-400 mb-2 text-sm font-medium">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full p-3 rounded bg-slate-900 border border-slate-700 text-white focus:outline-none focus:border-blue-500 transition-colors"
                        placeholder="Enter your password"
                        required
                    />
                </div>

                <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-blue-600 p-3 rounded text-white font-semibold hover:bg-blue-500 focus:ring-4 focus:ring-blue-500/30 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {isLoading ? 'Signing In...' : 'Sign In'}
                </button>

                <p className="mt-6 text-center text-gray-500 text-sm">
                    Don't have an account?{' '}
                    <Link to="/register" className="text-blue-400 hover:text-blue-300 font-medium hover:underline">
                        Create one
                    </Link>
                </p>
            </form>
        </div>
    );
};

export default LoginPage;
