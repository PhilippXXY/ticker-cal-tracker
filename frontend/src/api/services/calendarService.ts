import api from '../axios';

export interface CalendarTokenResponse {
    calendar_url: string;
    token: string;
}

export const calendarService = {
    getCalendarUrl: async (watchlistId: string): Promise<CalendarTokenResponse> => {
        const response = await api.get<CalendarTokenResponse>(`/api/cal/${watchlistId}`);
        return response.data;
    },

    rotateCalendarToken: async (watchlistId: string): Promise<CalendarTokenResponse> => {
        const response = await api.post<CalendarTokenResponse>(`/api/cal/${watchlistId}`);
        return response.data;
    }
};
