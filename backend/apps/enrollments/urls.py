from django.urls import path
from .views import (
    CourseEnrollView, CheckoutSessionView, PaymentProcessView,
    MyEnrollmentsView, EnrollmentCurriculumView
)

urlpatterns = [
    path('courses/<uuid:course_id>/enroll/', CourseEnrollView.as_view(), name='course_enroll'),
    path('checkout-sessions/', CheckoutSessionView.as_view(), name='checkout_sessions'),
    path('payments/process/', PaymentProcessView.as_view(), name='payment_process'),
    path('me/enrollments/', MyEnrollmentsView.as_view(), name='my_enrollments'),
    path('enrollments/<uuid:enrollment_id>/curriculum/', EnrollmentCurriculumView.as_view(), name='enrollment_curriculum'),
]
