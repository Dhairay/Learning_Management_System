from typing import Optional
from core.exceptions import EntityNotFoundError, UnauthorizedDomainAction, BusinessRuleViolation
from repositories.course_repository import CourseRepository
from repositories.organization_repository import OrganizationRepository
from apps.courses.models import Course, CourseSection, Lesson, CoursePrice
from apps.accounts.models import OrganizationMembership

class CourseService:
    def __init__(
        self,
        course_repo: Optional[CourseRepository] = None,
        org_repo: Optional[OrganizationRepository] = None
    ):
        self.course_repo = course_repo or CourseRepository()
        self.org_repo = org_repo or OrganizationRepository()

    def list_courses(self, user, org_slug: Optional[str] = None, category_slug: Optional[str] = None, search: Optional[str] = None):
        is_instructor_or_admin = False
        if user.is_authenticated:
            if user.is_staff or OrganizationMembership.objects.filter(
                user=user, role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
            ).exists():
                is_instructor_or_admin = True

        return self.course_repo.get_catalog_courses(
            org_slug=org_slug,
            category_slug=category_slug,
            search=search,
            include_drafts=is_instructor_or_admin
        )

    def get_course_detail(self, course_id: str) -> Course:
        course = self.course_repo.get_course_detail(course_id)
        if not course:
            raise EntityNotFoundError(f"Course '{course_id}' not found.")
        return course

    def publish_course(self, course_id: str, actor_user) -> Course:
        course = self.get_course_detail(course_id)
        membership = self.org_repo.get_membership(str(course.organization.id), str(actor_user.id))
        is_instructor = membership and membership.role in ['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
        if not is_instructor and not actor_user.is_staff:
            raise UnauthorizedDomainAction("Only instructors or admins can publish courses.")

        course.status = 'PUBLISHED'
        course.save(update_fields=['status'])
        return course

    def add_section(self, course_id: str, title: str, actor_user) -> CourseSection:
        course = self.get_course_detail(course_id)
        return self.course_repo.create_section(course=course, title=title)

    def add_lesson(self, section_id: str, title: str, lesson_type: str, content_text: str, duration_seconds: int, actor_user) -> Lesson:
        section = CourseSection.objects.select_related('course').filter(id=section_id).first()
        if not section:
            raise EntityNotFoundError(f"Section '{section_id}' not found.")
        return self.course_repo.create_lesson(
            section=section,
            title=title,
            lesson_type=lesson_type,
            content_text=content_text,
            duration_seconds=duration_seconds
        )

    def verify_lesson_playback_access(self, lesson_id: str, user) -> Lesson:
        lesson = self.course_repo.find_lesson(lesson_id)
        if not lesson:
            raise EntityNotFoundError(f"Lesson '{lesson_id}' not found.")

        # Check instructor or active enrollment
        course = lesson.section.course
        from apps.enrollments.models import Enrollment
        has_enrollment = Enrollment.objects.filter(
            course=course, student_membership__user=user, status='ACTIVE'
        ).exists()
        is_instructor = OrganizationMembership.objects.filter(
            organization=course.organization, user=user, role__in=['PLATFORM_ADMIN', 'ORG_ADMIN', 'INSTRUCTOR']
        ).exists()

        if not has_enrollment and not is_instructor and not user.is_staff:
            raise UnauthorizedDomainAction("You must be enrolled in this course to access this lesson.")

        return lesson
