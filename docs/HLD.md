# High-Level Design (HLD) — Enterprise Multi-Tenant LMS

## 1. Executive Summary & Architecture Principles
This Learning Management System (LMS) is designed as a scalable, cloud-native **Modular Monolith** using **Django REST Framework (DRF)** on the backend and **Vue.js 3 (Composition API + TypeScript)** on the frontend. The platform supports multi-tenant organization isolation, mixed commercial monetization (free and paid courses), blended asynchronous (recorded video) and synchronous (live streaming/conferencing) learning, rigorous assessments (quizzes & graded assignments), interactive engagement (discussions & reviews), and automated PDF certificate issuance.

### Core Architectural Decisions
1. **Organization-Aware Multi-Tenancy**:
   - Every tenant has its own isolated domain boundary: users, roles, courses, curriculum, orders, enrollments, reports, and audit logs.
   - Users maintain a single global identity but hold distinct `OrganizationMembership` records with scoped roles (`PlatformAdmin`, `OrgAdmin`, `Instructor`, `Student`).
   - Every incoming request resolves the active tenant context (`X-Organization-Slug` header or membership context) and strictly enforces tenant boundary checks.

2. **Modular Monolith Structure**:
   - Clean domain separation across Django applications (`accounts`, `courses`, `enrollments`, `learning`, `assessments`, `live_sessions`, `discussions`, `certificates`, `media_assets`, `notifications`, `audit`).
   - Enforces transactional boundaries using database-level constraints and atomic transactions for financial and eligibility calculations.
   - Enables future microservice extraction if specific domains (e.g., media streaming or live session telemetry) demand independent scaling.

3. **Blended Delivery (Recorded + Live)**:
   - **Recorded Media**: Direct-to-storage signed uploads with asynchronous transcoding triggers and short-lived signed playback tokens.
   - **Live Classes**: Provider-agnostic adapter interface (`LiveSessionProvider`) integrating Zoom/Daily.co/Jitsi, handling scheduled sessions, participant token issuance, and attendance ingestion.

4. **Authoritative Assessment & Certification**:
   - Quizzes with randomized questions, attempt tracking, and server-side evaluation.
   - Assignments with revision versioning, file submissions, rubric-based grading, and feedback.
   - Unified `CourseCompletionService` gating cryptographic/PDF certificate generation strictly when all required lessons are completed and assessments are passed.

---

## 2. System Architecture Diagram

```
                              +---------------------------------------+
                              |         Learners & Instructors        |
                              +---------------------------------------+
                                                  |
                                                  v
                              +---------------------------------------+
                              |    Cloud Edge / CDN / TLS Gateway     |
                              +---------------------------------------+
                                       /                     \
                                      /                       \
                                     v                         v
        +----------------------------------------+    +--------------------------------+
        |   Frontend SPA (Vue 3 + TS + Pinia)   |    |  Media CDN (HLS Video / PDFs)  |
        +----------------------------------------+    +--------------------------------+
                                     \
                                      v [REST API /api/v1/]
        +------------------------------------------------------------------------------+
        |                       Django REST Framework Monolith                         |
        |  +--------------------+---------------------+-----------------------------+  |
        |  | accounts (Tenancy) | courses (Catalog)   | enrollments (Commerce)      |  |
        |  +--------------------+---------------------+-----------------------------+  |
        |  | learning (Progress)| assessments (Quiz)  | live_sessions (Meetings)    |  |
        |  +--------------------+---------------------+-----------------------------+  |
        |  | discussions (Forum)| certificates (PDF)  | notifications & audit       |  |
        |  +--------------------+---------------------+-----------------------------+  |
        +------------------------------------------------------------------------------+
                               /              |             \
                              v               v              v
        +------------------------+  +------------------+  +----------------------------+
        | PostgreSQL Database    |  | Redis Cache & MQ |  | External Provider Adapters |
        | (Transactional Store)  |  | (Rate Limiting)  |  | - Payment Gateway (Stripe) |
        +------------------------+  +------------------+  | - Live Video (Zoom/Jitsi)  |
                                                          | - S3 / Object Storage      |
                                                          +----------------------------+
```

---

## 3. Organization & Tenancy Model
- **Global User Identity**: Users authenticate with normalized email and password.
- **Organization Memberships**: Users belong to one or more organizations with defined roles:
  - `PlatformAdmin`: System-wide maintenance and tenant provisioning.
  - `OrgAdmin`: Manages courses, members, billing settings, and reports within their organization.
  - `Instructor`: Authors courses, reviews assignments, hosts live sessions, and moderates discussions.
  - `Student`: Discovers courses, enrolls, accesses curriculum, participates in live classes, takes assessments, and claims certificates.
- **Tenant Isolation Enforcement**:
  - Middleware / Base ViewSets automatically filter QuerySets by `organization_id`.
  - Invariant validation prevents cross-tenant associations (e.g., enrolling in Org B's course using an Org A membership).
  - Multi-tenant data segregation is enforced at the database level with composite unique keys.

---

## 4. Scalability & Operational Blueprint
- **Stateless Application Servers**: Django runs as a stateless container behind Nginx / ALB.
- **Asynchronous Task Processing**: Heavy tasks (PDF certificate generation, media processing notifications, webhook dispatch) execute via Celery background workers.
- **Database Indexing**: Compound indexes on `(organization_id, slug)`, `(enrollment_id, lesson_id)`, and `(course_id, status)`.
- **Media Offloading**: Video streaming and large assignment uploads bypass the application server directly to Cloud Object Storage (S3 / GCS) via pre-signed authorization URLs.
