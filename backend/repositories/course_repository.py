from typing import Optional
from django.db.models import QuerySet
from core.repositories.base_repository import BaseRepository
from apps.courses.models import Course, Category, CourseSection, Lesson, CoursePrice

class CourseRepository(BaseRepository[Course]):
    model = Course

    def get_catalog_courses(
        self,
        org_slug: Optional[str] = None,
        category_slug: Optional[str] = None,
        search: Optional[str] = None,
        include_drafts: bool = False
    ) -> QuerySet[Course]:
        qs = self.model.objects.all()
        if not include_drafts:
            qs = qs.filter(status='PUBLISHED')
        if org_slug:
            qs = qs.filter(organization__slug=org_slug)
        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if search:
            qs = qs.filter(title__icontains=search)
        return qs.select_related('organization', 'instructor_membership__user', 'category', 'price').prefetch_related('sections__lessons')

    def get_course_detail(self, course_id: str) -> Optional[Course]:
        return (
            self.model.objects
            .select_related('organization', 'price', 'category', 'instructor_membership__user')
            .prefetch_related('sections__lessons')
            .filter(id=course_id)
            .first()
        )

    def get_categories(self) -> QuerySet[Category]:
        return Category.objects.all()

    def create_section(self, course: Course, title: str) -> CourseSection:
        position = CourseSection.objects.filter(course=course).count() + 1
        return CourseSection.objects.create(course=course, title=title, position=position)

    def create_lesson(self, section: CourseSection, title: str, lesson_type: str = 'VIDEO', content_text: str = '', duration_seconds: int = 300) -> Lesson:
        position = Lesson.objects.filter(section=section).count() + 1
        return Lesson.objects.create(
            section=section,
            title=title,
            lesson_type=lesson_type,
            content_text=content_text,
            position=position,
            duration_seconds=duration_seconds
        )

    def find_lesson(self, lesson_id: str) -> Optional[Lesson]:
        return Lesson.objects.select_related('section__course__organization').filter(id=lesson_id).first()
