import os
import django
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from apps.accounts.models import User, Organization, OrganizationMembership
from apps.courses.models import Category, Course, CoursePrice, CourseSection, Lesson
from apps.media_assets.models import MediaAsset
from apps.enrollments.models import Enrollment, Entitlement, Order, OrderItem, Payment
from apps.learning.models import LessonProgress, CourseCompletion
from apps.assessments.models import (
    Quiz, Question, AnswerOption, QuizAttempt, QuizResponse,
    Assignment, AssignmentSubmission, AssignmentGrade
)
from apps.live_sessions.models import LiveSession, LiveSessionRegistration, AttendanceRecord
from apps.discussions.models import DiscussionThread, DiscussionReply, CourseReview
from apps.certificates.models import Certificate
from apps.certificates.services import CertificateGeneratorService
from apps.notifications.models import Notification
from apps.audit.models import AuditLog

def seed():
    print("Seeding LMS Enterprise Platform database...")

    # 1. Create Users
    admin_user, _ = User.objects.get_or_create(
        email='admin@lms.local',
        defaults={
            'first_name': 'Eleanor',
            'last_name': 'Vance',
            'headline': 'Chief Learning Officer & Platform Admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    admin_user.set_password('AdminPass123!')
    admin_user.save()

    instructor_user, _ = User.objects.get_or_create(
        email='instructor@lms.local',
        defaults={
            'first_name': 'Dr. Marcus',
            'last_name': 'Sterling',
            'headline': 'Principal Architect & Distributed Systems Specialist',
            'bio': 'Over 15 years designing mission-critical high-throughput microservices and cloud infrastructures.',
        }
    )
    instructor_user.set_password('InstructorPass123!')
    instructor_user.save()

    student_user, _ = User.objects.get_or_create(
        email='student@lms.local',
        defaults={
            'first_name': 'Sarah',
            'last_name': 'Connor',
            'headline': 'Full-Stack Software Engineer Fellow',
        }
    )
    student_user.set_password('StudentPass123!')
    student_user.save()

    tanish_user, _ = User.objects.get_or_create(
        email='tanish@lms.local',
        defaults={
            'first_name': 'Tanish',
            'last_name': 'Developer',
            'headline': 'Lead Platform Developer',
        }
    )
    tanish_user.set_password('TanishPass123!')
    tanish_user.save()

    # 2. Create Organizations
    org_tech, _ = Organization.objects.get_or_create(
        slug='acme-academy',
        defaults={
            'name': 'Acme Engineering Academy',
            'description': 'Premier enterprise academy for software architects and senior engineering leaders.',
            'website': 'https://acme-academy.internal',
            'status': 'ACTIVE',
            'settings': {'primary_color': '#3B82F6', 'currency': 'USD'}
        }
    )

    org_design, _ = Organization.objects.get_or_create(
        slug='nova-institute',
        defaults={
            'name': 'Nova Product & Design Institute',
            'description': 'Modern human-centered design, product management, and design systems training.',
            'website': 'https://nova-design.org',
            'status': 'ACTIVE',
            'settings': {'primary_color': '#8B5CF6', 'currency': 'USD'}
        }
    )

    # Memberships
    OrganizationMembership.objects.get_or_create(
        organization=org_tech, user=admin_user, defaults={'role': 'ORG_ADMIN', 'status': 'ACTIVE'}
    )
    OrganizationMembership.objects.get_or_create(
        organization=org_tech, user=instructor_user, defaults={'role': 'INSTRUCTOR', 'status': 'ACTIVE'}
    )
    student_mem_tech, _ = OrganizationMembership.objects.get_or_create(
        organization=org_tech, user=student_user, defaults={'role': 'STUDENT', 'status': 'ACTIVE'}
    )
    tanish_mem_tech, _ = OrganizationMembership.objects.get_or_create(
        organization=org_tech, user=tanish_user, defaults={'role': 'STUDENT', 'status': 'ACTIVE'}
    )

    # 3. Categories
    cat_sys, _ = Category.objects.get_or_create(
        slug='system-architecture',
        defaults={'name': 'Distributed Systems & Architecture', 'icon': 'server'}
    )
    cat_backend, _ = Category.objects.get_or_create(
        slug='backend-engineering',
        defaults={'name': 'Backend & Cloud Engineering', 'icon': 'database'}
    )
    cat_frontend, _ = Category.objects.get_or_create(
        slug='frontend-web',
        defaults={'name': 'Modern Web & Frontend', 'icon': 'code'}
    )

    # 4. Media Asset
    video_asset, _ = MediaAsset.objects.get_or_create(
        organization=org_tech,
        title='Distributed Consensus & Raft Architecture',
        defaults={
            'asset_type': 'VIDEO',
            'storage_key': 'media/acme-academy/raft-consensus.mp4',
            'playback_url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
            'duration_seconds': 720,
            'status': 'READY'
        }
    )

    # 5. Courses
    # Course 1: Distributed Systems (Paid)
    course_dist, _ = Course.objects.get_or_create(
        organization=org_tech,
        slug='distributed-systems-cloud-architecture',
        defaults={
            'title': 'Distributed Systems & Cloud Architecture Masterclass',
            'instructor_membership': OrganizationMembership.objects.get(organization=org_tech, user=instructor_user),
            'category': cat_sys,
            'short_description': 'Master distributed consensus, idempotency, event-driven pipelines, and cloud scalability.',
            'description': 'A comprehensive masterclass designed by principal engineers for architects scaling enterprise systems. Covers multi-region resilience, transactional outbox, Kafka event ordering, Raft consensus, and zero-downtime database migrations.',
            'thumbnail_url': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?auto=format&fit=crop&w=800&q=80',
            'level': 'ADVANCED',
            'status': 'PUBLISHED',
            'visibility': 'PUBLIC',
            'is_free': False
        }
    )
    CoursePrice.objects.get_or_create(course=course_dist, defaults={'currency': 'USD', 'amount_minor': 8900})

    # Sections & Lessons for Course 1
    s1, _ = CourseSection.objects.get_or_create(course=course_dist, position=1, defaults={'title': '1. Foundations of Distributed Reliability'})
    l1, _ = Lesson.objects.get_or_create(
        section=s1, position=1,
        defaults={
            'title': 'Anatomy of Distributed Consensus & CAP Theorem in Practice',
            'lesson_type': 'VIDEO',
            'media_asset': video_asset,
            'content_text': 'Detailed breakdown of partition tolerance, quorum consensus, and trade-offs in distributed transactions.',
            'duration_seconds': 720,
            'is_required': True
        }
    )
    l2, _ = Lesson.objects.get_or_create(
        section=s1, position=2,
        defaults={
            'title': 'Transactional Outbox & Dual-Write Prevention',
            'lesson_type': 'ARTICLE',
            'content_text': 'Why direct publishing inside database transactions is dangerous, and how the transactional outbox pattern guarantees at-least-once delivery.',
            'duration_seconds': 480,
            'is_required': True
        }
    )

    s2, _ = CourseSection.objects.get_or_create(course=course_dist, position=2, defaults={'title': '2. Comprehensive Assessment & Hands-On Project'})
    l3, _ = Lesson.objects.get_or_create(
        section=s2, position=1,
        defaults={
            'title': 'Milestone Quiz: Distributed Data Consistency',
            'lesson_type': 'QUIZ',
            'duration_seconds': 600,
            'is_required': True
        }
    )
    l4, _ = Lesson.objects.get_or_create(
        section=s2, position=2,
        defaults={
            'title': 'Architecture Project: Scalable Payment & Entitlement Engine',
            'lesson_type': 'ASSIGNMENT',
            'duration_seconds': 1200,
            'is_required': True
        }
    )

    # Quiz for Course 1
    quiz_dist, _ = Quiz.objects.get_or_create(
        course=course_dist,
        lesson=l3,
        defaults={
            'title': 'Distributed Data Consistency & Invariant Verification',
            'description': 'Assess your knowledge on quorum consensus, network partitions, and idempotency guarantees.',
            'pass_percentage': 70,
            'max_attempts': 3,
            'time_limit_minutes': 20
        }
    )

    q1, _ = Question.objects.get_or_create(
        quiz=quiz_dist, position=1,
        defaults={
            'text': 'What is the primary benefit of the Transactional Outbox pattern when publishing events to a message broker?',
            'question_type': 'SINGLE_CHOICE',
            'points': 50
        }
    )
    AnswerOption.objects.get_or_create(question=q1, text='Eliminates dual-write inconsistencies between database commits and broker publishes', defaults={'is_correct': True})
    AnswerOption.objects.get_or_create(question=q1, text='Guarantees exactly-once network transmission across all nodes', defaults={'is_correct': False})
    AnswerOption.objects.get_or_create(question=q1, text='Speeds up query latency on read-heavy models', defaults={'is_correct': False})

    q2, _ = Question.objects.get_or_create(
        quiz=quiz_dist, position=2,
        defaults={
            'text': 'Under a network partition (P in CAP), what guarantee must a CP system sacrifice?',
            'question_type': 'SINGLE_CHOICE',
            'points': 50
        }
    )
    AnswerOption.objects.get_or_create(question=q2, text='Availability (A) to preserve consistent state', defaults={'is_correct': True})
    AnswerOption.objects.get_or_create(question=q2, text='Consistency (C) to allow writes on disconnected partitions', defaults={'is_correct': False})
    AnswerOption.objects.get_or_create(question=q2, text='Durability (D) to reduce write amplification', defaults={'is_correct': False})

    # Assignment for Course 1
    assign_dist, _ = Assignment.objects.get_or_create(
        course=course_dist,
        lesson=l4,
        defaults={
            'title': 'Architecture Blueprint: Scalable Payment & Entitlement Engine',
            'instructions': 'Submit an architecture document explaining how idempotency keys, payment webhooks, database constraints, and outbox events are coordinated to guarantee no double-charging and accurate course entitlements.',
            'max_score': 100,
            'passing_score': 70,
            'due_at': timezone.now() + timedelta(days=30),
            'is_required': True
        }
    )

    # Course 2: Python & Django REST Framework (Free)
    course_python, _ = Course.objects.get_or_create(
        organization=org_tech,
        slug='django-rest-framework-production-guide',
        defaults={
            'title': 'Enterprise Django REST Framework Architecture',
            'instructor_membership': OrganizationMembership.objects.get(organization=org_tech, user=instructor_user),
            'category': cat_backend,
            'short_description': 'Build clean modular monoliths with Django, DRF, JWT authentication, and automated testing.',
            'description': 'Learn industry best practices for architecting maintainable Django APIs. Covers custom user models, multi-tenancy isolation, serializers, model constraints, and pytest-django integration.',
            'thumbnail_url': 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80',
            'level': 'INTERMEDIATE',
            'status': 'PUBLISHED',
            'visibility': 'PUBLIC',
            'is_free': True
        }
    )
    sp1, _ = CourseSection.objects.get_or_create(course=course_python, position=1, defaults={'title': '1. Core Foundations'})
    Lesson.objects.get_or_create(
        section=sp1, position=1,
        defaults={
            'title': 'Custom User Model & Tenancy Strategy',
            'lesson_type': 'VIDEO',
            'duration_seconds': 540,
            'is_required': True
        }
    )
    Lesson.objects.get_or_create(
        section=sp1, position=2,
        defaults={
            'title': 'Enforcing Domain Invariants with Model Constraints',
            'lesson_type': 'ARTICLE',
            'duration_seconds': 420,
            'is_required': True
        }
    )

    # Course 3: Vue 3 & TypeScript
    course_vue, _ = Course.objects.get_or_create(
        organization=org_tech,
        slug='vue-3-typescript-fullstack-frontend',
        defaults={
            'title': 'Vue 3 Composition API & TypeScript Mastery',
            'instructor_membership': OrganizationMembership.objects.get(organization=org_tech, user=instructor_user),
            'category': cat_frontend,
            'short_description': 'State-of-the-art Single Page App development with Vue 3, Pinia, TypeScript, and Vite.',
            'description': 'Master enterprise frontend architecture. Build clean feature-first components, custom composables, reactive store management, and responsive modern user interfaces.',
            'thumbnail_url': 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80',
            'level': 'INTERMEDIATE',
            'status': 'PUBLISHED',
            'visibility': 'PUBLIC',
            'is_free': False
        }
    )
    CoursePrice.objects.get_or_create(course=course_vue, defaults={'currency': 'USD', 'amount_minor': 4900})

    # 6. Live Session
    now = timezone.now()
    live_sess, _ = LiveSession.objects.get_or_create(
        course=course_dist,
        title='Live Q&A & Architecture Review with Dr. Marcus Sterling',
        defaults={
            'instructor_membership': OrganizationMembership.objects.get(organization=org_tech, user=instructor_user),
            'description': 'Deep-dive interactive session on handling edge cases in distributed payment reconciliation and live system diagrams review.',
            'provider': 'JITSI',
            'provider_session_id': 'acme-dist-arch-live-01',
            'room_url': 'https://meet.jit.si/LMS-acme-academy-dist-arch-live-01',
            'scheduled_start': now + timedelta(days=2, hours=3),
            'scheduled_end': now + timedelta(days=2, hours=4, minutes=30),
            'status': 'SCHEDULED'
        }
    )

    # 7. Seed Student Enrollments & Demo Completed Course
    # Student enrolled in Distributed Systems
    order1, _ = Order.objects.get_or_create(
        organization=org_tech,
        buyer_user=student_user,
        defaults={
            'currency': 'USD',
            'total_minor': 8900,
            'status': 'COMPLETED',
            'idempotency_key': 'seed_order_student_01'
        }
    )
    OrderItem.objects.get_or_create(order=order1, course=course_dist, defaults={'price_minor': 8900, 'currency': 'USD'})
    Payment.objects.get_or_create(order=order1, defaults={'provider': 'STRIPE', 'provider_reference': 'ch_seed_01', 'amount_minor': 8900, 'status': 'SUCCESS'})

    Entitlement.objects.get_or_create(
        organization=org_tech, user=student_user, course=course_dist,
        defaults={'source_type': 'PURCHASE', 'status': 'ACTIVE'}
    )

    enrollment_student, _ = Enrollment.objects.get_or_create(
        organization=org_tech,
        student_membership=student_mem_tech,
        course=course_dist,
        defaults={'status': 'ACTIVE'}
    )

    # Mark all lessons complete for student_user to demonstrate full completion!
    LessonProgress.objects.get_or_create(enrollment=enrollment_student, lesson=l1, defaults={'completed': True, 'last_position_seconds': 720, 'completed_at': now})
    LessonProgress.objects.get_or_create(enrollment=enrollment_student, lesson=l2, defaults={'completed': True, 'completed_at': now})
    LessonProgress.objects.get_or_create(enrollment=enrollment_student, lesson=l3, defaults={'completed': True, 'completed_at': now})
    LessonProgress.objects.get_or_create(enrollment=enrollment_student, lesson=l4, defaults={'completed': True, 'completed_at': now})

    # Pass the quiz
    QuizAttempt.objects.get_or_create(
        enrollment=enrollment_student, quiz=quiz_dist, attempt_number=1,
        defaults={'status': 'EVALUATED', 'score': 100.0, 'passed': True, 'submitted_at': now}
    )

    # Submit and grade assignment
    sub1, _ = AssignmentSubmission.objects.get_or_create(
        assignment=assign_dist, enrollment=enrollment_student, version=1,
        defaults={
            'content_text': 'Detailed architecture document implementing idempotency keys using Redis locks with a fallback PostgreSQL table and transaction outbox pattern.',
            'status': 'GRADED',
            'submitted_at': now - timedelta(days=1)
        }
    )
    AssignmentGrade.objects.get_or_create(
        submission=sub1,
        defaults={
            'grader_membership': OrganizationMembership.objects.get(organization=org_tech, user=instructor_user),
            'score': 95.0,
            'feedback': 'Exemplary blueprint! The handling of network race conditions and database rollback semantics is thorough.',
            'graded_at': now
        }
    )

    # Complete course and issue official PDF certificate
    CourseCompletion.objects.get_or_create(
        enrollment=enrollment_student,
        defaults={'policy_version': 'v1.0', 'status': 'COMPLETED', 'completed_at': now}
    )
    enrollment_student.status = 'COMPLETED'
    enrollment_student.save()

    cert1, _ = Certificate.objects.get_or_create(
        organization=org_tech,
        enrollment=enrollment_student,
        defaults={
            'certificate_number': 'CERT-ACME-202610-A91B4C',
            'status': 'VALID',
            'policy_version': 'v1.0'
        }
    )
    CertificateGeneratorService.generate_pdf(cert1)

    # Also register for live class
    reg1, _ = LiveSessionRegistration.objects.get_or_create(live_session=live_sess, enrollment=enrollment_student)
    AttendanceRecord.objects.get_or_create(registration=reg1, duration_seconds=3600)

    # Discussions & Reviews
    dt1, _ = DiscussionThread.objects.get_or_create(
        organization=org_tech, course=course_dist, author=student_user,
        title='Handling clock drift in distributed lease timers?',
        defaults={'content': 'In a distributed locking mechanism using consensus leases, how do you defend against monotonic clock skews across virtualized hypervisors?'}
    )
    DiscussionReply.objects.get_or_create(
        thread=dt1, author=instructor_user,
        defaults={'content': 'Use fencing tokens! Every acquired lease increments a monotonically increasing counter at the database. Whenever a stale worker attempts a write, the database rejects tokens lower than current.'}
    )

    CourseReview.objects.get_or_create(
        organization=org_tech, course=course_dist, student=student_user,
        defaults={
            'rating': 5,
            'review_text': 'Exceptional content. The depth of transactional outbox and distributed consensus explanations is unmatched.',
            'status': 'PUBLISHED'
        }
    )

    # Also enroll tanish in the free Django course
    Entitlement.objects.get_or_create(
        organization=org_tech, user=tanish_user, course=course_python,
        defaults={'source_type': 'FREE_ENROLLMENT', 'status': 'ACTIVE'}
    )
    Enrollment.objects.get_or_create(
        organization=org_tech, student_membership=tanish_mem_tech, course=course_python,
        defaults={'status': 'ACTIVE'}
    )

    # Notification
    Notification.objects.get_or_create(
        organization=org_tech, user=student_user,
        title='Certificate Ready for Download!',
        defaults={
            'message': 'Congratulations! You have satisfied all learning, quiz, and assignment requirements for Distributed Systems. Your official verifiable PDF credential is now available.',
            'notification_type': 'CERTIFICATE_ISSUED',
            'read': False
        }
    )

    # Audit Log
    AuditLog.objects.get_or_create(
        organization=org_tech, actor_user=admin_user,
        action='COURSE_PUBLISHED', target_type='Course', target_id=str(course_dist.id),
        defaults={'payload': {'title': course_dist.title, 'version': '1.0'}}
    )

    print("Successfully seeded all LMS database models with realistic multi-tenant data!")
    print(f"Generated Certificate Number: {cert1.certificate_number}")
    print(f"Certificate PDF Path: {cert1.pdf_file.name}")

if __name__ == '__main__':
    seed()
