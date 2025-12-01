export interface User {
    id: number;
    username: string;
    email?: string;
    created_at?: string;
}

export interface LoginResponse {
    access_token: string;
    user?: User; // Backend might not return user object on login yet, but good to have
}

export interface AuthState {
    user: User | null;
    token: string | null;
    isAuthenticated: boolean;
    isLoading: boolean;
}
