import { apiRequest } from './httpClient';
import type { Quiz, QuizAttempt, Assignment, AssignmentSubmission } from '../types';

export const assessmentApi = {
  getQuiz: (quizId: string) =>
    apiRequest<{
      quiz: Quiz;
      past_attempts: QuizAttempt[];
      can_attempt: boolean;
    }>(`/quizzes/${quizId}/`),

  startQuizAttempt: (quizId: string) =>
    apiRequest<QuizAttempt>(`/quizzes/${quizId}/attempts/`, {
      method: 'POST',
    }),

  submitQuiz: (attemptId: string, answers: Record<string, string[]>) =>
    apiRequest<{
      attempt_id: string;
      score: number;
      passed: boolean;
      pass_percentage: number;
      message: string;
    }>(`/quiz-attempts/${attemptId}/submit/`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    }),

  getAssignment: (assignmentId: string) =>
    apiRequest<{
      assignment: Assignment;
      submission?: AssignmentSubmission;
    }>(`/assignments/${assignmentId}/`),

  submitAssignment: (assignmentId: string, data: { content_text?: string; file_url?: string }) =>
    apiRequest<AssignmentSubmission>(`/assignments/${assignmentId}/submit/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  gradeAssignment: (submissionId: string, data: { score: number; feedback: string }) =>
    apiRequest(`/submissions/${submissionId}/grade/`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  getCourseAssignments: (courseId: string) =>
    apiRequest<Assignment[]>(`/courses/${courseId}/assignments/`),

  getInstructorSubmissions: (courseId: string) =>
    apiRequest<AssignmentSubmission[]>(`/courses/${courseId}/submissions/`),
};
