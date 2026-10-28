import { apiRequest } from './httpClient';
import type { Course, Category } from '../types';

export const courseApi = {
  getCategories: () =>
    apiRequest<Category[]>('/courses/categories/'),

  getCourses: (params?: { category?: string; search?: string }) => {
    const q = new URLSearchParams();
    if (params?.category) q.append('category', params.category);
    if (params?.search) q.append('search', params.search);
    const queryString = q.toString() ? `?${q.toString()}` : '';
    return apiRequest<{ results: Course[] } | Course[]>(`/courses/${queryString}`).then(res => 
      Array.isArray(res) ? res : res.results || []
    );
  },

  getCourse: (courseId: string) =>
    apiRequest<Course>(`/courses/${courseId}/`),

  createCourse: (data: Partial<Course> & { price_amount?: number; price_currency?: string }) =>
    apiRequest<Course>('/courses/', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  updateCourse: (courseId: string, data: Partial<Course>) =>
    apiRequest<Course>(`/courses/${courseId}/`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  publishCourse: (courseId: string) =>
    apiRequest<{ detail: string; status: string }>(`/courses/${courseId}/publish/`, {
      method: 'POST',
    }),

  createSection: (courseId: string, data: { title: string }) =>
    apiRequest(`/courses/${courseId}/sections/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  createLesson: (sectionId: string, data: { title: string; lesson_type: string; content_text?: string; duration_seconds?: number }) =>
    apiRequest(`/courses/sections/${sectionId}/lessons/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getLessonPlayback: (lessonId: string) =>
    apiRequest<{
      lesson_id: string;
      title: string;
      lesson_type: string;
      playback_url: string;
      content_text: string;
      duration_seconds: number;
    }>(`/courses/lessons/${lessonId}/playback/`),
};
