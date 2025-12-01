import axios from '../axios';



export interface CalendarTokenResponse {
    calendar_url: string;
    token: string;
}

export const calendarService = {
    getCalendarUrl: async (watchlistId: string): Promise<CalendarTokenResponse> => {
        const response = await axios.get(`/cal/${watchlistId}`);
        return response.data;
    },

    rotateToken: async (watchlistId: string): Promise<CalendarTokenResponse> => {
        const response = await axios.post(`/cal/${watchlistId}`);
        return response.data;
    },
};
