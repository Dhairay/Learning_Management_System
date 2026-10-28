export type Role = 'PLATFORM_ADMIN' | 'ORG_ADMIN' | 'INSTRUCTOR' | 'STUDENT';

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  avatar_url?: string;
  bio?: string;
  headline?: string;
  is_staff?: boolean;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  logo_url?: string;
  website?: string;
  status: 'ACTIVE' | 'SUSPENDED' | 'INACTIVE';
  settings?: Record<string, any>;
}

export interface OrganizationMembership {
  id: string;
  organization: Organization;
  user?: User;
  role: Role;
  status: 'ACTIVE' | 'PENDING_INVITE' | 'REVOKED';
  joined_at: string;
}

export interface Category {
  id: string;
  name: string;
  slug: string;
  icon?: string;
}

export interface CoursePrice {
  id: string;
  currency: string;
  amount_minor: number;
  formatted_price: string;
}

export interface LessonSummary {
  id: string;
  title: string;
  lesson_type: 'VIDEO' | 'ARTICLE' | 'QUIZ' | 'ASSIGNMENT' | 'LIVE_SESSION';
  position: number;
  is_required: boolean;
  duration_seconds: number;
  is_completed?: boolean;
}

export interface CourseSection {
  id: string;
  title: string;
  position: number;
  lessons: LessonSummary[];
}

export interface Course {
  id: string;
  title: string;
  slug: string;
  short_description?: string;
  description?: string;
  thumbnail_url?: string;
  level: 'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED' | 'ALL_LEVELS';
  status: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED' | 'SUSPENDED';
  visibility: 'PUBLIC' | 'ORGANIZATION_ONLY' | 'PRIVATE';
  is_free: boolean;
  price?: CoursePrice;
  price_display: string;
  category?: Category;
  organization_name: string;
  organization_slug: string;
  instructor_name: string;
  total_lessons: number;
  total_duration_seconds: number;
  sections?: CourseSection[];
}

export interface Enrollment {
  id: string;
  course: Course;
  student_name: string;
  student_email: string;
  status: 'ACTIVE' | 'COMPLETED' | 'SUSPENDED';
  progress_percentage: number;
  enrolled_at: string;
}

export interface QuizQuestionOption {
  id: string;
  text: string;
}

export interface QuizQuestion {
  id: string;
  text: string;
  question_type: 'SINGLE_CHOICE' | 'MULTIPLE_CHOICE';
  points: number;
  position: number;
  options: QuizQuestionOption[];
}

export interface Quiz {
  id: string;
  course: string;
  title: string;
  description?: string;
  pass_percentage: number;
  max_attempts: number;
  time_limit_minutes: number;
  total_questions: number;
  questions: QuizQuestion[];
}

export interface QuizAttempt {
  id: string;
  quiz: string;
  quiz_title: string;
  attempt_number: number;
  status: 'IN_PROGRESS' | 'SUBMITTED' | 'EVALUATED';
  score: number;
  passed: boolean;
  pass_percentage: number;
  started_at: string;
  submitted_at?: string;
}

export interface Assignment {
  id: string;
  course: string;
  course_title: string;
  title: string;
  instructions: string;
  max_score: number;
  passing_score: number;
  due_at?: string;
  is_required: boolean;
  created_at: string;
}

export interface AssignmentGrade {
  id: string;
  score: number;
  feedback: string;
  grader_name: string;
  graded_at: string;
}

export interface AssignmentSubmission {
  id: string;
  assignment: string;
  version: number;
  content_text: string;
  file_url?: string;
  status: 'SUBMITTED' | 'GRADED' | 'RESUBMISSION_REQUIRED';
  submitted_at: string;
  grade?: AssignmentGrade;
  student_name?: string;
}

export interface LiveSession {
  id: string;
  course: string;
  instructor_name: string;
  title: string;
  description?: string;
  provider: 'DAILY_CO' | 'ZOOM' | 'JITSI' | 'INTERNAL';
  provider_session_id: string;
  room_url: string;
  scheduled_start: string;
  scheduled_end: string;
  status: 'SCHEDULED' | 'LIVE' | 'COMPLETED' | 'CANCELLED';
  is_registered: boolean;
  registered_count: number;
}

export interface DiscussionReply {
  id: string;
  thread: string;
  author: string;
  author_name: string;
  author_avatar?: string;
  content: string;
  created_at: string;
}

export interface DiscussionThread {
  id: string;
  course: string;
  author: string;
  author_name: string;
  author_avatar?: string;
  title: string;
  content: string;
  replies_count: number;
  replies?: DiscussionReply[];
  created_at: string;
}

export interface CourseReview {
  id: string;
  course: string;
  student_name: string;
  student_avatar?: string;
  rating: number;
  review_text: string;
  created_at: string;
}

export interface Certificate {
  id: string;
  certificate_number: string;
  student_name: string;
  course_title: string;
  organization_name: string;
  policy_version: string;
  status: 'VALID' | 'REVOKED';
  download_url?: string;
  issued_at: string;
}

export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  notification_type: string;
  read: boolean;
  created_at: string;
}
