import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/authStore';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: () => {
        const orgSlug = localStorage.getItem('current_org_slug') || 'acme-academy';
        return `/org/${orgSlug}/catalog`;
      },
    },
    {
      path: '/login',
      name: 'Login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { public: true },
    },
    {
      path: '/register',
      name: 'Register',
      component: () => import('../views/auth/RegisterView.vue'),
      meta: { public: true },
    },
    {
      path: '/organizations',
      name: 'Organizations',
      component: () => import('../views/auth/OrganizationsView.vue'),
    },
    {
      path: '/verify-certificate',
      name: 'VerifyCertificate',
      component: () => import('../views/certificates/VerifyCertificateView.vue'),
      meta: { public: true },
    },
    {
      path: '/verify/:certificateNumber',
      name: 'VerifyCertificateDirect',
      component: () => import('../views/certificates/VerifyCertificateView.vue'),
      meta: { public: true },
    },
    {
      path: '/checkout/pay/:orderId',
      name: 'CheckoutPayment',
      component: () => import('../views/enrollment/CheckoutView.vue'),
    },
    // Org-scoped routes
    {
      path: '/org/:orgSlug',
      component: () => import('../layouts/MainLayout.vue'),
      children: [
        {
          path: '',
          redirect: (to) => `/org/${to.params.orgSlug}/catalog`,
        },
        {
          path: 'catalog',
          name: 'Catalog',
          component: () => import('../views/catalog/CatalogView.vue'),
          meta: { public: true },
        },
        {
          path: 'my-learning',
          name: 'MyLearning',
          component: () => import('../views/learning/MyLearningView.vue'),
        },
        {
          path: 'courses/:courseId',
          name: 'CourseDetail',
          component: () => import('../views/catalog/CourseDetailView.vue'),
          meta: { public: true },
        },
        {
          path: 'learn/:courseId/:lessonId',
          name: 'LearningPlayer',
          component: () => import('../views/learning/LearningPlayerView.vue'),
        },
        {
          path: 'quiz/:quizId',
          name: 'QuizPlayer',
          component: () => import('../views/assessments/QuizPlayerView.vue'),
        },
        {
          path: 'assignments/:assignmentId',
          name: 'AssignmentDetail',
          component: () => import('../views/assessments/AssignmentDetailView.vue'),
        },
        {
          path: 'live/:sessionId',
          name: 'LiveSessionRoom',
          component: () => import('../views/live/LiveSessionRoomView.vue'),
        },
        {
          path: 'courses/:courseId/discussions',
          name: 'CourseDiscussions',
          component: () => import('../views/engagement/DiscussionsView.vue'),
        },
        {
          path: 'courses/:courseId/reviews',
          name: 'CourseReviews',
          component: () => import('../views/engagement/ReviewsView.vue'),
          meta: { public: true },
        },
        {
          path: 'certificates/:certificateId',
          name: 'CertificateViewer',
          component: () => import('../views/certificates/CertificateView.vue'),
        },
        {
          path: 'instructor/dashboard',
          name: 'InstructorDashboard',
          component: () => import('../views/instructor/InstructorDashboardView.vue'),
        },
        {
          path: 'admin/members',
          name: 'AdminMembers',
          component: () => import('../views/admin/OrganizationAdminView.vue'),
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
});

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore();
  const token = localStorage.getItem('access_token');

  if (to.params.orgSlug) {
    localStorage.setItem('current_org_slug', to.params.orgSlug as string);
  }

  if (token && !authStore.user) {
    try {
      await authStore.fetchProfile();
    } catch (e) {
      // Token expired
    }
  }

  if (!to.meta.public && !authStore.isAuthenticated) {
    return next({ name: 'Login', query: { redirect: to.fullPath } });
  }

  next();
});

export default router;
