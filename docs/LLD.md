# Low-Level Design (LLD) & Data Dictionary

## 1. Core Domain Models & Schemas

### 1.1 Identity & Multi-Tenancy (`accounts`)
- **`User`**:
  - `id`: UUID (Primary Key)
  - `email`: EmailField (unique, normalized)
  - `first_name`, `last_name`: CharField
  - `is_active`, `is_staff`, `is_superuser`: BooleanField
  - `created_at`, `updated_at`: DateTimeField
- **`Organization`**:
  - `id`: UUID (Primary Key)
  - `name`: CharField(max_length=255)
  - `slug`: SlugField(unique=True)
  - `status`: CharField (`ACTIVE`, `SUSPENDED`, `INACTIVE`)
  - `settings`: JSONField (theme, allowed payment gateways, default language)
  - `created_at`: DateTimeField
- **`OrganizationMembership`**:
  - `id`: UUID (Primary Key)
  - `organization`: ForeignKey(`Organization`, on_delete=CASCADE)
  - `user`: ForeignKey(`User`, on_delete=CASCADE)
  - `role`: CharField (`PLATFORM_ADMIN`, `ORG_ADMIN`, `INSTRUCTOR`, `STUDENT`)
  - `status`: CharField (`ACTIVE`, `PENDING_INVITE`, `REVOKED`)
  - `joined_at`: DateTimeField
  - *Constraint*: `UniqueConstraint(fields=['organization', 'user'])`
- **`Invitation`**:
  - `id`: UUID (Primary Key)
  - `organization`: ForeignKey(`Organization`, on_delete=CASCADE)
  - `email`: EmailField
  - `role`: CharField
  - `token_hash`: CharField
  - `expires_at`: DateTimeField
  - `status`: CharField (`PENDING`, `ACCEPTED`, `EXPIRED`, `REVOKED`)

---

### 1.2 Courses & Curriculum (`courses`, `media_assets`)
- **`Category`**:
  - `id`: UUID, `organization`: ForeignKey(nullable for global), `name`, `slug`
- **`Course`**:
  - `id`: UUID (Primary Key)
  - `organization`: ForeignKey(`Organization`, on_delete=CASCADE)
  - `instructor_membership`: ForeignKey(`OrganizationMembership`, on_delete=SET_NULL, null=True)
  - `category`: ForeignKey(`Category`, on_delete=SET_NULL, null=True)
  - `title`: CharField(max_length=255)
  - `slug`: SlugField
  - `description`: TextField
  - `level`: CharField (`BEGINNER`, `INTERMEDIATE`, `ADVANCED`)
  - `status`: CharField (`DRAFT`, `PUBLISHED`, `ARCHIVED`, `SUSPENDED`)
  - `visibility`: CharField (`PUBLIC`, `ORGANIZATION_ONLY`, `PRIVATE`)
  - `is_free`: BooleanField(default=True)
  - `thumbnail_url`: URLField
  - *Constraint*: `UniqueConstraint(fields=['organization', 'slug'])`
- **`CoursePrice`**:
  - `id`: UUID, `course`: OneToOneField(`Course`), `currency`: CharField(3), `amount_minor`: PositiveIntegerField
- **`CourseSection`**:
  - `id`: UUID, `course`: ForeignKey(`Course`, on_delete=CASCADE), `title`: CharField, `position`: PositiveIntegerField
  - *Constraint*: `UniqueConstraint(fields=['course', 'position'])`
- **`MediaAsset`**:
  - `id`: UUID, `organization`: ForeignKey(`Organization`), `title`: CharField, `asset_type`: (`VIDEO`, `DOCUMENT`, `IMAGE`), `storage_key`: CharField, `duration_seconds`: PositiveIntegerField, `status`: (`READY`, `PROCESSING`, `FAILED`)
