from typing import Optional
from django.db.models import QuerySet
from core.repositories.base_repository import BaseRepository
from apps.enrollments.models import Enrollment, Entitlement, Order, OrderItem, Payment

class EnrollmentRepository(BaseRepository[Enrollment]):
    model = Enrollment

    def find_active_enrollment(self, user_id: str, course_id: str) -> Optional[Enrollment]:
        return self.model.objects.filter(
            student_membership__user_id=user_id,
            course_id=course_id,
            status='ACTIVE'
        ).select_related('course', 'organization', 'student_membership__user').first()

    def get_user_enrollments(self, user_id: str) -> QuerySet[Enrollment]:
        return self.model.objects.filter(
            student_membership__user_id=user_id,
            status='ACTIVE'
        ).select_related('course', 'course__category', 'course__organization', 'course__price')

    def has_active_entitlement(self, user_id: str, course_id: str) -> bool:
        return Entitlement.objects.filter(
            user_id=user_id,
            course_id=course_id,
            status='ACTIVE'
        ).exists()

    def create_order_with_payment(self, organization, buyer_user, course, total_minor: int, currency: str) -> Order:
        import uuid
        order = Order.objects.create(
            organization=organization,
            buyer_user=buyer_user,
            currency=currency,
            total_minor=total_minor,
            status='PENDING',
            idempotency_key=str(uuid.uuid4())
        )
        OrderItem.objects.create(
            order=order,
            course=course,
            price_minor=total_minor,
            currency=currency
        )
        Payment.objects.create(
            order=order,
            provider='SIMULATED',
            provider_reference=f"sim_{uuid.uuid4().hex[:12]}",
            amount_minor=total_minor,
            currency=currency,
            status='PENDING'
        )
        return order

    def find_order(self, order_id: str, user_id: str) -> Optional[Order]:
        return Order.objects.filter(id=order_id, buyer_user_id=user_id).prefetch_related('items__course__organization', 'payments').first()
