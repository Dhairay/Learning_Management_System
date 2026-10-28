<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { courseApi } from '../../api/courseApi';
import { assessmentApi } from '../../api/assessmentApi';
import { liveSessionApi } from '../../api/liveSessionApi';
import type { Course, AssignmentSubmission, LiveSession } from '../../types';
import { 
  Award, Plus, BookOpen, Video, CheckCircle2, Clock, 
  Send, User, FileText, Check, Calendar
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();

const orgSlug = ref(route.params.orgSlug as string || 'acme-academy');

const myCourses = ref<Course[]>([]);
const submissions = ref<AssignmentSubmission[]>([]);
const liveSessions = ref<LiveSession[]>([]);
const activeTab = ref<'courses' | 'submissions' | 'live'>('courses');

// Course creation modal
const showCreateCourse = ref(false);
const newTitle = ref('');
const newDesc = ref('');
const newLevel = ref<'BEGINNER' | 'INTERMEDIATE' | 'ADVANCED'>('INTERMEDIATE');
const newIsFree = ref(true);
const newPrice = ref(49.00);

// Schedule live session modal
const showScheduleModal = ref(false);
const selectedCourseIdForLive = ref('');
const liveTitle = ref('');
const liveStart = ref('');
const liveEnd = ref('');

// Grade modal
const selectedSubmission = ref<AssignmentSubmission | null>(null);
const gradeScore = ref(90);
const gradeFeedback = ref('Great architecture writeup!');

const loading = ref(true);

async function loadData() {
  loading.value = true;
  try {
    const courses = await courseApi.getCourses();
    myCourses.value = courses;

    if (courses.length > 0) {
      selectedCourseIdForLive.value = courses[0].id;
      // Fetch submissions for first course
      const subs = await assessmentApi.getInstructorSubmissions(courses[0].id).catch(() => []);
      submissions.value = subs;

      // Fetch live sessions
      const sessions = await liveSessionApi.getSessions(courses[0].id).catch(() => []);
      liveSessions.value = sessions;
    }
  } catch (e) {
    console.error('Failed to load instructor studio data', e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});

async function createCourse() {
  if (!newTitle.value.trim()) return;
  try {
    const created = await courseApi.createCourse({
      title: newTitle.value,
      description: newDesc.value,
      level: newLevel.value,
      is_free: newIsFree.value,
      price_amount: newPrice.value,
    });
    alert('Course authored successfully as DRAFT! You can now add curriculum.');
    showCreateCourse.value = false;
    await loadData();
  } catch (err: any) {
    alert(err.message || 'Failed to author course');
  }
}

async function publishCourse(cId: string) {
  try {
    await courseApi.publishCourse(cId);
    alert('Course published to organization catalog!');
    await loadData();
  } catch (err: any) {
    alert(err.message || 'Failed to publish course');
  }
}

async function scheduleSession() {
  if (!liveTitle.value.trim() || !selectedCourseIdForLive.value) return;
  try {
    await liveSessionApi.createSession(selectedCourseIdForLive.value, {
      title: liveTitle.value,
      scheduled_start: liveStart.value || new Date().toISOString(),
      scheduled_end: liveEnd.value || new Date(Date.now() + 3600000).toISOString(),
      provider: 'JITSI'
    });
    alert('Live Session scheduled successfully!');
    showScheduleModal.value = false;
    await loadData();
  } catch (err: any) {
    alert(err.message || 'Failed to schedule live session');
  }
}

async function submitGrade() {
  if (!selectedSubmission.value) return;
  try {
    await assessmentApi.gradeAssignment(selectedSubmission.value.id, {
      score: gradeScore.value,
      feedback: gradeFeedback.value
    });
    alert('Grade recorded successfully! Student course completion updated.');
    selectedSubmission.value = null;
    await loadData();
  } catch (err: any) {
    alert(err.message || 'Failed to grade submission');
  }
}
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
      <div>
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/10 text-amber-400 text-xs font-semibold mb-2">
          <Award class="w-3.5 h-3.5" /> Instructor Studio
        </div>
        <h1 class="text-3xl font-extrabold text-white">Course Management &amp; Grading Studio</h1>
        <p class="text-xs text-slate-400 mt-1">Author curriculum, grade student submissions, and host live workshops</p>
      </div>

      <div class="flex items-center gap-2">
        <button @click="showScheduleModal = true" class="btn-secondary text-xs">
          <Video class="w-4 h-4 text-cyan-400" /> Schedule Live Class
        </button>
        <button @click="showCreateCourse = true" class="btn-primary text-xs">
          <Plus class="w-4 h-4" /> Author New Course
        </button>
      </div>
    </div>

    <!-- Navigation Tabs -->
    <div class="flex items-center gap-2 border-b border-slate-800 text-xs font-semibold">
      <button 
        @click="activeTab = 'courses'"
        class="py-2.5 px-4 border-b-2 transition"
        :class="activeTab === 'courses' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-white'"
      >
        Authored Courses ({{ myCourses.length }})
      </button>
      <button 
        @click="activeTab = 'submissions'"
        class="py-2.5 px-4 border-b-2 transition"
        :class="activeTab === 'submissions' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-white'"
      >
        Project Submissions ({{ submissions.length }})
      </button>
      <button 
        @click="activeTab = 'live'"
        class="py-2.5 px-4 border-b-2 transition"
        :class="activeTab === 'live' ? 'border-indigo-500 text-indigo-400' : 'border-transparent text-slate-400 hover:text-white'"
      >
        Live Virtual Sessions ({{ liveSessions.length }})
      </button>
    </div>

    <!-- Tab 1: Authored Courses -->
    <div v-if="activeTab === 'courses'" class="space-y-4">
      <div 
        v-for="c in myCourses" 
        :key="c.id"
        class="glass-panel p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-slate-800"
      >
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="badge" :class="c.status === 'PUBLISHED' ? 'badge-emerald' : 'badge-amber'">
              {{ c.status }}
            </span>
            <span class="text-xs text-slate-400">{{ c.level }}</span>
            <span class="text-xs font-bold text-slate-300">{{ c.is_free ? 'Free' : c.price_display }}</span>
          </div>
          <h3 class="text-base font-bold text-white">{{ c.title }}</h3>
          <div class="text-xs text-slate-400 mt-1 flex items-center gap-3">
            <span>{{ c.total_lessons }} Lessons</span>
            <span>Created {{ new Date().toLocaleDateString() }}</span>
          </div>
        </div>

        <div class="flex items-center gap-2 shrink-0">
          <button 
            v-if="c.status === 'DRAFT'"
            @click="publishCourse(c.id)"
            class="btn-primary text-xs py-1.5 px-3"
          >
            Publish Live
          </button>
          <router-link :to="`/org/${orgSlug}/courses/${c.id}`" class="btn-secondary text-xs py-1.5 px-3">
            Preview Syllabus
          </router-link>
        </div>
      </div>
    </div>

    <!-- Tab 2: Project Submissions to Grade -->
    <div v-if="activeTab === 'submissions'" class="space-y-4">
      <div v-if="submissions.length === 0" class="glass-panel p-8 text-center text-xs text-slate-500 border border-slate-800">
        No student submissions awaiting evaluation.
      </div>
      <div 
        v-for="sub in submissions" 
        :key="sub.id"
        class="glass-panel p-5 border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
      >
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="badge" :class="sub.status === 'GRADED' ? 'badge-emerald' : 'badge-amber'">
              {{ sub.status }}
            </span>
            <span class="text-xs text-slate-400">Student: {{ sub.student_name || 'Enrolled Student' }}</span>
          </div>
          <p class="text-xs text-slate-300 line-clamp-2 italic mb-2">"{{ sub.content_text }}"</p>
          <div v-if="sub.grade" class="text-xs font-bold text-emerald-400">
            Graded: {{ sub.grade.score }} Points ("{{ sub.grade.feedback }}")
          </div>
        </div>

        <button @click="selectedSubmission = sub" class="btn-primary text-xs py-1.5 px-3 shrink-0">
          {{ sub.status === 'GRADED' ? 'Revise Grade' : 'Grade Submission' }}
        </button>
      </div>
    </div>

    <!-- Tab 3: Live Virtual Sessions -->
    <div v-if="activeTab === 'live'" class="space-y-4">
      <div 
        v-for="s in liveSessions" 
        :key="s.id"
        class="glass-panel p-5 border border-slate-800 flex items-center justify-between"
      >
        <div>
          <div class="flex items-center gap-2 mb-1">
            <span class="badge" :class="s.status === 'LIVE' ? 'badge-rose' : 'badge-cyan'">{{ s.status }}</span>
            <span class="text-xs text-slate-400">Starts: {{ new Date(s.scheduled_start).toLocaleString() }}</span>
          </div>
          <h4 class="text-sm font-bold text-white">{{ s.title }}</h4>
          <div class="text-xs text-slate-400 mt-1">{{ s.registered_count }} Students Registered</div>
        </div>

        <router-link :to="`/org/${orgSlug}/live/${s.id}`" class="btn-primary text-xs py-1.5 px-3">
          Enter as Host
        </router-link>
      </div>
    </div>

    <!-- Create Course Modal -->
    <div v-if="showCreateCourse" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="glass-panel p-6 max-w-lg w-full border border-slate-800 space-y-4 animate-fade-in">
        <h3 class="text-lg font-bold text-white">Author New Course</h3>
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Course Title</label>
          <input v-model="newTitle" type="text" placeholder="e.g. Advanced Event-Driven Microservices" class="input-field text-sm" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Description &amp; Syllabus Overview</label>
          <textarea v-model="newDesc" rows="3" placeholder="Learning objectives..." class="input-field text-sm"></textarea>
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-slate-400 mb-1">Difficulty Level</label>
            <select v-model="newLevel" class="input-field text-sm">
              <option value="BEGINNER">Beginner</option>
              <option value="INTERMEDIATE">Intermediate</option>
              <option value="ADVANCED">Advanced</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-400 mb-1">Access Model</label>
            <select v-model="newIsFree" class="input-field text-sm">
              <option :value="true">Free Enrollment</option>
              <option :value="false">Paid Course</option>
            </select>
          </div>
        </div>
        <div v-if="!newIsFree">
          <label class="block text-xs font-semibold text-slate-400 mb-1">Price (USD)</label>
          <input v-model="newPrice" type="number" step="0.01" class="input-field text-sm" />
        </div>
        <div class="flex justify-end gap-2 pt-2">
          <button @click="showCreateCourse = false" class="btn-secondary text-xs">Cancel</button>
          <button @click="createCourse" class="btn-primary text-xs">Create Draft Course</button>
        </div>
      </div>
    </div>

    <!-- Grade Submission Modal -->
    <div v-if="selectedSubmission" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="glass-panel p-6 max-w-md w-full border border-slate-800 space-y-4 animate-fade-in">
        <h3 class="text-lg font-bold text-white">Evaluate Student Submission</h3>
        <p class="text-xs text-slate-300 italic p-3 rounded-lg bg-slate-900 border border-slate-800">
          "{{ selectedSubmission.content_text }}"
        </p>
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Score (0 - 100)</label>
          <input v-model="gradeScore" type="number" min="0" max="100" class="input-field text-sm" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Instructor Feedback</label>
          <textarea v-model="gradeFeedback" rows="3" placeholder="Provide constructive technical guidance..." class="input-field text-sm"></textarea>
        </div>
        <div class="flex justify-end gap-2 pt-2">
          <button @click="selectedSubmission = null" class="btn-secondary text-xs">Cancel</button>
          <button @click="submitGrade" class="btn-primary text-xs">Save &amp; Issue Grade</button>
        </div>
      </div>
    </div>

    <!-- Schedule Live Class Modal -->
    <div v-if="showScheduleModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="glass-panel p-6 max-w-md w-full border border-slate-800 space-y-4 animate-fade-in">
        <h3 class="text-lg font-bold text-white">Schedule Live Virtual Workshop</h3>
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Session Title</label>
          <input v-model="liveTitle" type="text" placeholder="e.g. Multi-Region Cassandra Live Tuning" class="input-field text-sm" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Target Course</label>
          <select v-model="selectedCourseIdForLive" class="input-field text-sm">
            <option v-for="c in myCourses" :key="c.id" :value="c.id">{{ c.title }}</option>
          </select>
        </div>
        <div class="flex justify-end gap-2 pt-2">
          <button @click="showScheduleModal = false" class="btn-secondary text-xs">Cancel</button>
          <button @click="scheduleSession" class="btn-primary text-xs">Schedule Meeting</button>
        </div>
      </div>
    </div>
  </div>
</template>
