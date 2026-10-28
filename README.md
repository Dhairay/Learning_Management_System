# Enterprise Learning Management System (LMS)

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.2-green.svg)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/Django%20REST%20Framework-3.18-red.svg)](https://django-rest-framework.org)
[![Vue 3](https://img.shields.io/badge/Vue.js-3.4%20(TS)-emerald.svg)](https://vuejs.org)
[![Vite](https://img.shields.io/badge/Vite-5.1-purple.svg)](https://vitejs.dev)

A scalable, multi-tenant **Enterprise Learning Management System (LMS)** architected as a **Modular Monolith** using **Django REST Framework (DRF)** on the backend and **Vue.js 3 (Composition API + TypeScript + Pinia)** on the frontend.

Designed per the High-Level Design (HLD) and Low-Level Design (LLD) blueprints from the technical requirements specification.

---

## 🌟 Key Capabilities & Architectural Pillars

1. **Organization-Aware Multi-Tenancy**:
   - Isolated tenant domains (`Acme Engineering Academy`, `Nova Product & Design Institute`, etc.) with strict boundary enforcement.
   - Global user identity with multi-organization membership and scoped roles (`PlatformAdmin`, `OrgAdmin`, `Instructor`, `Student`).
   - Tenant-scoped query isolation and composite foreign key uniqueness constraints.

2. **Mixed Commercial Monetization**:
   - Free enrollment lifecycle with immediate entitlement grant (`access_status: GRANTED`).
   - Paid courses with atomic checkout sessions, idempotency keys, order snapshots, simulated provider reconciliation, and verified entitlement.

3. **Blended Delivery (Recorded Lectures + Live Classes)**:
   - **Recorded Media**: Direct signed upload flow with playback authorization tokens.
   - **Live Classes**: Provider-agnostic adapter (`Jitsi Meet`, `Daily.co`, `Zoom`) with automated student registration and verified attendance duration tracking.

4. **Rigorous Assessments**:
   - **Interactive Quizzes**: Randomized questions, attempt tracking, time limits, and server-side evaluation (answer keys hidden from learner APIs).
   - **Capstone Assignments**: Versioned text/file submissions, rubric-based scoring, and instructor feedback loops.

5. **Authoritative PDF Certification**:
   - Unified `CourseCompletionService` gating certification behind completion of all required lessons, passing all required quizzes, and passing all required assignments.
   - High-resolution landscape PDF generation using ReportLab (`/media/certificates/*.pdf`).
   - Public, non-authenticated certificate verification portal (`/verify/:certificateNumber`).

6. **Social & Engagement Features**:
   - Threaded Q&A course discussion forum with nested replies.
   - Verified student star ratings (1–5) and reviews (strictly gated to enrolled learners).

---

## 🏛️ Project Directory Structure

```text
├── backend/
│   ├── config/             # Django settings, URLs, WSGI, ASGI
│   ├── apps/
│   │   ├── accounts/       # Custom User, Organization, Membership, Invitations
│   │   ├── courses/        # Categories, Courses, Sections, Lessons, Pricing
│   │   ├── enrollments/    # Orders, Payments, Entitlements, Enrollments
│   │   ├── learning/       # LessonProgress, CourseCompletion, Services
│   │   ├── assessments/    # Quizzes, Questions, Attempts, Assignments, Grades
│   │   ├── live_sessions/  # LiveSession, Registration, Attendance
│   │   ├── discussions/    # Forum Threads, Replies, Course Reviews
│   │   ├── certificates/   # Certificate models, ReportLab PDF generation
│   │   ├── media_assets/   # Storage keys, media processing, playback tokens
│   │   ├── notifications/  # Notification center
│   │   └── audit/          # Security and administrative audit trail
│   ├── tests/              # Pytest-django test suite
│   ├── seed_data.py        # Realistic multi-tenant data seeder
│   └── manage.py
├── frontend/
│   ├── src/
│   │   ├── api/            # Centralized httpClient, auth, course, quiz, cert APIs
│   │   ├── assets/         # Enterprise dark-mode design system (main.css)
│   │   ├── layouts/        # MainLayout (Tenant switcher, navbar, notifications)
│   │   ├── stores/         # Pinia authStore, courseStore
│   │   ├── types/          # Full TypeScript domain contracts
│   │   └── views/          # Catalog, Player, Quiz, Assignment, Live, Cert, Studio
├── docs/
│   ├── HLD.md              # High-Level Design Architecture
│   ├── LLD.md              # Low-Level Design & Data Dictionary
│   ├── API_SPEC.md         # REST API Contract
│   └── MAPPINGS.md         # Requirement -> Module -> DB -> UI Mapping Matrix
└── infrastructure/
    ├── docker-compose.yml  # Docker Compose (Postgres, Redis, Backend, Frontend)
    ├── Dockerfile.backend
    ├── Dockerfile.frontend
    └── nginx.conf
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+ & npm**

### 2. Backend Setup
```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Or on Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply database migrations
python manage.py migrate

# Seed realistic multi-tenant data (Organizations, Courses, Quizzes, Certificates)
python seed_data.py

# Run the Django development server
python manage.py runserver 127.0.0.1:8000
```
Backend API will be accessible at `http://127.0.0.1:8000/api/v1/`.

### 3. Frontend Setup
```bash
cd frontend

# Install npm packages
npm install

# Start Vite development server
npm run dev
```
Frontend will be available at `http://localhost:5173/`.

---

## 🔑 Pre-Seeded Demo Accounts (1-Click Login on `/login`)

| Role | Email | Password | Pre-Configured Access |
|---|---|---|---|
| **Platform / Org Admin** | `admin@lms.local` | `AdminPass123!` | Full admin access, tenant provisioning, member role management |
| **Course Instructor** | `instructor@lms.local` | `InstructorPass123!` | Instructor Studio, course authoring, assignment grading, live sessions |
| **Certified Student** | `student@lms.local` | `StudentPass123!` | Enrolled in Distributed Systems, 100% progress, issued PDF certificate |
| **Personalized Demo** | `tanish@lms.local` | `TanishPass123!` | Student enrolled in free Python & DRF course |

---

## 🧪 Automated Test Suite

Run the automated pytest test suite covering multi-tenant isolation, free vs. paid course enrollment boundaries, quiz evaluation, and certificate eligibility predicates:

```bash
cd backend
python -m pytest tests
```

---

## 🐳 Docker Deployment

To launch the complete containerized stack (PostgreSQL 15, Redis 7, Django backend, and Nginx Vue frontend):

```bash
docker-compose -f infrastructure/docker-compose.yml up --build
```
- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`
