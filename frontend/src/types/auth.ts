export interface User {
    id: number;
    username: string;
    email?: string;
    created_at?: string;
}

export interface LoginResponse {
    access_token: string;
    user?: User;
}

export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}
