import api from '../axios';

export interface UserProfile {
    id: number;
    username: string;
    email: string;
    created_at: string;
}

export interface UpdateUserProfile {
    email?: string;
    password?: string;
}

export const userService = {
    getProfile: async (): Promise<UserProfile> => {
        const response = await api.get<UserProfile>('/api/user/profile');
        return response.data;
    },

    updateProfile: async (data: UpdateUserProfile): Promise<UserProfile> => {
        const response = await api.put<UserProfile>('/api/user/profile', data);
        return response.data;
    }
};
