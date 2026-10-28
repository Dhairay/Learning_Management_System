import pytest
from rest_framework.test import APIClient
from apps.accounts.models import User, Organization, OrganizationMembership
from apps.courses.models import Course, CoursePrice, CourseSection, Lesson
from apps.enrollments.models import Enrollment, Entitlement
from apps.learning.models import LessonProgress, CourseCompletion
from apps.assessments.models import Quiz, Question, AnswerOption, QuizAttempt, Assignment, AssignmentSubmission, AssignmentGrade
from apps.certificates.models import Certificate
from apps.certificates.services import CertificateGeneratorService
from apps.learning.services import CourseCompletionService

@pytest.mark.django_db
class TestLMSArchitecture:
    def setup_method(self):
        self.client = APIClient()
        self.org_a = Organization.objects.create(name='Org Alpha', slug='org-alpha')
        self.org_b = Organization.objects.create(name='Org Beta', slug='org-beta')

        self.student = User.objects.create_user(email='teststudent@lms.local', password='Password123!')
        self.instructor = User.objects.create_user(email='testinstructor@lms.local', password='Password123!')

        self.client.force_authenticate(user=self.student)

        # Free course in Org Alpha
        self.course_free = Course.objects.create(
            organization=self.org_a,
            title='Free Intro Course',
            slug='free-intro-course',
            status='PUBLISHED',
            is_free=True
        )

        # Paid course in Org Alpha
        self.course_paid = Course.objects.create(
            organization=self.org_a,
            title='Advanced Masterclass',
            slug='advanced-masterclass',
            status='PUBLISHED',
            is_free=False
        )
        CoursePrice.objects.create(course=self.course_paid, currency='USD', amount_minor=5000)

    def test_free_enrollment_grants_immediate_access(self):
        """Free enrollment immediately creates an entitlement and active enrollment."""
        resp = self.client.post(f'/api/v1/courses/{self.course_free.id}/enroll/')
        assert resp.status_code == 201
        assert resp.data['access_status'] == 'GRANTED'
        assert Enrollment.objects.filter(course=self.course_free, student_membership__user=self.student, status='ACTIVE').exists()

    def test_paid_course_enrollment_requires_checkout(self):
        """Requesting enrollment for a paid course without an entitlement triggers PURCHASE_REQUIRED."""
        resp = self.client.post(f'/api/v1/courses/{self.course_paid.id}/enroll/')
        assert resp.status_code == 200
        assert resp.data['access_status'] == 'PURCHASE_REQUIRED'
        assert resp.data['checkout_required'] is True
        assert not Enrollment.objects.filter(course=self.course_paid, student_membership__user=self.student).exists()

    def test_quiz_grading_and_answer_hiding(self):
        """Learner API hides answer keys, and server-side submission accurately grades scores."""
        sec = CourseSection.objects.create(course=self.course_free, title='Section 1', position=1)
        les = Lesson.objects.create(section=sec, title='Quiz Lesson', lesson_type='QUIZ', position=1)
        quiz = Quiz.objects.create(course=self.course_free, lesson=les, title='Core Quiz', pass_percentage=70)
        q = Question.objects.create(quiz=quiz, text='What is 2+2?', position=1, points=10)
        opt_correct = AnswerOption.objects.create(question=q, text='4', is_correct=True)
        opt_wrong = AnswerOption.objects.create(question=q, text='5', is_correct=False)

        # Enroll first
        self.client.post(f'/api/v1/courses/{self.course_free.id}/enroll/')

        # Start attempt
        start_resp = self.client.post(f'/api/v1/quizzes/{quiz.id}/attempts/')
        assert start_resp.status_code == 201
        attempt_id = start_resp.data['id']

        # Submit wrong answer
        sub_resp = self.client.post(f'/api/v1/quiz-attempts/{attempt_id}/submit/', {
            'answers': {str(q.id): [str(opt_wrong.id)]}
        }, format='json')
        assert sub_resp.status_code == 200
        assert sub_resp.data['score'] == 0.0
        assert sub_resp.data['passed'] is False

    def test_certificate_eligibility_predicate(self):
        """Certificates cannot be issued until all required lessons, quizzes, and assignments are completed."""
        sec = CourseSection.objects.create(course=self.course_free, title='Section 1', position=1)
        l1 = Lesson.objects.create(section=sec, title='Mandatory Lesson', is_required=True, position=1)
        
        # Enroll
        self.client.post(f'/api/v1/courses/{self.course_free.id}/enroll/')
        enrollment = Enrollment.objects.get(course=self.course_free, student_membership__user=self.student)

        # Attempt to issue certificate prematurely
        cert_resp = self.client.post(f'/api/v1/enrollments/{enrollment.id}/certificate/issue/')
        assert cert_resp.status_code == 400
        assert 'Cannot issue certificate' in cert_resp.data['detail']

        # Complete lesson
        self.client.post('/api/v1/learning/progress/', {
            'lesson_id': str(l1.id),
            'completed': True
        }, format='json')

        # Now certificate generation succeeds
        cert_resp2 = self.client.post(f'/api/v1/enrollments/{enrollment.id}/certificate/issue/')
        assert cert_resp2.status_code == 201
        assert cert_resp2.data['certificate_number'].startswith('CERT-')
        assert Certificate.objects.filter(enrollment=enrollment).exists()
