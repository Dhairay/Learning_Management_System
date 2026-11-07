from dataclasses import dataclass
from typing import Optional, List
from django.db import transaction
from core.exceptions import BusinessRuleViolation, EntityNotFoundError
from repositories.course_repository import CourseRepository
from repositories.enrollment_repository import EnrollmentRepository
from apps.accounts.models import OrganizationMembership
from apps.enrollments.models import Enrollment, Entitlement

@dataclass
class EnrollmentResult:
    enrollment_id: Optional[str]
    course_id: str
    access_status: str  # GRANTED | PURCHASE_REQUIRED | ALREADY_ENROLLED
    message: str
    checkout_required: bool = False
    checkout_url: Optional[str] = None
    price_minor: Optional[int] = None
    currency: Optional[str] = None

class EnrollmentService:
    def __init__(
        self,
        course_repo: Optional[CourseRepository] = None,
        enrollment_repo: Optional[EnrollmentRepository] = None
    ):
        self.course_repo = course_repo or CourseRepository()
        self.enrollment_repo = enrollment_repo or EnrollmentRepository()

    @transaction.atomic
    def enroll_student(self, user, course_id: str) -> EnrollmentResult:
        course = self.course_repo.find_by_id(course_id)
        if not course:
            raise EntityNotFoundError(f"Course '{course_id}' not found.")

        # 1. Check existing active enrollment
        existing = self.enrollment_repo.find_active_enrollment(str(user.id), str(course.id))
        if existing:
            return EnrollmentResult(
                enrollment_id=str(existing.id),
                course_id=str(course.id),
                access_status='GRANTED',
                message='You are already enrolled in this course.'
            )

        # 2. Check monetization & entitlement requirements
        if not course.is_free:
            has_entitlement = self.enrollment_repo.has_active_entitlement(str(user.id), str(course.id))
            if not has_entitlement:
                price = getattr(course, 'price', None)
                amount = price.amount_minor if price else 4900
                currency = price.currency if price else 'USD'
                return EnrollmentResult(
                    enrollment_id=None,
                    course_id=str(course.id),
                    access_status='PURCHASE_REQUIRED',
                    checkout_required=True,
                    message='Purchase required to unlock enrollment.',
                    checkout_url=f"/checkout/{course.id}",
                    price_minor=amount,
                    currency=currency
                )

        # 3. Ensure student membership in course's organization
        membership, _ = OrganizationMembership.objects.get_or_create(
            organization=course.organization,
            user=user,
            defaults={'role': 'STUDENT', 'status': 'ACTIVE'}
        )

        # 4. Create active enrollment (idempotent get_or_create)
        enrollment, created = Enrollment.objects.get_or_create(
            organization=course.organization,
            student_membership=membership,
            course=course,
            defaults={'status': 'ACTIVE'}
        )
        if not created and enrollment.status != 'ACTIVE':
            enrollment.status = 'ACTIVE'
            enrollment.save(update_fields=['status'])

        return EnrollmentResult(
            enrollment_id=str(enrollment.id),
            course_id=str(course.id),
            access_status='GRANTED',
            message='Enrollment successful! Access granted.' if created else 'You are already enrolled in this course.'
        )


    def create_checkout(self, user, course_id: str):
        course = self.course_repo.find_by_id(course_id)
        if not course:
            raise EntityNotFoundError(f"Course '{course_id}' not found.")

        price = getattr(course, 'price', None)
        total_minor = price.amount_minor if price else 4900
        currency = price.currency if price else 'USD'

        order = self.enrollment_repo.create_order_with_payment(
            organization=course.organization,
            buyer_user=user,
            course=course,
            total_minor=total_minor,
            currency=currency
        )
        payment = order.payments.first()
        return {
            'order_id': str(order.id),
            'payment_id': str(payment.id),
            'total_minor': total_minor,
            'currency': currency,
            'course_title': course.title,
            'checkout_url': f"/checkout/pay/{order.id}"
        }

    @transaction.atomic
    def process_payment(self, user, order_id: str):
        order = self.enrollment_repo.find_order(order_id, str(user.id))
        if not order:
            raise EntityNotFoundError(f"Order '{order_id}' not found.")

        order.status = 'COMPLETED'
        order.save(update_fields=['status'])

        payment = order.payments.first()
        if payment:
            payment.status = 'SUCCESS'
            payment.save(update_fields=['status'])

        enrollments_created = []
        for item in order.items.all():
            course = item.course
            org = course.organization

            Entitlement.objects.get_or_create(
                organization=org,
                user=user,
                course=course,
                defaults={'source_type': 'PURCHASE', 'status': 'ACTIVE'}
            )

            membership, _ = OrganizationMembership.objects.get_or_create(
                organization=org,
                user=user,
                defaults={'role': 'STUDENT', 'status': 'ACTIVE'}
            )

            enrollment, _ = Enrollment.objects.get_or_create(
                organization=org,
                student_membership=membership,
                course=course,
                defaults={'status': 'ACTIVE'}
            )
            enrollments_created.append(str(enrollment.id))

        return {
            'detail': 'Payment successfully processed!',
            'order_id': str(order.id),
            'status': order.status,
            'enrollments': enrollments_created
        }
