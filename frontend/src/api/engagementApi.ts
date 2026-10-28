import { apiRequest } from './httpClient';
import type { LiveSession, Certificate, DiscussionThread, CourseReview, NotificationItem } from '../types';

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

export const certificateApi = {
  issueCertificate: (enrollmentId: string) =>
    apiRequest<Certificate>(`/enrollments/${enrollmentId}/certificate/issue/`, {
      method: 'POST',
    }),

  getCertificate: (certificateId: string) =>
    apiRequest<Certificate>(`/certificates/${certificateId}/`),

  verifyCertificate: (certificateNumber: string) =>
    apiRequest<{
      valid: boolean;
      certificate?: Certificate;
      message?: string;
    }>(`/certificates/verify/${certificateNumber}/`),
};

export const engagementApi = {
  getDiscussions: (courseId: string) =>
    apiRequest<DiscussionThread[]>(`/courses/${courseId}/discussions/`),

  createDiscussion: (courseId: string, data: { title: string; content: string }) =>
    apiRequest<DiscussionThread>(`/courses/${courseId}/discussions/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  replyDiscussion: (threadId: string, data: { content: string; parent_reply_id?: string }) =>
    apiRequest(`/discussions/${threadId}/replies/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getReviews: (courseId: string) =>
    apiRequest<{
      course_id: string;
      average_rating: number;
      total_reviews: number;
      reviews: CourseReview[];
    }>(`/courses/${courseId}/reviews/`),

  submitReview: (courseId: string, data: { rating: number; review_text: string }) =>
    apiRequest<CourseReview>(`/courses/${courseId}/reviews/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getNotifications: () =>
    apiRequest<NotificationItem[]>('/notifications/'),

  markNotificationRead: (id: string) =>
    apiRequest(`/notifications/${id}/read/`, {
      method: 'PATCH',
    }),
};
