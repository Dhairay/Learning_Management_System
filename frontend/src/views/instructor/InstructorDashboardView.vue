<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { courseApi } from '../../api/courseApi';
import { assessmentApi } from '../../api/assessmentApi';
import { liveSessionApi } from '../../api/liveSessionApi';
import { useToast } from '../../composables/useToast';
import type { Course, AssignmentSubmission, LiveSession } from '../../types';
import { 
  Award, Plus, BookOpen, Video, CheckCircle2, Clock, 
  Send, User, FileText, Check, Calendar, X, Layers,
  Search, Filter, Sparkles, AlertCircle, PlayCircle, Eye,
  Sliders, MessageSquare, ExternalLink
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const orgSlug = ref(route.params.orgSlug as string || 'acme-academy');

const myCourses = ref<Course[]>([]);
const submissions = ref<AssignmentSubmission[]>([]);
const liveSessions = ref<LiveSession[]>([]);
const activeTab = ref<'courses' | 'submissions' | 'live'>('courses');

// Course search & filter
const courseSearchQuery = ref('');
const courseStatusFilter = ref<'ALL' | 'PUBLISHED' | 'DRAFT'>('ALL');

// Course creation modal
const showCreateCourse = ref(false);
const newTitle = ref('');
const newDesc = ref('');
const newThumbnailUrl = ref('');
const newLevel = ref<'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED'>('INTERMEDIATE');
const newIsFree = ref(true);
const newPrice = ref(49.00);
const creatingCourse = ref(false);

// Syllabus & Curriculum Builder
const showCurriculumModal = ref(false);
const activeCurriculumCourse = ref<Course | null>(null);
const loadingCurriculum = ref(false);
const newSectionTitle = ref('');
const addingSection = ref(false);
const activeAddingLessonSectionId = ref<string | null>(null);
const newLessonTitle = ref('');
const newLessonType = ref<'VIDEO' | 'ARTICLE' | 'QUIZ' | 'ASSIGNMENT'>('VIDEO');
const newLessonDurationMinutes = ref(15);
const newLessonContent = ref('');
const addingLesson = ref(false);

// Schedule live session modal
const showScheduleModal = ref(false);
const selectedCourseIdForLive = ref('');
const liveTitle = ref('');
const liveStart = ref('');
const liveEnd = ref('');
const schedulingSession = ref(false);

// Grade modal
const selectedSubmission = ref<AssignmentSubmission | null>(null);
const gradeScore = ref(90);
const gradeFeedback = ref('Great architecture writeup!');
const grading = ref(false);

const loading = ref(true);

// Computed KPIs
const totalCourses = computed(() => myCourses.value.length);
const publishedCourses = computed(() => myCourses.value.filter(c => c.status === 'PUBLISHED').length);
const totalLessons = computed(() => myCourses.value.reduce((acc, c) => acc + (c.total_lessons || 0), 0));
const pendingSubmissions = computed(() => submissions.value.filter(s => s.status !== 'GRADED').length);

const filteredCourses = computed(() => {
  return myCourses.value.filter(c => {
    const matchesSearch = !courseSearchQuery.value || 
      c.title.toLowerCase().includes(courseSearchQuery.value.toLowerCase()) ||
      (c.short_description && c.short_description.toLowerCase().includes(courseSearchQuery.value.toLowerCase()));
    const matchesStatus = courseStatusFilter.value === 'ALL' || c.status === courseStatusFilter.value;
    return matchesSearch && matchesStatus;
  });
});

async function loadData() {
  loading.value = true;
  try {
    const courses = await courseApi.getCourses();
    myCourses.value = courses;

    if (courses.length > 0) {
      if (!selectedCourseIdForLive.value) {
        selectedCourseIdForLive.value = courses[0].id;
      }
      // Fetch submissions for first course
      const subs = await assessmentApi.getInstructorSubmissions(courses[0].id).catch(() => []);
      submissions.value = subs;

      // Fetch live sessions
      const sessions = await liveSessionApi.getSessions(courses[0].id).catch(() => []);
      liveSessions.value = sessions;
    }
  } catch (e: any) {
    toast.error('Failed to load instructor studio data', e.message);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});

async function createCourse() {
  if (!newTitle.value.trim()) {
    toast.warning('Please enter a course title');
    return;
  }
  creatingCourse.value = true;
  try {
    const created = await courseApi.createCourse({
      title: newTitle.value.trim(),
      description: newDesc.value.trim(),
      level: newLevel.value,
      is_free: newIsFree.value,
      price_amount: newPrice.value,
    });
    showCreateCourse.value = false;
    newTitle.value = '';
    newDesc.value = '';
    newThumbnailUrl.value = '';
    toast.success('Course draft created successfully!', 'Now add your syllabus modules and lectures.');
    await loadData();
    await openCurriculumBuilder(created);
  } catch (err: any) {
    toast.error('Failed to author course', err.message);
  } finally {
    creatingCourse.value = false;
  }
}

async function openCurriculumBuilder(course: Course) {
  showCurriculumModal.value = true;
  loadingCurriculum.value = true;
  try {
    const fullCourse = await courseApi.getCourse(course.id);
    activeCurriculumCourse.value = fullCourse;
  } catch (err: any) {
    toast.error('Failed to load syllabus', err.message);
  } finally {
    loadingCurriculum.value = false;
  }
}

async function addSection() {
  if (!activeCurriculumCourse.value || !newSectionTitle.value.trim()) return;
  addingSection.value = true;
  try {
    await courseApi.createSection(activeCurriculumCourse.value.id, {
      title: newSectionTitle.value.trim()
    });
    const addedTitle = newSectionTitle.value.trim();
    newSectionTitle.value = '';
    toast.success('Module section created!', `"${addedTitle}" added to curriculum.`);
    const fullCourse = await courseApi.getCourse(activeCurriculumCourse.value.id);
    activeCurriculumCourse.value = fullCourse;
    await loadData();
  } catch (err: any) {
    toast.error('Failed to add module section', err.message);
  } finally {
    addingSection.value = false;
  }
}

function startAddLesson(sectionId: string) {
  activeAddingLessonSectionId.value = sectionId;
  newLessonTitle.value = '';
  newLessonContent.value = '';
  newLessonDurationMinutes.value = 15;
  newLessonType.value = 'VIDEO';
}

async function addLesson(sectionId: string) {
  if (!newLessonTitle.value.trim()) {
    toast.warning('Please enter a lesson title');
    return;
  }
  addingLesson.value = true;
  try {
    await courseApi.createLesson(sectionId, {
      title: newLessonTitle.value.trim(),
      lesson_type: newLessonType.value,
      duration_seconds: (newLessonDurationMinutes.value || 15) * 60,
      content_text: newLessonContent.value
    });
    toast.success('Lesson saved to curriculum!', `"${newLessonTitle.value.trim()}" is now available.`);
    newLessonTitle.value = '';
    newLessonContent.value = '';
    newLessonDurationMinutes.value = 15;
    activeAddingLessonSectionId.value = null;
    
    if (activeCurriculumCourse.value) {
      const fullCourse = await courseApi.getCourse(activeCurriculumCourse.value.id);
      activeCurriculumCourse.value = fullCourse;
    }
    await loadData();
  } catch (err: any) {
    toast.error('Failed to add lesson', err.message);
  } finally {
    addingLesson.value = false;
  }
}

async function publishCourse(cId: string) {
  try {
    await courseApi.publishCourse(cId);
    toast.success('Course is now LIVE!', 'Published to organization catalog and available for student enrollment.');
    await loadData();
  } catch (err: any) {
    toast.error('Failed to publish course', err.message);
  }
}

async function scheduleSession() {
  if (!liveTitle.value.trim() || !selectedCourseIdForLive.value) {
    toast.warning('Please enter a session title and select a course');
    return;
  }
  schedulingSession.value = true;
  try {
    await liveSessionApi.createSession(selectedCourseIdForLive.value, {
      title: liveTitle.value.trim(),
      scheduled_start: liveStart.value || new Date().toISOString(),
      scheduled_end: liveEnd.value || new Date(Date.now() + 3600000).toISOString(),
      provider: 'JITSI'
    });
    toast.success('Live Virtual Workshop scheduled!', 'Enrolled students will be notified to register.');
    showScheduleModal.value = false;
    liveTitle.value = '';
    await loadData();
  } catch (err: any) {
    toast.error('Failed to schedule session', err.message);
  } finally {
    schedulingSession.value = false;
  }
}

async function submitGrade() {
  if (!selectedSubmission.value) return;
  grading.value = true;
  try {
    await assessmentApi.gradeAssignment(selectedSubmission.value.id, {
      score: gradeScore.value,
      feedback: gradeFeedback.value
    });
    toast.success('Grade recorded successfully!', `Student received ${gradeScore.value} points.`);
    selectedSubmission.value = null;
    await loadData();
  } catch (err: any) {
    toast.error('Failed to grade submission', err.message);
  } finally {
    grading.value = false;
  }
}
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Studio Header Banner -->
    <div class="glass-panel p-6 sm:p-8 border border-slate-800 relative overflow-hidden bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 shadow-xl">
      <div class="relative z-10 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 text-amber-500 dark:text-amber-400 text-xs font-bold mb-3 border border-amber-500/20">
            <Award class="w-3.5 h-3.5" /> Instructor Studio &bull; Academic Portal
          </div>
          <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
            Curriculum Authoring &amp; Student Grading
          </h1>
          <p class="text-xs sm:text-sm text-slate-400 mt-1 max-w-xl">
            Design certified video masterclasses, organize multi-week modules, evaluate student code submissions, and run interactive workshops.
          </p>
        </div>

        <div class="flex flex-wrap items-center gap-3">
          <button 
            @click="showScheduleModal = true" 
            class="btn-secondary text-xs py-2.5 px-4 font-semibold shadow-sm flex items-center gap-2"
          >
            <Video class="w-4 h-4 text-cyan-500" />
            <span>Schedule Live Workshop</span>
          </button>
          <button 
            @click="showCreateCourse = true" 
            class="btn-primary text-xs py-2.5 px-4 font-bold shadow-lg flex items-center gap-2"
          >
            <Plus class="w-4 h-4" />
            <span>Author New Course</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Executive KPI Metric Cards -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- KPI 1 -->
      <div class="glass-panel p-5 border border-slate-800 flex items-center justify-between">
        <div>
          <div class="text-xs font-semibold text-slate-400 mb-1">Authored Courses</div>
          <div class="text-2xl font-extrabold text-white">{{ totalCourses }}</div>
          <div class="text-[11px] text-emerald-500 dark:text-emerald-400 font-medium mt-1 flex items-center gap-1">
            <CheckCircle2 class="w-3 h-3" /> {{ publishedCourses }} Published
          </div>
        </div>
        <div class="w-12 h-12 rounded-xl bg-indigo-500/10 text-indigo-500 flex items-center justify-center border border-indigo-500/20">
          <BookOpen class="w-6 h-6" />
        </div>
      </div>

      <!-- KPI 2 -->
      <div class="glass-panel p-5 border border-slate-800 flex items-center justify-between">
        <div>
          <div class="text-xs font-semibold text-slate-400 mb-1">Curriculum Lessons</div>
          <div class="text-2xl font-extrabold text-white">{{ totalLessons }}</div>
          <div class="text-[11px] text-slate-400 mt-1">
            Across all course syllabi
          </div>
        </div>
        <div class="w-12 h-12 rounded-xl bg-cyan-500/10 text-cyan-500 flex items-center justify-center border border-cyan-500/20">
          <Layers class="w-6 h-6" />
        </div>
      </div>

      <!-- KPI 3 -->
      <div class="glass-panel p-5 border border-slate-800 flex items-center justify-between">
        <div>
          <div class="text-xs font-semibold text-slate-400 mb-1">Pending Grading</div>
          <div class="text-2xl font-extrabold text-white">{{ pendingSubmissions }}</div>
          <div class="text-[11px] font-medium mt-1" :class="pendingSubmissions > 0 ? 'text-amber-500 dark:text-amber-400' : 'text-slate-400'">
            {{ pendingSubmissions > 0 ? 'Needs instructor review' : 'All assignments graded' }}
          </div>
        </div>
        <div class="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-500 flex items-center justify-center border border-amber-500/20">
          <FileText class="w-6 h-6" />
        </div>
      </div>

      <!-- KPI 4 -->
      <div class="glass-panel p-5 border border-slate-800 flex items-center justify-between">
        <div>
          <div class="text-xs font-semibold text-slate-400 mb-1">Live Workshops</div>
          <div class="text-2xl font-extrabold text-white">{{ liveSessions.length }}</div>
          <div class="text-[11px] text-slate-400 mt-1">
            Virtual classroom sessions
          </div>
        </div>
        <div class="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center border border-emerald-500/20">
          <Video class="w-6 h-6" />
        </div>
      </div>
    </div>

    <!-- Navigation Tabs & Search Toolbar -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800/80 pb-3">
      <div class="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs font-bold">
        <button 
          @click="activeTab = 'courses'"
          class="py-2 px-4 rounded-lg transition flex items-center gap-2 shrink-0"
          :class="activeTab === 'courses' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' : 'text-slate-400 hover:text-white hover:bg-slate-900'"
        >
          <BookOpen class="w-4 h-4" />
          <span>My Courses</span>
          <span class="text-[10px] px-1.5 py-0.2 rounded-full" :class="activeTab === 'courses' ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-400'">
            {{ myCourses.length }}
          </span>
        </button>

        <button 
          @click="activeTab = 'submissions'"
          class="py-2 px-4 rounded-lg transition flex items-center gap-2 shrink-0"
          :class="activeTab === 'submissions' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' : 'text-slate-400 hover:text-white hover:bg-slate-900'"
        >
          <FileText class="w-4 h-4" />
          <span>Assignment Submissions</span>
          <span class="text-[10px] px-1.5 py-0.2 rounded-full" :class="activeTab === 'submissions' ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-400'">
            {{ submissions.length }}
          </span>
        </button>

        <button 
          @click="activeTab = 'live'"
          class="py-2 px-4 rounded-lg transition flex items-center gap-2 shrink-0"
          :class="activeTab === 'live' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' : 'text-slate-400 hover:text-white hover:bg-slate-900'"
        >
          <Video class="w-4 h-4" />
          <span>Live Workshops</span>
          <span class="text-[10px] px-1.5 py-0.2 rounded-full" :class="activeTab === 'live' ? 'bg-white/20 text-white' : 'bg-slate-800 text-slate-400'">
            {{ liveSessions.length }}
          </span>
        </button>
      </div>

      <!-- Quick Search / Filter when on Courses tab -->
      <div v-if="activeTab === 'courses'" class="flex items-center gap-2">
        <div class="relative w-48 sm:w-64">
          <Search class="w-4 h-4 text-slate-400 absolute left-3 top-2.5 pointer-events-none" />
          <input 
            v-model="courseSearchQuery" 
            type="text" 
            placeholder="Search authored courses..." 
            class="input-field text-xs pl-9 py-2"
          />
        </div>
        <select v-model="courseStatusFilter" class="input-field text-xs py-2 w-32">
          <option value="ALL">All Status</option>
          <option value="PUBLISHED">Published</option>
          <option value="DRAFT">Draft</option>
        </select>
      </div>
    </div>

    <!-- Tab 1: Authored Courses -->
    <div v-if="activeTab === 'courses'" class="space-y-4">
      <div v-if="loading" class="text-center py-20 text-slate-500">
        <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
        Loading authored courses...
      </div>

      <div v-else-if="filteredCourses.length === 0" class="glass-panel p-12 text-center border border-slate-800 rounded-2xl">
        <BookOpen class="w-12 h-12 text-slate-500 mx-auto mb-3" />
        <h3 class="text-base font-bold text-white mb-1">No courses match your filter</h3>
        <p class="text-xs text-slate-400 mb-4">Try clearing your search query or author a brand new masterclass.</p>
        <button @click="showCreateCourse = true" class="btn-primary text-xs py-2 px-4">
          <Plus class="w-4 h-4" /> Author New Course
        </button>
      </div>

      <div v-else class="grid gap-4">
        <div 
          v-for="c in filteredCourses" 
          :key="c.id"
          class="glass-panel p-5 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-5 hover:border-slate-700 transition"
        >
          <!-- Left: Thumbnail & Details -->
          <div class="flex items-start gap-4 flex-1">
            <div class="w-24 h-16 sm:w-32 sm:h-20 rounded-xl overflow-hidden bg-slate-800 shrink-0 relative border border-slate-700">
              <img 
                :src="c.thumbnail_url || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80'" 
                :alt="c.title"
                class="w-full h-full object-cover"
              />
              <div class="absolute bottom-1 right-1">
                <span class="badge text-[9px] px-1.5 py-0.5" :class="c.is_free ? 'badge-emerald' : 'badge-amber'">
                  {{ c.is_free ? 'Free' : c.price_display }}
                </span>
              </div>
            </div>

            <div class="flex-1 min-w-0">
              <div class="flex flex-wrap items-center gap-2 mb-1.5">
                <span class="badge" :class="c.status === 'PUBLISHED' ? 'badge-emerald' : 'badge-amber'">
                  <span class="w-1.5 h-1.5 rounded-full" :class="c.status === 'PUBLISHED' ? 'bg-emerald-500' : 'bg-amber-500'"></span>
                  {{ c.status }}
                </span>
                <span class="badge badge-indigo text-[10px]">{{ c.level }}</span>
                <span class="text-xs text-slate-400 font-medium">
                  {{ c.category?.name || 'Computer Science' }}
                </span>
              </div>

              <h3 class="text-base font-bold text-white truncate mb-1">
                {{ c.title }}
              </h3>

              <p class="text-xs text-slate-400 line-clamp-1 leading-relaxed mb-2">
                {{ c.short_description || c.description }}
              </p>

              <div class="flex items-center gap-4 text-xs text-slate-400">
                <span class="flex items-center gap-1">
                  <Layers class="w-3.5 h-3.5 text-indigo-400" />
                  <strong>{{ c.total_lessons || 0 }}</strong> Lessons
                </span>
                <span class="flex items-center gap-1">
                  <Clock class="w-3.5 h-3.5 text-cyan-400" />
                  {{ Math.round((c.total_duration_seconds || 0) / 60) }} Mins
                </span>
              </div>
            </div>
          </div>

          <!-- Right: Actions -->
          <div class="flex flex-wrap items-center gap-2 shrink-0 md:justify-end pt-2 md:pt-0 border-t md:border-t-0 border-slate-800/80">
            <button 
              @click="openCurriculumBuilder(c)"
              class="btn-primary text-xs py-2 px-3.5 flex items-center gap-1.5 shadow-md shadow-indigo-600/20"
            >
              <Layers class="w-3.5 h-3.5" />
              <span>Manage Syllabus ({{ c.total_lessons || 0 }})</span>
            </button>

            <button 
              v-if="c.status === 'DRAFT'"
              @click="publishCourse(c.id)"
              class="btn-secondary text-xs py-2 px-3 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 hover:bg-emerald-500/10 flex items-center gap-1"
            >
              <CheckCircle2 class="w-3.5 h-3.5" />
              <span>Publish Live</span>
            </button>

            <router-link 
              :to="`/org/${orgSlug}/courses/${c.id}`" 
              class="btn-secondary text-xs py-2 px-3 flex items-center gap-1"
              title="Preview public course syllabus"
            >
              <Eye class="w-3.5 h-3.5" />
              <span>Preview</span>
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Tab 2: Project Submissions to Grade -->
    <div v-if="activeTab === 'submissions'" class="space-y-4">
      <div v-if="submissions.length === 0" class="glass-panel p-12 text-center text-xs text-slate-400 border border-slate-800 rounded-2xl">
        <CheckCircle2 class="w-12 h-12 text-emerald-500 mx-auto mb-3" />
        <h3 class="text-base font-bold text-white mb-1">All Submissions Evaluated</h3>
        <p class="text-slate-400">There are currently no student capstone projects awaiting grading.</p>
      </div>

      <div 
        v-for="sub in submissions" 
        :key="sub.id"
        class="glass-panel p-5 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:border-slate-700 transition"
      >
        <div class="flex-1">
          <div class="flex items-center gap-2 mb-1.5">
            <span class="badge" :class="sub.status === 'GRADED' ? 'badge-emerald' : 'badge-amber'">
              {{ sub.status }}
            </span>
            <span class="text-xs font-semibold text-white flex items-center gap-1">
              <User class="w-3.5 h-3.5 text-slate-400" />
              {{ sub.student_name || 'Enrolled Student' }}
            </span>
            <span class="text-[11px] text-slate-400">
              &bull; Submitted {{ new Date(sub.submitted_at || Date.now()).toLocaleDateString() }}
            </span>
          </div>

          <div class="p-3 rounded-lg bg-slate-900 border border-slate-800/80 my-2">
            <div class="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-1">Student Solution Text</div>
            <p class="text-xs text-slate-200 whitespace-pre-line leading-relaxed">
              {{ sub.content_text }}
            </p>
          </div>

          <div v-if="sub.grade" class="text-xs font-semibold text-emerald-600 dark:text-emerald-400 flex items-center gap-1.5 mt-2">
            <Check class="w-4 h-4" />
            <span>Awarded: <strong>{{ sub.grade.score }} / 100 Points</strong> &bull; Feedback: "{{ sub.grade.feedback }}"</span>
          </div>
        </div>

        <button 
          @click="selectedSubmission = sub; gradeScore = sub.grade?.score || 90; gradeFeedback = sub.grade?.feedback || 'Great architecture writeup!'" 
          class="btn-primary text-xs py-2 px-4 shrink-0 font-semibold"
        >
          {{ sub.status === 'GRADED' ? 'Revise Evaluation' : 'Grade Submission' }}
        </button>
      </div>
    </div>

    <!-- Tab 3: Live Virtual Sessions -->
    <div v-if="activeTab === 'live'" class="space-y-4">
      <div v-if="liveSessions.length === 0" class="glass-panel p-12 text-center text-xs text-slate-400 border border-slate-800 rounded-2xl">
        <Video class="w-12 h-12 text-slate-500 mx-auto mb-3" />
        <h3 class="text-base font-bold text-white mb-1">No Live Virtual Workshops Scheduled</h3>
        <p class="text-slate-400 mb-4">Host real-time live masterclasses using the integrated classroom engine.</p>
        <button @click="showScheduleModal = true" class="btn-primary text-xs py-2 px-4">
          <Plus class="w-4 h-4" /> Schedule First Live Class
        </button>
      </div>

      <div 
        v-for="s in liveSessions" 
        :key="s.id"
        class="glass-panel p-5 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 hover:border-slate-700 transition"
      >
        <div>
          <div class="flex items-center gap-2 mb-1.5">
            <span class="badge" :class="s.status === 'LIVE' ? 'badge-rose' : 'badge-cyan'">
              <span v-if="s.status === 'LIVE'" class="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse"></span>
              {{ s.status }}
            </span>
            <span class="badge badge-indigo text-[10px]">{{ s.provider }}</span>
            <span class="text-xs text-slate-400 flex items-center gap-1">
              <Calendar class="w-3.5 h-3.5" />
              {{ new Date(s.scheduled_start).toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' }) }}
            </span>
          </div>

          <h4 class="text-base font-bold text-white mb-1">{{ s.title }}</h4>
          <div class="text-xs text-slate-400 flex items-center gap-2">
            <span><strong>{{ s.registered_count }}</strong> Learners Registered</span>
            <span>&bull;</span>
            <span>Duration: ~60 mins</span>
          </div>
        </div>

        <router-link 
          :to="`/org/${orgSlug}/live/${s.id}`" 
          class="btn-primary text-xs py-2 px-4 font-bold flex items-center gap-1.5"
        >
          <Video class="w-3.5 h-3.5" />
          <span>Enter Live Room</span>
          <ExternalLink class="w-3 h-3 ml-0.5 opacity-80" />
        </router-link>
      </div>
    </div>

    <!-- Modal 1: Create Course -->
    <Teleport to="body">
      <div v-if="showCreateCourse" class="modal-backdrop-wrap" @click.self="showCreateCourse = false">
        <div class="modal-box max-w-lg space-y-4 animate-fade-in">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="text-lg font-bold text-white flex items-center gap-2">
              <BookOpen class="w-5 h-5 text-indigo-500" />
              Author New Masterclass Course
            </h3>
            <button @click="showCreateCourse = false" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">Course Title</label>
            <input 
              v-model="newTitle" 
              type="text" 
              placeholder="e.g. Distributed Systems & Cloud Architecture Masterclass" 
              class="input-field text-sm" 
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">Description &amp; Syllabus Overview</label>
            <textarea 
              v-model="newDesc" 
              rows="3" 
              placeholder="What students will learn, architecture patterns covered, prerequisites..." 
              class="input-field text-sm"
            ></textarea>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1.5">Difficulty Level</label>
              <select v-model="newLevel" class="input-field text-sm">
                <option value="BEGINNER">Beginner</option>
                <option value="INTERMEDIATE">Intermediate</option>
                <option value="ADVANCED">Advanced</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1.5">Access Model</label>
              <select v-model="newIsFree" class="input-field text-sm">
                <option :value="true">Free Enrollment</option>
                <option :value="false">Commercial Paid Course</option>
              </select>
            </div>
          </div>

          <div v-if="!newIsFree">
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">Price Amount (USD)</label>
            <div class="relative">
              <span class="absolute left-3 top-2.5 text-xs font-bold text-slate-400">$</span>
              <input v-model="newPrice" type="number" step="0.01" class="input-field text-sm pl-7" />
            </div>
          </div>

          <div class="flex justify-end gap-2.5 pt-3 border-t border-slate-800">
            <button @click="showCreateCourse = false" class="btn-secondary text-xs px-4 py-2 font-semibold">
              Cancel
            </button>
            <button 
              @click="createCourse" 
              :disabled="creatingCourse || !newTitle.trim()"
              class="btn-primary text-xs px-5 py-2 font-bold flex items-center gap-1.5"
            >
              <Plus class="w-3.5 h-3.5" />
              <span>{{ creatingCourse ? 'Authoring...' : 'Create Draft & Build Syllabus' }}</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal 2: Curriculum & Syllabus Builder -->
    <Teleport to="body">
      <div v-if="showCurriculumModal" class="modal-backdrop-wrap" @click.self="showCurriculumModal = false">
        <div class="modal-box max-w-2xl space-y-5 animate-fade-in">
          <!-- Header -->
          <div class="flex items-start justify-between pb-3 border-b border-slate-800">
            <div>
              <div class="flex items-center gap-2 mb-1">
                <span class="badge" :class="activeCurriculumCourse?.status === 'PUBLISHED' ? 'badge-emerald' : 'badge-amber'">
                  {{ activeCurriculumCourse?.status }}
                </span>
                <span class="text-xs text-slate-400 font-medium">{{ activeCurriculumCourse?.level }}</span>
                <span class="text-xs font-bold text-slate-300">{{ activeCurriculumCourse?.is_free ? 'Free' : activeCurriculumCourse?.price_display }}</span>
              </div>
              <h3 class="text-lg font-bold text-white flex items-center gap-2">
                <BookOpen class="w-5 h-5 text-indigo-500" />
                {{ activeCurriculumCourse?.title }} &mdash; Syllabus Builder
              </h3>
              <p class="text-xs text-slate-400 mt-0.5">Author sections, chapters, video lectures, reading notes, and assignments.</p>
            </div>
            <button @click="showCurriculumModal = false" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
              <X class="w-5 h-5" />
            </button>
          </div>

          <!-- Add New Section Bar -->
          <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
            <label class="block text-xs font-bold text-white uppercase tracking-wider">Add New Course Module / Section</label>
            <div class="flex gap-2">
              <input 
                v-model="newSectionTitle" 
                @keyup.enter="addSection"
                type="text" 
                placeholder="e.g. Module 1: Foundations & Architecture" 
                class="input-field text-xs flex-1" 
              />
              <button 
                @click="addSection" 
                :disabled="addingSection || !newSectionTitle.trim()"
                class="btn-primary text-xs px-4 py-2 shrink-0 flex items-center gap-1.5 font-semibold"
              >
                <Plus class="w-3.5 h-3.5" />
                {{ addingSection ? 'Adding...' : 'Add Section' }}
              </button>
            </div>
          </div>

          <!-- Sections & Lessons List -->
          <div v-if="loadingCurriculum" class="text-center py-10 text-xs text-slate-400">
            <div class="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
            Loading syllabus curriculum...
          </div>
          <div v-else-if="!activeCurriculumCourse?.sections || activeCurriculumCourse.sections.length === 0" class="text-center py-12 p-6 rounded-xl border border-dashed border-slate-800 bg-slate-900/40">
            <Layers class="w-10 h-10 text-slate-500 mx-auto mb-2" />
            <h4 class="text-sm font-semibold text-white">No Syllabus Sections Yet</h4>
            <p class="text-xs text-slate-400 max-w-sm mx-auto mt-1">
              Add your first section above (for example: "Module 1: Introduction") to begin adding video lectures, quizzes, and projects.
            </p>
          </div>
          <div v-else class="space-y-4 max-h-[55vh] overflow-y-auto pr-1">
            <div 
              v-for="(sec, secIdx) in activeCurriculumCourse.sections" 
              :key="sec.id"
              class="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden"
            >
              <!-- Section Header -->
              <div class="p-3.5 px-4 bg-slate-850 border-b border-slate-800 flex items-center justify-between">
                <div class="flex items-center gap-2.5">
                  <span class="w-6 h-6 rounded-md bg-indigo-500/20 text-indigo-500 dark:text-indigo-300 text-xs font-bold flex items-center justify-center border border-indigo-500/30">
                    {{ secIdx + 1 }}
                  </span>
                  <span class="font-bold text-sm text-white">{{ sec.title }}</span>
                  <span class="text-[11px] text-slate-400">({{ sec.lessons?.length || 0 }} items)</span>
                </div>
                <button 
                  @click="startAddLesson(sec.id)" 
                  class="btn-secondary text-[11px] py-1 px-2.5 flex items-center gap-1 text-indigo-600 dark:text-indigo-300 border-indigo-500/30 hover:bg-indigo-500/10"
                >
                  <Plus class="w-3 h-3" /> Add Lesson
                </button>
              </div>

              <!-- Inline Add Lesson Form -->
              <div v-if="activeAddingLessonSectionId === sec.id" class="p-4 bg-slate-950/60 border-b border-slate-800 space-y-3 animate-fade-in">
                <div class="text-xs font-bold text-indigo-500 flex items-center gap-1">
                  <Plus class="w-3.5 h-3.5" /> New Lesson under "{{ sec.title }}"
                </div>
                <div class="grid sm:grid-cols-3 gap-3">
                  <div class="sm:col-span-2">
                    <label class="block text-[11px] font-semibold text-slate-300 mb-1">Lesson Title</label>
                    <input v-model="newLessonTitle" type="text" placeholder="e.g. Distributed Consensus & Raft Protocol" class="input-field text-xs" />
                  </div>
                  <div>
                    <label class="block text-[11px] font-semibold text-slate-300 mb-1">Lesson Type</label>
                    <select v-model="newLessonType" class="input-field text-xs">
                      <option value="VIDEO">Video Lecture</option>
                      <option value="ARTICLE">Article / Notes</option>
                      <option value="QUIZ">Quiz Assessment</option>
                      <option value="ASSIGNMENT">Capstone Project</option>
                    </select>
                  </div>
                </div>
                <div class="grid sm:grid-cols-3 gap-3">
                  <div>
                    <label class="block text-[11px] font-semibold text-slate-300 mb-1">Duration (Minutes)</label>
                    <input v-model="newLessonDurationMinutes" type="number" min="1" max="600" class="input-field text-xs" />
                  </div>
                  <div class="sm:col-span-2">
                    <label class="block text-[11px] font-semibold text-slate-300 mb-1">Summary / Lecture Notes (Optional)</label>
                    <input v-model="newLessonContent" type="text" placeholder="Key architecture takeaways or video outline..." class="input-field text-xs" />
                  </div>
                </div>
                <div class="flex justify-end gap-2 pt-1">
                  <button @click="activeAddingLessonSectionId = null" class="btn-secondary text-[11px] px-3 py-1.5 font-semibold">
                    Cancel
                  </button>
                  <button 
                    @click="addLesson(sec.id)" 
                    :disabled="addingLesson || !newLessonTitle.trim()" 
                    class="btn-primary text-[11px] px-3.5 py-1.5 font-bold"
                  >
                    {{ addingLesson ? 'Saving...' : 'Save Lesson' }}
                  </button>
                </div>
              </div>

              <!-- Lessons in this Section -->
              <div v-if="!sec.lessons || sec.lessons.length === 0" class="p-3 text-center text-xs text-slate-400 italic">
                No lessons yet in this section. Click "+ Add Lesson" to author content.
              </div>
              <div v-else class="divide-y divide-slate-800/40">
                <div 
                  v-for="(les, lIdx) in sec.lessons" 
                  :key="les.id"
                  class="p-3 px-4 flex items-center justify-between text-xs hover:bg-slate-800/40 transition"
                >
                  <div class="flex items-center gap-3">
                    <span 
                      class="w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold"
                      :class="{
                        'bg-indigo-500/10 text-indigo-500 border border-indigo-500/25': les.lesson_type === 'VIDEO',
                        'bg-cyan-500/10 text-cyan-500 border border-cyan-500/25': les.lesson_type === 'ARTICLE',
                        'bg-amber-500/10 text-amber-500 border border-amber-500/25': les.lesson_type === 'QUIZ',
                        'bg-rose-500/10 text-rose-500 border border-rose-500/25': les.lesson_type === 'ASSIGNMENT',
                      }"
                    >
                      {{ lIdx + 1 }}
                    </span>
                    <div>
                      <div class="font-bold text-white">{{ les.title }}</div>
                      <div class="text-[11px] text-slate-400">
                        {{ les.lesson_type }} &bull; {{ Math.round(les.duration_seconds / 60) }} Mins
                      </div>
                    </div>
                  </div>

                  <span class="text-[11px] text-slate-400">
                    {{ les.is_required ? 'Required for Cert' : 'Optional' }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="flex items-center justify-between pt-3 border-t border-slate-800">
            <span class="text-xs text-slate-400">
              Total Syllabus: <strong>{{ activeCurriculumCourse?.total_lessons || 0 }} lessons</strong>
            </span>
            <button @click="showCurriculumModal = false" class="btn-primary text-xs px-4 py-2 font-semibold">
              Done Editing Syllabus
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal 3: Grade Submission -->
    <Teleport to="body">
      <div v-if="selectedSubmission" class="modal-backdrop-wrap" @click.self="selectedSubmission = null">
        <div class="modal-box max-w-md space-y-4 animate-fade-in">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="text-lg font-bold text-white flex items-center gap-2">
              <Award class="w-5 h-5 text-indigo-500" />
              Evaluate Student Submission
            </h3>
            <button @click="selectedSubmission = null" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div class="p-3 rounded-lg bg-slate-900 border border-slate-800">
            <div class="text-[11px] font-semibold text-slate-400 uppercase tracking-wide mb-1">Student Answer</div>
            <p class="text-xs text-slate-200 italic whitespace-pre-line leading-relaxed">
              "{{ selectedSubmission.content_text }}"
            </p>
          </div>

          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="text-xs font-semibold text-slate-300">Grade Score</label>
              <span class="text-xs font-bold text-indigo-400">{{ gradeScore }} / 100</span>
            </div>
            <input 
              v-model.number="gradeScore" 
              type="range" 
              min="0" 
              max="100" 
              class="w-full accent-indigo-500 cursor-pointer mb-2" 
            />
            <input 
              v-model.number="gradeScore" 
              type="number" 
              min="0" 
              max="100" 
              class="input-field text-sm" 
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">Instructor Feedback</label>
            <textarea 
              v-model="gradeFeedback" 
              rows="3" 
              placeholder="Provide constructive technical guidance..." 
              class="input-field text-sm"
            ></textarea>
          </div>

          <div class="flex justify-end gap-2.5 pt-3 border-t border-slate-800">
            <button @click="selectedSubmission = null" class="btn-secondary text-xs px-4 py-2 font-semibold">
              Cancel
            </button>
            <button 
              @click="submitGrade" 
              :disabled="grading"
              class="btn-primary text-xs px-5 py-2 font-bold flex items-center gap-1.5"
            >
              <Check class="w-3.5 h-3.5" />
              <span>{{ grading ? 'Recording...' : 'Save & Issue Grade' }}</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal 4: Schedule Live Class -->
    <Teleport to="body">
      <div v-if="showScheduleModal" class="modal-backdrop-wrap" @click.self="showScheduleModal = false">
        <div class="modal-box max-w-md space-y-4 animate-fade-in">
          <div class="flex items-center justify-between pb-3 border-b border-slate-800">
            <h3 class="text-lg font-bold text-white flex items-center gap-2">
              <Video class="w-5 h-5 text-cyan-500" />
              Schedule Live Virtual Workshop
            </h3>
            <button @click="showScheduleModal = false" class="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">Workshop Topic / Title</label>
            <input 
              v-model="liveTitle" 
              type="text" 
              placeholder="e.g. Multi-Region Cassandra Architecture Q&A" 
              class="input-field text-sm" 
            />
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-300 mb-1.5">Target Course</label>
            <select v-model="selectedCourseIdForLive" class="input-field text-sm">
              <option v-for="c in myCourses" :key="c.id" :value="c.id">{{ c.title }}</option>
            </select>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1.5">Start Date &amp; Time</label>
              <input v-model="liveStart" type="datetime-local" class="input-field text-xs" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1.5">End Date &amp; Time</label>
              <input v-model="liveEnd" type="datetime-local" class="input-field text-xs" />
            </div>
          </div>

          <div class="p-3 rounded-lg bg-indigo-500/10 border border-indigo-500/20 text-xs text-indigo-400">
            Integrated with secure classroom adapter (Jitsi Meet). Students can join in 1 click from their course hub.
          </div>

          <div class="flex justify-end gap-2.5 pt-3 border-t border-slate-800">
            <button @click="showScheduleModal = false" class="btn-secondary text-xs px-4 py-2 font-semibold">
              Cancel
            </button>
            <button 
              @click="scheduleSession" 
              :disabled="schedulingSession || !liveTitle.trim()"
              class="btn-primary text-xs px-4 py-2 font-bold flex items-center gap-1.5"
            >
              <Video class="w-3.5 h-3.5" />
              <span>{{ schedulingSession ? 'Scheduling...' : 'Schedule Live Workshop' }}</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
