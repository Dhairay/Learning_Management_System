<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { courseApi } from '../../api/courseApi';
import { enrollmentApi } from '../../api/enrollmentApi';
import { liveSessionApi } from '../../api/liveSessionApi';
import { engagementApi } from '../../api/engagementApi';
import { useAuthStore } from '../../stores/authStore';
import { useToast } from '../../composables/useToast';
import type { Course, LiveSession, CourseReview } from '../../types';
import { 
  PlayCircle, Clock, BookOpen, Award, CheckCircle, Shield, 
  Video, Star, MessageSquare, ArrowRight, Lock, Check, Calendar,
  ShieldCheck, Sparkles, FileText
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const courseId = route.params.courseId as string;
const orgSlug = route.params.orgSlug as string;

const course = ref<Course | null>(null);
const liveSessions = ref<LiveSession[]>([]);
const reviewsData = ref<{ average_rating: number; total_reviews: number; reviews: CourseReview[] }>({
  average_rating: 0,
  total_reviews: 0,
  reviews: []
});

const isEnrolled = ref(false);
const enrollmentId = ref('');
const loading = ref(true);
const actionLoading = ref(false);

onMounted(async () => {
  try {
    const [c, sessions, revs] = await Promise.all([
      courseApi.getCourse(courseId),
      liveSessionApi.getSessions(courseId).catch(() => []),
      engagementApi.getReviews(courseId).catch(() => ({ average_rating: 0, total_reviews: 0, reviews: [] }))
    ]);
    course.value = c;
    liveSessions.value = sessions;
    reviewsData.value = revs;

    // Check enrollment status
    if (authStore.isAuthenticated) {
      const myEnrollments = await enrollmentApi.getMyEnrollments().catch(() => []);
      const found = myEnrollments.find(e => e.course.id === courseId);
      if (found) {
        isEnrolled.value = true;
        enrollmentId.value = found.id;
      }
    }
  } catch (e) {
    console.error('Failed to load course details', e);
  } finally {
    loading.value = false;
  }
});

async function handleEnrollOrPurchase() {
  if (!authStore.isAuthenticated) {
    router.push({ name: 'Login', query: { redirect: route.fullPath } });
    return;
  }

  actionLoading.value = true;
  try {
    const res = await enrollmentApi.enrollCourse(courseId);
    if (res.access_status === 'GRANTED') {
      isEnrolled.value = true;
      enrollmentId.value = res.enrollment_id || '';
      toast.success('Successfully Enrolled!', 'Welcome to the curriculum. Starting first lesson...');
      // Route directly to first lesson
      if (course.value?.sections?.[0]?.lessons?.[0]) {
        router.push(`/org/${orgSlug}/learn/${courseId}/${course.value.sections[0].lessons[0].id}`);
      } else {
        router.push(`/org/${orgSlug}/my-learning`);
      }
    } else if (res.access_status === 'PURCHASE_REQUIRED') {
      // Create checkout session
      const checkout = await enrollmentApi.createCheckoutSession(courseId);
      toast.info('Checkout Session Ready', 'Redirecting to payment gateway...');
      router.push(`/checkout/pay/${checkout.order_id}`);
    }
  } catch (err: any) {
    toast.error('Enrollment Failed', err.message || 'Please try again later.');
  } finally {
    actionLoading.value = false;
  }
}

function startLearning() {
  if (course.value?.sections?.[0]?.lessons?.[0]) {
    router.push(`/org/${orgSlug}/learn/${courseId}/${course.value.sections[0].lessons[0].id}`);
  }
}
</script>

<template>
  <div v-if="loading" class="text-center py-32 text-slate-500">
    <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
    Loading course details...
  </div>

  <div v-else-if="course" class="space-y-10 animate-fade-in">
    <!-- Single Unified Grid Layout -->
    <div class="grid lg:grid-cols-3 gap-8 items-start">
      <!-- Left Column: Hero Info, Curriculum, Live Sessions, Reviews -->
      <div class="lg:col-span-2 space-y-8">
        <!-- Hero Details -->
        <div class="space-y-4">
          <div class="flex items-center gap-2">
            <span class="badge badge-indigo text-[11px]">{{ course.category?.name || 'Curriculum' }}</span>
            <span class="badge badge-emerald text-[11px]">{{ course.level }}</span>
            <div v-if="reviewsData.total_reviews > 0" class="flex items-center gap-1 text-amber-400 text-xs font-bold ml-2">
              <Star class="w-3.5 h-3.5 fill-amber-400" />
              <span>{{ reviewsData.average_rating }}</span>
              <span class="text-slate-500 font-normal">({{ reviewsData.total_reviews }} reviews)</span>
            </div>
          </div>

          <h1 class="text-3xl sm:text-4xl font-extrabold text-white tracking-tight leading-tight">
            {{ course.title }}
          </h1>

          <p class="text-base text-slate-300 leading-relaxed">
            {{ course.description || course.short_description }}
          </p>

          <!-- Instructor Profile -->
          <div class="flex items-center justify-between pt-2 border-b border-slate-800/80 pb-5">
            <div class="flex items-center gap-3">
              <div class="w-11 h-11 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center font-bold text-sm text-indigo-400">
                {{ course.instructor_name[0] }}
              </div>
              <div>
                <div class="text-xs text-slate-400">Course Instructor</div>
                <div class="text-sm font-bold text-white">{{ course.instructor_name }}</div>
              </div>
            </div>

            <router-link 
              v-if="authStore.isInstructorOrAdmin" 
              :to="`/org/${orgSlug}/studio`"
              class="btn-secondary text-xs py-1.5 px-3 flex items-center gap-1.5 text-indigo-300 border-indigo-500/30 hover:bg-indigo-500/10"
            >
              <span>Manage Syllabus in Studio</span>
            </router-link>
          </div>
        </div>

        <!-- Curriculum Syllabus Breakdown (Placed directly under instructor profile) -->
        <div>
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-bold text-white flex items-center gap-2">
              <BookOpen class="w-5 h-5 text-indigo-400" /> Course Curriculum &amp; Syllabus
            </h2>
            <span class="text-xs text-slate-400">
              {{ course.sections?.length || 0 }} Sections &bull; {{ course.total_lessons || 0 }} Lessons
            </span>
          </div>

          <div v-if="!course.sections || course.sections.length === 0" class="glass-panel p-8 text-center text-xs text-slate-500 border border-slate-800">
            No sections published in this syllabus yet.
          </div>

          <div v-else class="space-y-4">
            <div 
              v-for="sec in course.sections" 
              :key="sec.id"
              class="glass-panel overflow-hidden border border-slate-800"
            >
              <div class="p-4 bg-slate-900/60 border-b border-slate-800/80 flex items-center justify-between">
                <span class="font-bold text-sm text-white">{{ sec.title }}</span>
                <span class="text-xs text-slate-400">{{ sec.lessons?.length || 0 }} Items</span>
              </div>
              <div class="divide-y divide-slate-800/40">
                <div 
                  v-for="les in sec.lessons" 
                  :key="les.id"
                  class="p-3.5 px-4 flex items-center justify-between text-xs hover:bg-slate-800/30 transition"
                >
                  <div class="flex items-center gap-3">
                    <span 
                      class="w-6 h-6 rounded-md flex items-center justify-center text-[10px] font-bold"
                      :class="{
                        'bg-indigo-500/20 text-indigo-400': les.lesson_type === 'VIDEO',
                        'bg-emerald-500/20 text-emerald-400': les.lesson_type === 'ARTICLE',
                        'bg-amber-500/20 text-amber-400': les.lesson_type === 'QUIZ',
                        'bg-rose-500/20 text-rose-400': les.lesson_type === 'ASSIGNMENT',
                        'bg-cyan-500/20 text-cyan-400': les.lesson_type === 'LIVE_SESSION',
                      }"
                    >
                      {{ les.lesson_type ? les.lesson_type.slice(0, 2) : 'LE' }}
                    </span>
                    <span class="text-slate-200 font-medium">{{ les.title }}</span>
                  </div>
                  <div class="flex items-center gap-3 text-slate-500 font-mono text-[11px]">
                    <Clock class="w-3.5 h-3.5 text-slate-500 inline mr-0.5" />
                    <span>{{ Math.round((les.duration_seconds || 300) / 60) }} min</span>
                    <Lock v-if="!isEnrolled" class="w-3.5 h-3.5 text-slate-600" />
                    <Check v-else-if="les.is_completed" class="w-3.5 h-3.5 text-emerald-400" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Live Sessions Section -->
        <div v-if="liveSessions.length > 0">
          <h2 class="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Video class="w-5 h-5 text-cyan-400" /> Scheduled Live Classes
          </h2>
          <div class="space-y-3">
            <div 
              v-for="s in liveSessions" 
              :key="s.id"
              class="glass-panel p-4 flex items-center justify-between border border-slate-800"
            >
              <div>
                <div class="flex items-center gap-2 mb-1">
                  <span class="badge" :class="s.status === 'LIVE' ? 'badge-rose animate-pulse' : 'badge-cyan'">
                    {{ s.status === 'LIVE' ? 'LIVE NOW' : 'SCHEDULED' }}
                  </span>
                  <span class="text-xs text-slate-400">Host: {{ s.instructor_name }}</span>
                </div>
                <h4 class="font-bold text-sm text-white">{{ s.title }}</h4>
                <div class="text-xs text-slate-400 mt-1 flex items-center gap-3">
                  <span>Starts: {{ new Date(s.scheduled_start).toLocaleString() }}</span>
                  <span>{{ s.registered_count }} Registered</span>
                </div>
              </div>

              <router-link 
                v-if="isEnrolled" 
                :to="`/org/${orgSlug}/live/${s.id}`" 
                class="btn-primary text-xs py-2 px-3"
              >
                Join Classroom
              </router-link>
            </div>
          </div>
        </div>

        <!-- Reviews Section -->
        <div>
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-xl font-bold text-white flex items-center gap-2">
              <Star class="w-5 h-5 text-amber-400" /> Student Reviews &amp; Ratings
            </h2>
            <router-link :to="`/org/${orgSlug}/courses/${courseId}/reviews`" class="text-xs text-indigo-400 hover:underline">
              View All Reviews &rarr;
            </router-link>
          </div>

          <div v-if="reviewsData.reviews.length === 0" class="glass-panel p-6 text-center text-xs text-slate-500 border border-slate-800">
            No reviews yet for this course. Be the first enrolled student to review!
          </div>

          <div v-else class="space-y-3">
            <div 
              v-for="rev in reviewsData.reviews.slice(0, 3)" 
              :key="rev.id"
              class="glass-panel p-4 border border-slate-800"
            >
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 rounded-full bg-slate-800 text-[10px] font-bold text-indigo-400 flex items-center justify-center">
                    {{ rev.student_name[0] }}
                  </div>
                  <span class="text-xs font-semibold text-white">{{ rev.student_name }}</span>
                </div>
                <div class="flex items-center gap-0.5 text-amber-400">
                  <Star v-for="i in rev.rating" :key="i" class="w-3 h-3 fill-amber-400" />
                </div>
              </div>
              <p class="text-xs text-slate-300 leading-relaxed">{{ rev.review_text }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Sticky Enrollment Action Card -->
      <div class="glass-panel p-6 border border-slate-800 shadow-2xl sticky top-20">
        <div class="aspect-video rounded-xl overflow-hidden bg-slate-900 mb-5 relative group">
          <img 
            :src="course.thumbnail_url || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80'" 
            :alt="course.title"
            class="w-full h-full object-cover"
          />
          <div class="absolute inset-0 bg-slate-950/40 flex items-center justify-center">
            <div class="w-12 h-12 rounded-full bg-white/20 backdrop-blur-md flex items-center justify-center border border-white/40 shadow-lg">
              <PlayCircle class="w-6 h-6 text-white" />
            </div>
          </div>
        </div>

        <div class="flex items-baseline justify-between mb-4">
          <div class="text-2xl font-extrabold text-white">
            {{ course.is_free ? 'Free' : course.price_display }}
          </div>
          <span class="text-xs text-slate-400 font-medium">Lifetime Access</span>
        </div>

        <div v-if="isEnrolled" class="space-y-3">
          <div class="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center gap-2">
            <CheckCircle class="w-4 h-4 text-emerald-400" /> You are enrolled in this course!
          </div>
          <button @click="startLearning" class="btn-primary w-full justify-center py-3 text-sm">
            Resume Learning <ArrowRight class="w-4 h-4" />
          </button>
        </div>

        <div v-else>
          <button 
            @click="handleEnrollOrPurchase" 
            :disabled="actionLoading" 
            class="btn-primary w-full justify-center py-3 text-sm font-bold shadow-lg shadow-indigo-500/30 mb-3"
          >
            <span v-if="actionLoading">Processing Request...</span>
            <span v-else-if="course.is_free">Enroll Now — Free</span>
            <span v-else>Buy Course — {{ course.price_display }}</span>
          </button>
          <div class="text-[11px] text-slate-500 text-center flex items-center justify-center gap-1.5">
            <Shield class="w-3.5 h-3.5 text-indigo-400" /> Verified Cryptographic Certificate Included
          </div>
        </div>

        <!-- Course Highlights List -->
        <div class="mt-6 pt-5 border-t border-slate-800 space-y-2.5 text-xs text-slate-300">
          <div class="flex items-center gap-2">
            <PlayCircle class="w-4 h-4 text-indigo-400" />
            <span>{{ course.total_lessons }} Structured Lectures &amp; Modules</span>
          </div>
          <div class="flex items-center gap-2">
            <Award class="w-4 h-4 text-amber-400" />
            <span>Graded Projects &amp; Automated Quizzes</span>
          </div>
          <div class="flex items-center gap-2">
            <Video class="w-4 h-4 text-cyan-400" />
            <span>Live Virtual Classrooms &amp; Workshops</span>
          </div>
          <div class="flex items-center gap-2">
            <MessageSquare class="w-4 h-4 text-emerald-400" />
            <span>Collaborative Student Discussion Forum</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
