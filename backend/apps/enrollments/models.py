import uuid
from django.db import models
from apps.accounts.models import User, Organization, OrganizationMembership
from apps.courses.models import Course

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='orders')
    buyer_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    currency = models.CharField(max_length=3, default='USD')
    total_minor = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    idempotency_key = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} - {self.status} ({self.currency} {self.total_minor / 100:.2f})"

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    price_minor = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default='USD')

    class Meta:
        db_table = 'order_items'

class Payment(models.Model):
    STATUS_CHOICES = [
        ('SUCCESS', 'Success'),
        ('PENDING', 'Pending'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    provider = models.CharField(max_length=50, default='SIMULATED')
    provider_reference = models.CharField(max_length=255, blank=True, default='')
    amount_minor = models.PositiveIntegerField(default=0)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-created_at']

class Entitlement(models.Model):
    SOURCE_CHOICES = [
        ('FREE_ENROLLMENT', 'Free Enrollment'),
        ('PURCHASE', 'Direct Purchase'),
        ('ORGANIZATION_SPONSORED', 'Organization Sponsored'),
    ]
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('EXPIRED', 'Expired'),
        ('REVOKED', 'Revoked'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='entitlements')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='entitlements')
    source_type = models.CharField(max_length=30, choices=SOURCE_CHOICES, default='FREE_ENROLLMENT')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    starts_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'entitlements'
        ordering = ['-starts_at']

    def __str__(self):
        return f"{self.user.email} -> {self.course.title} ({self.status})"

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('SUSPENDED', 'Suspended'),
        ('CANCELLED', 'Cancelled'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='enrollments')
    student_membership = models.ForeignKey(OrganizationMembership, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'enrollments'
        constraints = [
            models.UniqueConstraint(fields=['student_membership', 'course'], name='unique_student_course_enrollment')
        ]
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"Enrollment: {self.student_membership.user.email} in {self.course.title}"

    @property
    def progress_percentage(self):
        from apps.courses.models import Lesson
        from apps.learning.models import LessonProgress
        total = Lesson.objects.filter(section__course=self.course).count()
        if total == 0:
            return 100
        completed = LessonProgress.objects.filter(enrollment=self, completed=True).count()
        return min(100, int((completed / total) * 100))
