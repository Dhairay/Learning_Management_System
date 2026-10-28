import { apiRequest } from './httpClient';
import type { Enrollment } from '../types';

export const enrollmentApi = {
  enrollCourse: (courseId: string) =>
    apiRequest<{
      enrollment_id?: string;
      course_id: string;
      access_status: 'GRANTED' | 'PURCHASE_REQUIRED';
      checkout_required?: boolean;
      price?: { amount_minor: number; currency: string; formatted: string };
      message: string;
    }>(`/courses/${courseId}/enroll/`, {
      method: 'POST',
    }),

  createCheckoutSession: (courseId: string) =>
    apiRequest<{
      order_id: string;
      payment_id: string;
      total_minor: number;
      currency: string;
      course_title: string;
    }>('/checkout-sessions/', {
      method: 'POST',
      body: JSON.stringify({ course_id: courseId }),
    }),

  processPayment: (orderId: string) =>
    apiRequest<{
      detail: string;
      order_id: string;
      status: string;
      enrollments: string[];
    }>('/payments/process/', {
      method: 'POST',
      body: JSON.stringify({ order_id: orderId }),
    }),

  getMyEnrollments: () =>
    apiRequest<Enrollment[]>('/me/enrollments/'),

  getCurriculum: (enrollmentId: string) =>
    apiRequest<{
      enrollment_id: string;
      course_id: string;
      course_title: string;
      progress_percentage: number;
      curriculum: Array<{
        id: string;
        title: string;
        position: number;
        lessons: Array<{
          id: string;
          title: string;
          lesson_type: 'VIDEO' | 'ARTICLE' | 'QUIZ' | 'ASSIGNMENT' | 'LIVE_SESSION';
          position: number;
          is_required: boolean;
          duration_seconds: number;
          is_completed: boolean;
        }>;
      }>;
    }>(`/enrollments/${enrollmentId}/curriculum/`),

  updateProgress: (data: { lesson_id: string; completed?: boolean; last_position_seconds?: number }) =>
    apiRequest<{
      lesson_id: string;
      completed: boolean;
      last_position_seconds: number;
      course_progress_percentage: number;
      is_course_completed: boolean;
      completion_status: string;
    }>('/learning/progress/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};