- **`Lesson`**:
  - `id`: UUID, `section`: ForeignKey(`CourseSection`, on_delete=CASCADE)
  - `title`: CharField, `lesson_type`: (`VIDEO`, `ARTICLE`, `QUIZ`, `ASSIGNMENT`, `LIVE_SESSION`)
  - `media_asset`: ForeignKey(`MediaAsset`, null=True, blank=True)
  - `content_text`: TextField(blank=True)
  - `position`: PositiveIntegerField
  - `is_required`: BooleanField(default=True)
  - `duration_seconds`: PositiveIntegerField(default=0)
  - *Constraint*: `UniqueConstraint(fields=['section', 'position'])`

---

### 1.3 Commerce & Enrollment (`enrollments`)
- **`Enrollment`**:
  - `id`: UUID (Primary Key)
  - `organization`: ForeignKey(`Organization`, on_delete=CASCADE)
  - `student_membership`: ForeignKey(`OrganizationMembership`, on_delete=CASCADE)
  - `course`: ForeignKey(`Course`, on_delete=CASCADE)
  - `status`: CharField (`ACTIVE`, `COMPLETED`, `SUSPENDED`, `CANCELLED`)
  - `enrolled_at`: DateTimeField(auto_now_add=True)
  - *Constraint*: `UniqueConstraint(fields=['student_membership', 'course'])`
- **`Entitlement`**:
  - `id`: UUID, `user`: ForeignKey(`User`), `course`: ForeignKey(`Course`), `source_type`: (`FREE_ENROLLMENT`, `PURCHASE`, `ORGANIZATION_SPONSORED`), `status`: (`ACTIVE`, `EXPIRED`, `REVOKED`)
- **`Order`**:
  - `id`: UUID, `organization`: ForeignKey(`Organization`), `buyer_user`: ForeignKey(`User`), `currency`: CharField, `total_minor`: PositiveIntegerField, `status`: (`PENDING`, `COMPLETED`, `FAILED`, `REFUNDED`), `idempotency_key`: CharField(unique=True)
- **`OrderItem`**:
  - `id`: UUID, `order`: ForeignKey(`Order`), `course`: ForeignKey(`Course`), `price_minor`: PositiveIntegerField
- **`Payment`**:
  - `id`: UUID, `order`: ForeignKey(`Order`), `provider`: CharField (`STRIPE`, `RAZORPAY`, `SIMULATED`), `provider_reference`: CharField, `amount_minor`: PositiveIntegerField, `status`: (`SUCCESS`, `PENDING`, `FAILED`)

---

### 1.4 Progress & Learning Trackers (`learning`)
- **`LessonProgress`**:
  - `id`: UUID, `enrollment`: ForeignKey(`Enrollment`), `lesson`: ForeignKey(`Lesson`), `completed`: BooleanField(default=False), `last_position_seconds`: PositiveIntegerField(default=0), `completed_at`: DateTimeField(null=True)
  - *Constraint*: `UniqueConstraint(fields=['enrollment', 'lesson'])`
- **`CourseCompletion`**:
  - `id`: UUID, `enrollment`: OneToOneField(`Enrollment`), `completed_at`: DateTimeField, `policy_version`: CharField, `status`: CharField (`COMPLETED`, `REVOKED`)

---

### 1.5 Assessments: Quizzes & Assignments (`assessments`)
- **`Quiz`**:
  - `id`: UUID, `course`: ForeignKey(`Course`), `lesson`: OneToOneField(`Lesson`, null=True), `title`: CharField, `pass_percentage`: PositiveIntegerField(default=70), `max_attempts`: PositiveIntegerField(default=3), `time_limit_minutes`: PositiveIntegerField(default=30)
- **`Question`**:
  - `id`: UUID, `quiz`: ForeignKey(`Quiz`), `text`: TextField, `question_type`: (`SINGLE_CHOICE`, `MULTIPLE_CHOICE`), `points`: PositiveIntegerField(default=10), `position`: PositiveIntegerField
- **`AnswerOption`**:
  - `id`: UUID, `question`: ForeignKey(`Question`), `text`: CharField, `is_correct`: BooleanField(default=False)
