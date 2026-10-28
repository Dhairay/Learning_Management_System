import uuid
from django.db import models
from apps.accounts.models import Organization, OrganizationMembership
from apps.media_assets.models import MediaAsset

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, null=True, blank=True, related_name='categories')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    icon = models.CharField(max_length=50, blank=True, default='book')

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'categories'
        ordering = ['name']

    def __str__(self):
        return self.name

class Course(models.Model):
    LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner'),
        ('INTERMEDIATE', 'Intermediate'),
        ('ADVANCED', 'Advanced'),
        ('ALL_LEVELS', 'All Levels'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
        ('SUSPENDED', 'Suspended'),
    ]
    VISIBILITY_CHOICES = [
        ('PUBLIC', 'Public Catalog'),
        ('ORGANIZATION_ONLY', 'Organization Only'),
        ('PRIVATE', 'Private / Invitation Only'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='courses')
    instructor_membership = models.ForeignKey(
        OrganizationMembership, on_delete=models.SET_NULL, null=True, blank=True, related_name='authored_courses'
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    short_description = models.CharField(max_length=300, blank=True, default='')
    description = models.TextField(blank=True, default='')
    thumbnail_url = models.URLField(blank=True, default='')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='ALL_LEVELS')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='PUBLIC')
    is_free = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'courses'
        constraints = [
            models.UniqueConstraint(fields=['organization', 'slug'], name='unique_org_course_slug')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.organization.slug})"

    @property
    def price_display(self):
        if self.is_free:
            return 'Free'
        price = getattr(self, 'price', None)
        if price:
            return f"{price.currency} {price.amount_minor / 100:.2f}"
        return 'Free'

    @property
    def total_lessons(self):
        return Lesson.objects.filter(section__course=self).count()

    @property
    def total_duration_seconds(self):
        return sum(Lesson.objects.filter(section__course=self).values_list('duration_seconds', flat=True))

class CoursePrice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.OneToOneField(Course, on_delete=models.CASCADE, related_name='price')
    currency = models.CharField(max_length=3, default='USD')
    amount_minor = models.PositiveIntegerField(default=0)  # e.g. 4900 = $49.00
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'course_prices'

    def __str__(self):
        return f"{self.currency} {self.amount_minor / 100:.2f}"

class CourseSection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='sections')
    title = models.CharField(max_length=255)
    position = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'course_sections'
        constraints = [
            models.UniqueConstraint(fields=['course', 'position'], name='unique_section_position')
        ]
        ordering = ['position']

    def __str__(self):
        return f"{self.course.title} - S{self.position}: {self.title}"

class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ('VIDEO', 'Video Lecture'),
        ('ARTICLE', 'Reading Material'),
        ('QUIZ', 'Interactive Quiz'),
        ('ASSIGNMENT', 'Graded Assignment'),
        ('LIVE_SESSION', 'Live Virtual Class'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    section = models.ForeignKey(CourseSection, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES, default='VIDEO')
    media_asset = models.ForeignKey(MediaAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name='lessons')
    content_text = models.TextField(blank=True, default='')
    position = models.PositiveIntegerField(default=1)
    is_required = models.BooleanField(default=True)
    duration_seconds = models.PositiveIntegerField(default=300)

    class Meta:
        db_table = 'lessons'
        constraints = [
            models.UniqueConstraint(fields=['section', 'position'], name='unique_lesson_position')
        ]
        ordering = ['position']

    def __str__(self):
        return f"{self.section.title} - L{self.position}: {self.title}"
