from rest_framework import status, permissions
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from core.controllers.base_controller import BaseController
from services.enrollment_service import EnrollmentService
from services.learning_service import LearningService
from apps.enrollments.serializers import EnrollmentSerializer, OrderSerializer

class CourseEnrollController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EnrollmentSerializer

    def __init__(self, enrollment_service: EnrollmentService = None, **kwargs):
        super().__init__(**kwargs)
        self.enrollment_service = enrollment_service or EnrollmentService()

    @extend_schema(summary="Enroll Student in Course", tags=['Enrollment Controller'])
    def post(self, request, course_id: str):
        result = self.enrollment_service.enroll_student(user=request.user, course_id=course_id)
        http_status = status.HTTP_201_CREATED if result.access_status == 'GRANTED' else status.HTTP_200_OK
        return Response({
            'enrollment_id': result.enrollment_id,
            'course_id': result.course_id,
            'access_status': result.access_status,
            'checkout_required': result.checkout_required,
            'message': result.message,
            'checkout_url': result.checkout_url,
            'price_minor': result.price_minor,
            'currency': result.currency,
        }, status=http_status)

class CheckoutSessionController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def __init__(self, enrollment_service: EnrollmentService = None, **kwargs):
        super().__init__(**kwargs)
        self.enrollment_service = enrollment_service or EnrollmentService()

    @extend_schema(summary="Create Checkout Session", tags=['Enrollment Controller'])
    def post(self, request):
        course_id = request.data.get('course_id')
        checkout_data = self.enrollment_service.create_checkout(user=request.user, course_id=course_id)
        return Response(checkout_data, status=status.HTTP_201_CREATED)

class PaymentProcessController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def __init__(self, enrollment_service: EnrollmentService = None, **kwargs):
        super().__init__(**kwargs)
        self.enrollment_service = enrollment_service or EnrollmentService()

    @extend_schema(summary="Process Order Payment", tags=['Enrollment Controller'])
    def post(self, request):
        order_id = request.data.get('order_id')
        payment_data = self.enrollment_service.process_payment(user=request.user, order_id=order_id)
        return Response(payment_data)

class MyEnrollmentsController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EnrollmentSerializer

    @extend_schema(summary="List User Enrollments", tags=['Enrollment Controller'])
    def get(self, request):
        from repositories.enrollment_repository import EnrollmentRepository
        enrollments = EnrollmentRepository().get_user_enrollments(str(request.user.id))
        return Response(self.serializer_class(enrollments, many=True).data)

class EnrollmentCurriculumController(BaseController):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EnrollmentSerializer

    def __init__(self, learning_service: LearningService = None, **kwargs):
        super().__init__(**kwargs)
        self.learning_service = learning_service or LearningService()

    @extend_schema(summary="Get Enrollment Curriculum and Progress", tags=['Enrollment Controller'])
    def get(self, request, enrollment_id: str):
        data = self.learning_service.get_enrollment_curriculum(request.user, enrollment_id)
        return Response(data)