- **`QuizAttempt`**:
  - `id`: UUID, `enrollment`: ForeignKey(`Enrollment`), `quiz`: ForeignKey(`Quiz`), `attempt_number`: PositiveIntegerField, `status`: (`IN_PROGRESS`, `SUBMITTED`, `EVALUATED`), `score`: FloatField(default=0.0), `passed`: BooleanField(default=False), `started_at`: DateTimeField, `submitted_at`: DateTimeField(null=True)
- **`Assignment`**:
  - `id`: UUID, `course`: ForeignKey(`Course`), `lesson`: OneToOneField(`Lesson`, null=True), `title`: CharField, `instructions`: TextField, `max_score`: PositiveIntegerField(default=100), `passing_score`: PositiveIntegerField(default=60), `due_at`: DateTimeField(null=True), `is_required`: BooleanField(default=True)
- **`AssignmentSubmission`**:
  - `id`: UUID, `assignment`: ForeignKey(`Assignment`), `enrollment`: ForeignKey(`Enrollment`), `version`: PositiveIntegerField(default=1), `content_text`: TextField, `file_url`: URLField(blank=True), `submitted_at`: DateTimeField(auto_now_add=True), `status`: (`SUBMITTED`, `GRADED`, `RESUBMISSION_REQUIRED`)
- **`AssignmentGrade`**:
  - `id`: UUID, `submission`: OneToOneField(`AssignmentSubmission`), `grader_membership`: ForeignKey(`OrganizationMembership`), `score`: FloatField, `feedback`: TextField, `graded_at`: DateTimeField(auto_now=True)

---

### 1.6 Live Sessions (`live_sessions`)
- **`LiveSession`**:
  - `id`: UUID, `course`: ForeignKey(`Course`), `instructor_membership`: ForeignKey(`OrganizationMembership`), `title`: CharField, `description`: TextField, `provider`: CharField (`DAILY_CO`, `ZOOM`, `JITSI`, `INTERNAL`), `provider_session_id`: CharField, `room_url`: URLField, `scheduled_start`: DateTimeField, `scheduled_end`: DateTimeField, `status`: (`SCHEDULED`, `LIVE`, `COMPLETED`, `CANCELLED`)
- **`LiveSessionRegistration`**:
  - `id`: UUID, `live_session`: ForeignKey(`LiveSession`), `enrollment`: ForeignKey(`Enrollment`), `registered_at`: DateTimeField
  - *Constraint*: `UniqueConstraint(fields=['live_session', 'enrollment'])`
- **`AttendanceRecord`**:
  - `id`: UUID, `registration`: ForeignKey(`LiveSessionRegistration`), `joined_at`: DateTimeField, `left_at`: DateTimeField(null=True), `duration_seconds`: PositiveIntegerField(default=0)

---

### 1.7 Certificates & Engagement (`certificates`, `discussions`)
- **`Certificate`**:
  - `id`: UUID, `enrollment`: OneToOneField(`Enrollment`), `certificate_number`: CharField(unique=True), `pdf_file`: FileField(upload_to='certificates/'), `issued_at`: DateTimeField(auto_now_add=True), `status`: (`VALID`, `REVOKED`)
- **`DiscussionThread`**:
  - `id`: UUID, `course`: ForeignKey(`Course`), `author`: ForeignKey(`User`), `title`: CharField, `content`: TextField, `created_at`: DateTimeField
- **`DiscussionReply`**:
  - `id`: UUID, `thread`: ForeignKey(`DiscussionThread`), `author`: ForeignKey(`User`), `content`: TextField, `created_at`: DateTimeField
- **`CourseReview`**:
  - `id`: UUID, `course`: ForeignKey(`Course`), `student`: ForeignKey(`User`), `rating`: PositiveSmallIntegerField(choices=[1,2,3,4,5]), `review_text`: TextField, `created_at`: DateTimeField
  - *Constraint*: `UniqueConstraint(fields=['course', 'student'])`
