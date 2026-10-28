# API Specification — Learning Management System (LMS)

All API endpoints are versioned under `/api/v1/`. Responses return consistent JSON envelopes with status codes.

## 1. Authentication & Tenancy (`/auth/`, `/me/`, `/organizations/`)
- `POST /api/v1/auth/register/`: Register a new user account.
- `POST /api/v1/auth/login/`: Authenticate user and return JWT access and refresh tokens.
- `POST /api/v1/auth/token/refresh/`: Refresh expired JWT access token.
- `GET /api/v1/me/`: Current user profile and global details.
- `GET /api/v1/me/organizations/`: List user's active organization memberships with assigned roles.
- `POST /api/v1/organizations/`: Create a new organization tenant.
- `GET /api/v1/organizations/{org_slug}/members/`: List members belonging to the organization (OrgAdmin only).
- `POST /api/v1/organizations/{org_slug}/invitations/`: Invite a new member via email and assigned role.

## 2. Courses & Curriculum (`/courses/`, `/sections/`, `/lessons/`)
- `GET /api/v1/courses/`: Catalog listing for active organization with search, category filtering, and pagination.
- `POST /api/v1/courses/`: Author a new course (Instructor / Admin).
- `GET /api/v1/courses/{course_id}/`: Public/preview details of course (syllabus outline, instructor, pricing).
- `PATCH /api/v1/courses/{course_id}/`: Update course details.
- `POST /api/v1/courses/{course_id}/publish/`: Transition course from `DRAFT` to `PUBLISHED`.
- `POST /api/v1/courses/{course_id}/sections/`: Add a curriculum section.
- `POST /api/v1/sections/{section_id}/lessons/`: Add a lesson (Video, Article, Quiz, Assignment, Live Session).
- `GET /api/v1/lessons/{lesson_id}/playback/`: Get authorized video streaming playback payload for enrolled learner.

## 3. Enrollment & Commerce (`/courses/{id}/enroll/`, `/orders/`)
- `POST /api/v1/courses/{course_id}/enroll/`:
  - If course is free: Immediately provisions `Enrollment` and `Entitlement`, returns `access_status: GRANTED`.
  - If course is paid and user has no entitlement: Returns `access_status: PURCHASE_REQUIRED` and checkout session details.
- `POST /api/v1/checkout/`: Initialize an order for paid courses.
- `POST /api/v1/payments/process/`: Process or simulate payment completion, activating enrollment and entitlement.
- `GET /api/v1/me/enrollments/`: Retrieve learner's active course enrollments with overall progress percentage.
- `GET /api/v1/enrollments/{enrollment_id}/curriculum/`: Full authorized curriculum with lesson completion states.

## 4. Learning & Progress (`/learning/`)
- `POST /api/v1/learning/progress/`: Update video playback position or mark lesson as completed.
- `GET /api/v1/enrollments/{enrollment_id}/progress/`: Get detailed completion breakdown across all sections.

## 5. Assessments: Quizzes & Assignments (`/quizzes/`, `/assignments/`)
- `GET /api/v1/quizzes/{quiz_id}/`: Quiz details, questions (excluding answer keys), time limit.
- `POST /api/v1/quizzes/{quiz_id}/attempts/`: Start a timed quiz attempt.
- `POST /api/v1/quiz-attempts/{attempt_id}/submit/`: Submit answers for grading; returns evaluated score and pass/fail.
- `GET /api/v1/assignments/{assignment_id}/`: Assignment instructions, due date, rubrics, and existing submission.
- `POST /api/v1/assignments/{assignment_id}/submit/`: Submit text/file response.
- `POST /api/v1/assignments/submissions/{submission_id}/grade/`: Instructor evaluation with score and feedback.

## 6. Live Sessions (`/live-sessions/`)
- `GET /api/v1/courses/{course_id}/live-sessions/`: List scheduled and past live classes.
- `POST /api/v1/courses/{course_id}/live-sessions/`: Schedule a live class (Instructor).
- `POST /api/v1/live-sessions/{session_id}/register/`: Register learner for session.
- `POST /api/v1/live-sessions/{session_id}/join/`: Generate secure room access token/link and log join attendance.

## 7. Engagement & Reviews (`/discussions/`, `/reviews/`)
- `GET /api/v1/courses/{course_id}/discussions/`: List Q&A threads.
- `POST /api/v1/courses/{course_id}/discussions/`: Post question thread.
- `POST /api/v1/discussions/{thread_id}/replies/`: Reply to discussion thread.
- `GET /api/v1/courses/{course_id}/reviews/`: Course reviews and average rating score.
- `POST /api/v1/courses/{course_id}/reviews/`: Submit rating and review (enrolled learners only).

## 8. Certificates (`/certificates/`)
- `POST /api/v1/enrollments/{enrollment_id}/certificate/issue/`: Validate completion criteria and generate certificate PDF.
- `GET /api/v1/certificates/{certificate_id}/`: Certificate details and download URL.
- `GET /api/v1/certificates/verify/{certificate_number}/`: Public, non-authenticated verification endpoint.
