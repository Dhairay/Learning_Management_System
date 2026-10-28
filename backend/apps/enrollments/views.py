import uuid
from rest_framework import status, views, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Order, OrderItem, Payment, Entitlement, Enrollment
from .serializers import EnrollmentSerializer, OrderSerializer
from apps.courses.models import Course, CourseSection, Lesson
from apps.accounts.models import OrganizationMembership
from apps.learning.models import LessonProgress

class CourseEnrollView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        org = course.organization
        user = request.user

        # Ensure user has a membership in this organization
        membership, _ = OrganizationMembership.objects.get_or_create(
            organization=org,
            user=user,
            defaults={'role': 'STUDENT', 'status': 'ACTIVE'}
        )

        # Check existing enrollment
        existing_enrollment = Enrollment.objects.filter(
            student_membership=membership,
            course=course,
            status='ACTIVE'
        ).first()

        if existing_enrollment:
            return Response({
                'enrollment_id': str(existing_enrollment.id),
                'course_id': str(course.id),
                'status': existing_enrollment.status,
                'access_status': 'GRANTED',
                'message': 'You are already enrolled in this course.'
            })

        # Check if course is paid and user has no entitlement
        if not course.is_free:
            has_entitlement = Entitlement.objects.filter(
                organization=org,
                user=user,
                course=course,
                status='ACTIVE'
            ).exists()

            if not has_entitlement:
                price = getattr(course, 'price', None)
                amount = price.amount_minor if price else 4900
                currency = price.currency if price else 'USD'
                return Response({
                    'course_id': str(course.id),
                    'access_status': 'PURCHASE_REQUIRED',
                    'checkout_required': True,
                    'price': {
                        'amount_minor': amount,
                        'currency': currency,
                        'formatted': f"{currency} {amount / 100:.2f}"
                    },
                    'message': 'Payment required to enroll in this course.'
                }, status=status.HTTP_200_OK)

        # Free course or existing entitlement -> Create Enrollment & Entitlement
        entitlement, _ = Entitlement.objects.get_or_create(
            organization=org,
            user=user,
            course=course,
            defaults={'source_type': 'FREE_ENROLLMENT', 'status': 'ACTIVE'}
        )

        enrollment = Enrollment.objects.create(
            organization=org,
            student_membership=membership,
            course=course,
            status='ACTIVE'
        )

        return Response({
            'enrollment_id': str(enrollment.id),
            'course_id': str(course.id),
            'status': enrollment.status,
            'access_status': 'GRANTED',
            'message': 'Enrollment successful! Access granted.'
        }, status=status.HTTP_201_CREATED)

class CheckoutSessionView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        course_id = request.data.get('course_id')
        course = get_object_or_404(Course, id=course_id)
        org = course.organization
        price = getattr(course, 'price', None)
        total_minor = price.amount_minor if price else 4900
        currency = price.currency if price else 'USD'

        order = Order.objects.create(
            organization=org,
            buyer_user=request.user,
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
        payment = Payment.objects.create(
            order=order,
            provider='SIMULATED',
            provider_reference=f"sim_{uuid.uuid4().hex[:12]}",
            amount_minor=total_minor,
            currency=currency,
            status='PENDING'
        )

        return Response({
            'order_id': str(order.id),
            'payment_id': str(payment.id),
            'total_minor': total_minor,
            'currency': currency,
            'course_title': course.title,
            'checkout_url': f"/checkout/pay/{order.id}"
        }, status=status.HTTP_201_CREATED)

class PaymentProcessView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        order_id = request.data.get('order_id')
        order = get_object_or_404(Order, id=order_id, buyer_user=request.user)
        
        # Simulate payment success
        order.status = 'COMPLETED'
        order.save()

        payment = order.payments.first()
        if payment:
            payment.status = 'SUCCESS'
            payment.save()

        # Grant entitlement and enrollment for all items in order
        enrollments_created = []
        for item in order.items.all():
            course = item.course
            org = course.organization
            
            Entitlement.objects.get_or_create(
                organization=org,
                user=request.user,
                course=course,
                defaults={'source_type': 'PURCHASE', 'status': 'ACTIVE'}
            )

            membership, _ = OrganizationMembership.objects.get_or_create(
                organization=org,
                user=request.user,
                defaults={'role': 'STUDENT', 'status': 'ACTIVE'}
            )

            enrollment, _ = Enrollment.objects.get_or_create(
                organization=org,
                student_membership=membership,
                course=course,
                defaults={'status': 'ACTIVE'}
            )
            enrollments_created.append(str(enrollment.id))

        return Response({
            'detail': 'Payment successfully processed!',
            'order_id': str(order.id),
            'status': order.status,
            'enrollments': enrollments_created
        })

class MyEnrollmentsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        enrollments = Enrollment.objects.filter(
            student_membership__user=request.user,
            status='ACTIVE'
        ).select_related('course', 'course__category', 'course__organization', 'course__price')
        return Response(EnrollmentSerializer(enrollments, many=True).data)

class EnrollmentCurriculumView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, enrollment_id):
        enrollment = get_object_or_404(
            Enrollment.objects.select_related('course', 'student_membership__user'),
            id=enrollment_id
        )
        if enrollment.student_membership.user != request.user and not request.user.is_staff:
            return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        course = enrollment.course
        sections = CourseSection.objects.filter(course=course).prefetch_related('lessons')
        
        completed_lessons = set(
            LessonProgress.objects.filter(enrollment=enrollment, completed=True).values_list('lesson_id', flat=True)
        )

        curriculum = []
        for sec in sections:
            sec_data = {
                'id': str(sec.id),
                'title': sec.title,
                'position': sec.position,
                'lessons': []
            }
            for les in sec.lessons.all():
                sec_data['lessons'].append({
                    'id': str(les.id),
                    'title': les.title,
                    'lesson_type': les.lesson_type,
                    'position': les.position,
                    'is_required': les.is_required,
                    'duration_seconds': les.duration_seconds,
                    'is_completed': les.id in completed_lessons,
                })
            curriculum.append(sec_data)

        return Response({
            'enrollment_id': str(enrollment.id),
            'course_id': str(course.id),
            'course_title': course.title,
            'progress_percentage': enrollment.progress_percentage,
            'curriculum': curriculum
        })
