import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api/axios';

const RegisterPage: React.FC = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleRegister = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await api.post('/api/auth/register', { username, email, password });
            navigate('/login');
        } catch (err: any) {
            setError(err.response?.data?.message || 'Registration failed. Try again.');
        }
    };

    return (
        <div className="flex items-center justify-center min-h-screen bg-slate-900">
            <form onSubmit={handleRegister} className="p-8 bg-slate-800 rounded shadow-md w-96">
                <h2 className="text-2xl font-bold mb-6 text-white text-center">Register</h2>
                {error && <p className="text-red-500 mb-4 text-sm text-center">{error}</p>}

                <div className="mb-4">
                    <label className="block text-gray-400 mb-2">Username</label>
                    <input
                        type="text"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        className="w-full p-2 rounded bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                        required
                    />
                </div>

                <div className="mb-4">
                    <label className="block text-gray-400 mb-2">Email (Optional)</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="w-full p-2 rounded bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                </div>

                <div className="mb-6">
                    <label className="block text-gray-400 mb-2">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full p-2 rounded bg-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-green-500"
                        required
                    />
                </div>

                <button type="submit" className="w-full bg-green-600 p-2 rounded text-white hover:bg-green-500 transition font-medium">
                    Create Account
                </button>

                <p className="mt-4 text-center text-gray-400 text-sm">
                    Already have an account? <Link to="/login" className="text-blue-400 hover:text-blue-300">Login</Link>
                </p>
            </form>
        </div>
    );
};

export default RegisterPage;
