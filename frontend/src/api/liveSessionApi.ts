import { apiRequest } from './httpClient';
import type { LiveSession } from '../types';

export const liveSessionApi = {
  getSessions: (courseId: string) =>
    apiRequest<LiveSession[]>(`/courses/${courseId}/live-sessions/`),

  createSession: (courseId: string, data: Partial<LiveSession>) =>
    apiRequest<LiveSession>(`/courses/${courseId}/live-sessions/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  registerSession: (sessionId: string) =>
    apiRequest(`/live-sessions/${sessionId}/register/`, {
      method: 'POST',
    }),

  joinSession: (sessionId: string) =>
    apiRequest<{
      session_id: string;
      title: string;
      room_url: string;
      provider: string;
      is_instructor: boolean;
    }>(`/live-sessions/${sessionId}/join/`, {
      method: 'POST',
    }),
};
