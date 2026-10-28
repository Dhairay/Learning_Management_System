<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { courseApi } from '../../api/courseApi';
import { enrollmentApi } from '../../api/enrollmentApi';
import type { Course, LessonSummary } from '../../types';
import { 
  PlayCircle, CheckCircle2, Circle, ArrowLeft, ArrowRight, 
  Award, FileText, Video, HelpCircle, Check, Sparkles
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();

const courseId = route.params.courseId as string;
const lessonId = ref(route.params.lessonId as string);
const orgSlug = route.params.orgSlug as string;

const playbackData = ref<{
  lesson_id: string;
  title: string;
  lesson_type: string;
  playback_url: string;
  content_text: string;
  duration_seconds: number;
} | null>(null);

const curriculumData = ref<{
  enrollment_id: string;
  course_title: string;
  progress_percentage: number;
  curriculum: Array<{
    id: string;
    title: string;
    position: number;
    lessons: Array<{
      id: string;
      title: string;
      lesson_type: string;
      position: number;
      is_required: boolean;
      duration_seconds: number;
      is_completed: boolean;
    }>;
  }>;
} | null>(null);

const videoRef = ref<HTMLVideoElement | null>(null);
const loading = ref(true);
const isCompleted = ref(false);

async function loadLesson() {
  loading.value = true;
  try {
    // 1. Fetch authorized playback
    playbackData.value = await courseApi.getLessonPlayback(lessonId.value);

    // 2. Fetch my curriculum
    const myEnrollments = await enrollmentApi.getMyEnrollments();
    const myEnr = myEnrollments.find(e => e.course.id === courseId);
    if (myEnr) {
      curriculumData.value = await enrollmentApi.getCurriculum(myEnr.id);
      
      // Check if current lesson is completed
      for (const sec of curriculumData.value.curriculum) {
        const found = sec.lessons.find(l => l.id === lessonId.value);
        if (found) {
          isCompleted.value = found.is_completed;
          break;
        }
      }
    }
  } catch (e: any) {
    alert(e.message || 'Failed to load lesson content.');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadLesson();
});

watch(() => route.params.lessonId, (newId) => {
  if (newId) {
    lessonId.value = newId as string;
    loadLesson();
  }
});

async function toggleLessonCompletion() {
  try {
    const res = await enrollmentApi.updateProgress({
      lesson_id: lessonId.value,
      completed: true,
      last_position_seconds: videoRef.value?.currentTime ? Math.floor(videoRef.value.currentTime) : 0,
    });
    isCompleted.value = true;
    if (curriculumData.value) {
      curriculumData.value.progress_percentage = res.course_progress_percentage;
      for (const sec of curriculumData.value.curriculum) {
        const found = sec.lessons.find(l => l.id === lessonId.value);
        if (found) {
          found.is_completed = true;
          break;
        }
      }
    }
    // If next lesson exists, navigate
    navigateToNextLesson();
  } catch (e: any) {
    alert(e.message || 'Failed to update progress');
  }
}

function navigateToLesson(lId: string) {
  router.push(`/org/${orgSlug}/learn/${courseId}/${lId}`);
}

function navigateToNextLesson() {
  if (!curriculumData.value) return;
  const allLessons = curriculumData.value.curriculum.flatMap(s => s.lessons);
  const currentIndex = allLessons.findIndex(l => l.id === lessonId.value);
  if (currentIndex !== -1 && currentIndex + 1 < allLessons.length) {
    navigateToLesson(allLessons[currentIndex + 1].id);
  }
}
</script>

<template>
  <div class="h-[calc(100vh-120px)] flex flex-col lg:flex-row gap-6 animate-fade-in">
    <!-- Main Player Area -->
    <div class="flex-1 flex flex-col glass-panel overflow-hidden border border-slate-800">
      <!-- Top Bar -->
      <div class="p-3.5 px-6 border-b border-slate-800/80 bg-slate-900/40 flex items-center justify-between">
        <router-link :to="`/org/${orgSlug}/courses/${courseId}`" class="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition">
          <ArrowLeft class="w-4 h-4" /> Back to Course Overview
        </router-link>
        <div class="flex items-center gap-2">
          <span class="badge" :class="isCompleted ? 'badge-emerald' : 'badge-indigo'">
            {{ isCompleted ? 'Completed' : 'In Progress' }}
          </span>
          <button 
            @click="toggleLessonCompletion" 
            class="btn-primary text-xs py-1.5 px-3 flex items-center gap-1.5"
          >
            <Check class="w-3.5 h-3.5" /> Mark Complete &amp; Next
          </button>
        </div>
      </div>

      <!-- Player / Content Content -->
      <div class="flex-1 overflow-y-auto p-6 space-y-6">
        <div v-if="loading" class="text-center py-20 text-slate-500">
          <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
          Loading streaming content...
        </div>

        <div v-else-if="playbackData">
          <!-- Video Player -->
          <div v-if="playbackData.lesson_type === 'VIDEO'" class="aspect-video bg-black rounded-xl overflow-hidden shadow-2xl relative">
            <video 
              ref="videoRef"
              :src="playbackData.playback_url"
              controls
              autoplay
              class="w-full h-full object-contain"
            ></video>
          </div>

          <!-- Quiz Interactive Card -->
          <div v-else-if="playbackData.lesson_type === 'QUIZ'" class="glass-panel p-8 text-center max-w-xl mx-auto border border-amber-500/30 my-8">
            <div class="w-14 h-14 rounded-2xl bg-amber-500/20 text-amber-400 flex items-center justify-center mx-auto mb-4 border border-amber-500/40 shadow-lg">
              <HelpCircle class="w-7 h-7" />
            </div>
            <h2 class="text-2xl font-bold text-white mb-2">{{ playbackData.title }}</h2>
            <p class="text-sm text-slate-400 mb-6">This lesson is an interactive assessment required for course certification.</p>
            <button 
              @click="router.push(`/org/${orgSlug}/quiz/${lessonId}`)" 
              class="btn-primary py-2.5 px-6 font-bold"
            >
              Launch Timed Quiz Experience
            </button>
          </div>

          <!-- Assignment Interactive Card -->
          <div v-else-if="playbackData.lesson_type === 'ASSIGNMENT'" class="glass-panel p-8 text-center max-w-xl mx-auto border border-rose-500/30 my-8">
            <div class="w-14 h-14 rounded-2xl bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto mb-4 border border-rose-500/40 shadow-lg">
              <Award class="w-7 h-7" />
            </div>
            <h2 class="text-2xl font-bold text-white mb-2">{{ playbackData.title }}</h2>
            <p class="text-sm text-slate-400 mb-6">Hands-on graded assignment evaluated by Dr. Marcus Sterling.</p>
            <button 
              @click="router.push(`/org/${orgSlug}/assignments/${lessonId}`)" 
              class="btn-primary py-2.5 px-6 font-bold"
            >
              Open Assignment &amp; Submit Solution
            </button>
          </div>

          <!-- Lesson Info & Text Body -->
          <div class="space-y-4 max-w-4xl pt-4">
            <h1 class="text-2xl font-bold text-white">{{ playbackData.title }}</h1>
            <div class="prose prose-invert text-slate-300 text-sm leading-relaxed whitespace-pre-line bg-slate-900/40 p-5 rounded-xl border border-slate-800">
              {{ playbackData.content_text || 'Video lecture notes and supplementary resources.' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Curriculum Sidebar -->
    <div class="w-full lg:w-96 glass-panel flex flex-col overflow-hidden border border-slate-800">
      <div class="p-4 border-b border-slate-800/80 bg-slate-900/60">
        <div class="flex items-center justify-between text-xs text-slate-400 mb-2">
          <span>Course Progress</span>
          <span class="font-bold text-indigo-400">{{ curriculumData?.progress_percentage || 0 }}%</span>
        </div>
        <div class="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
          <div 
            class="h-full bg-gradient-to-r from-indigo-500 to-cyan-400 transition-all duration-500"
            :style="{ width: `${curriculumData?.progress_percentage || 0}%` }"
          ></div>
        </div>
      </div>

      <div class="flex-1 overflow-y-auto divide-y divide-slate-800/60 p-2">
        <div 
          v-for="sec in curriculumData?.curriculum" 
          :key="sec.id"
          class="py-2"
        >
          <div class="text-[11px] font-bold text-slate-400 px-3 py-1.5 uppercase tracking-wider">
            {{ sec.title }}
          </div>
          <div class="space-y-1 mt-1">
            <button
              v-for="les in sec.lessons"
              :key="les.id"
              @click="navigateToLesson(les.id)"
              class="w-full text-left p-2.5 px-3 rounded-lg text-xs font-medium flex items-center justify-between transition"
              :class="les.id === lessonId ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 font-semibold' : 'text-slate-300 hover:bg-slate-800/50'"
            >
              <div class="flex items-center gap-2.5 truncate">
                <CheckCircle2 v-if="les.is_completed" class="w-4 h-4 text-emerald-400 shrink-0" />
                <Circle v-else class="w-4 h-4 text-slate-600 shrink-0" />
                <span class="truncate">{{ les.title }}</span>
              </div>
              <span class="text-[10px] text-slate-500 font-mono shrink-0 ml-2">
                {{ les.lesson_type.slice(0, 3) }}
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
