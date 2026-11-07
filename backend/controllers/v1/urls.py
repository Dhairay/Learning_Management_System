"""
API v1 Controller URL routing.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from controllers.v1.auth_controller import (
    LoginController,
    RegisterController,
    RolesListController,
    ProvisionAdminUserController,
    UserDirectoryController,
    MeController,
    MyOrganizationsController,
)
from controllers.v1.organization_controller import (
    OrganizationViewSet,
    OrganizationMembersController,
    OrganizationInvitationController,
    AcceptInvitationController,
)
from controllers.v1.course_controller import (
    CourseViewSet,
    CategoryListController,
    CoursePublishController,
    CourseSectionCreateController,
    SectionLessonCreateController,
    LessonPlaybackController,
)
from controllers.v1.enrollment_controller import (
    CourseEnrollController,
    CheckoutSessionController,
    PaymentProcessController,
    MyEnrollmentsController,
    EnrollmentCurriculumController,
)
from controllers.v1.learning_controller import (
    UpdateLessonProgressController,
    RecalculateCompletionController,
)
from controllers.v1.assessment_controller import (
    QuizDetailController,
    QuizStartAttemptController,
    QuizSubmitController,
    AssignmentDetailController,
    AssignmentSubmitController,
    AssignmentGradeController,
    CourseAssignmentsListController,
    InstructorSubmissionsController,
)
from controllers.v1.certificate_controller import (
    IssueCertificateController,
    CertificateDetailController,
    CertificateVerifyController,
)
from controllers.v1.live_session_controller import (
    CourseLiveSessionsController,
    LiveSessionRegisterController,
    LiveSessionJoinController,
)
from controllers.v1.discussion_controller import (
    CourseDiscussionsController,
    ThreadRepliesController,
    CourseReviewsController,
)
from controllers.v1.media_controller import (
    MediaUploadSessionController,
    MediaAssetDetailController,
)
from controllers.v1.notification_controller import NotificationListController
from controllers.v1.audit_controller import AuditLogListController

# DefaultRouters for ViewSets
org_router = DefaultRouter()
org_router.register('', OrganizationViewSet, basename='organization')

course_router = DefaultRouter()
course_router.register('', CourseViewSet, basename='course')

urlpatterns = [
    # 1. Auth & Identity Controllers
    path('auth/roles/', RolesListController.as_view(), name='auth_roles'),
    path('auth/register/', RegisterController.as_view(), name='auth_register'),
    path('auth/admin-users/', ProvisionAdminUserController.as_view(), name='auth_provision_admin_user'),
    path('auth/users/', UserDirectoryController.as_view(), name='auth_user_directory'),
    path('auth/login/', LoginController.as_view(), name='auth_login'),
    path('auth/token/', LoginController.as_view(), name='auth_token'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='auth_token_refresh'),
    path('auth/invitations/accept/', AcceptInvitationController.as_view(), name='auth_accept_invitation'),

    path('me/', MeController.as_view(), name='me_profile'),
    path('me/organizations/', MyOrganizationsController.as_view(), name='me_organizations'),

    # 2. Organization Controllers
    path('organizations/<slug:org_slug>/members/', OrganizationMembersController.as_view(), name='org_members'),
    path('organizations/<slug:org_slug>/members/<uuid:membership_id>/roles/', OrganizationMembersController.as_view(), name='org_member_roles'),
    path('organizations/<slug:org_slug>/invitations/', OrganizationInvitationController.as_view(), name='org_invitations'),
    path('organizations/', include(org_router.urls)),

    # 3. Course Catalog & Authoring Controllers
    path('courses/categories/', CategoryListController.as_view(), name='category_list'),
    path('courses/<uuid:course_id>/publish/', CoursePublishController.as_view(), name='course_publish'),
    path('courses/<uuid:course_id>/sections/', CourseSectionCreateController.as_view(), name='course_section_create'),
    path('courses/sections/<uuid:section_id>/lessons/', SectionLessonCreateController.as_view(), name='section_lesson_create'),
    path('courses/lessons/<uuid:lesson_id>/playback/', LessonPlaybackController.as_view(), name='lesson_playback'),
    path('courses/', include(course_router.urls)),

    # 4. Enrollment & Monetization Controllers
    path('courses/<uuid:course_id>/enroll/', CourseEnrollController.as_view(), name='course_enroll'),
    path('checkout-sessions/', CheckoutSessionController.as_view(), name='checkout_sessions'),
    path('payments/process/', PaymentProcessController.as_view(), name='payment_process'),
    path('me/enrollments/', MyEnrollmentsController.as_view(), name='my_enrollments'),
    path('enrollments/<uuid:enrollment_id>/curriculum/', EnrollmentCurriculumController.as_view(), name='enrollment_curriculum'),

    # 5. Learning & Progress Controllers
    path('learning/progress/', UpdateLessonProgressController.as_view(), name='learning_progress_update'),
    path('learning/completion/<uuid:enrollment_id>/recalculate/', RecalculateCompletionController.as_view(), name='learning_recalculate_completion'),

    # 6. Assessment Controllers
    path('quizzes/<uuid:quiz_id>/', QuizDetailController.as_view(), name='quiz_detail'),
    path('quizzes/<uuid:quiz_id>/attempts/', QuizStartAttemptController.as_view(), name='quiz_start_attempt'),
    path('quiz-attempts/<uuid:attempt_id>/submit/', QuizSubmitController.as_view(), name='quiz_submit'),
    path('assignments/<uuid:assignment_id>/', AssignmentDetailController.as_view(), name='assignment_detail'),
    path('assignments/<uuid:assignment_id>/submit/', AssignmentSubmitController.as_view(), name='assignment_submit'),
    path('submissions/<uuid:submission_id>/grade/', AssignmentGradeController.as_view(), name='assignment_grade'),
    path('courses/<uuid:course_id>/assignments/', CourseAssignmentsListController.as_view(), name='course_assignments'),
    path('courses/<uuid:course_id>/submissions/', InstructorSubmissionsController.as_view(), name='instructor_submissions'),

    # 7. Certificate Controllers
    path('enrollments/<uuid:enrollment_id>/certificate/issue/', IssueCertificateController.as_view(), name='issue_certificate'),
    path('certificates/<uuid:certificate_id>/', CertificateDetailController.as_view(), name='certificate_detail'),
    path('certificates/verify/<str:certificate_number>/', CertificateVerifyController.as_view(), name='certificate_verify'),

    # 8. Live Classroom Controllers
    path('courses/<uuid:course_id>/live-sessions/', CourseLiveSessionsController.as_view(), name='course_live_sessions'),
    path('live-sessions/<uuid:session_id>/register/', LiveSessionRegisterController.as_view(), name='live_session_register'),
    path('live-sessions/<uuid:session_id>/join/', LiveSessionJoinController.as_view(), name='live_session_join'),

    # 9. Discussion & Review Controllers
    path('courses/<uuid:course_id>/discussions/', CourseDiscussionsController.as_view(), name='course_discussions'),
    path('discussions/<uuid:thread_id>/replies/', ThreadRepliesController.as_view(), name='thread_replies'),
    path('courses/<uuid:course_id>/reviews/', CourseReviewsController.as_view(), name='course_reviews'),

    # 10. Media Asset Controllers
    path('media/upload-sessions/', MediaUploadSessionController.as_view(), name='media_upload_session'),
    path('media/<uuid:asset_id>/status/', MediaAssetDetailController.as_view(), name='media_status'),

    # 11. Notification Controllers
    path('notifications/', NotificationListController.as_view(), name='notifications_list'),
    path('notifications/<uuid:notification_id>/read/', NotificationListController.as_view(), name='notification_read'),

    # 12. Audit Log Controllers
    path('audit/', AuditLogListController.as_view(), name='audit_log_list'),
]
