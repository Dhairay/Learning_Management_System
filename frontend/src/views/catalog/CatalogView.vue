<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { courseApi } from '../../api/courseApi';
import type { Course, Category } from '../../types';
import { 
  Search, BookOpen, Clock, Users, Award, PlayCircle, Filter, 
  Sparkles, CheckCircle2, ChevronRight, Star, ShieldCheck, Video, X
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();

const courses = ref<Course[]>([]);
const categories = ref<Category[]>([]);
const selectedCategory = ref('');
const searchQuery = ref('');
const loading = ref(true);

const orgSlug = ref(route.params.orgSlug as string || 'acme-academy');

async function loadData() {
  loading.value = true;
  try {
    const [cats, crs] = await Promise.all([
      courseApi.getCategories(),
      courseApi.getCourses({
        category: selectedCategory.value || undefined,
        search: searchQuery.value || undefined,
      })
    ]);
    categories.value = cats;
    courses.value = crs;
  } catch (e) {
    console.error('Failed to load catalog data', e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});

watch([selectedCategory, () => route.params.orgSlug], () => {
  if (route.params.orgSlug) orgSlug.value = route.params.orgSlug as string;
  loadData();
});

function handleSearch() {
  loadData();
}

function clearSearch() {
  searchQuery.value = '';
  loadData();
}

function formatDuration(seconds: number) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (hours > 0) return `${hours}h ${minutes}m`;
  return `${minutes} min`;
}
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <!-- Academic Hero Banner -->
    <div class="relative rounded-2xl overflow-hidden glass-panel p-8 sm:p-12 border border-slate-800 bg-gradient-to-r from-slate-900 via-indigo-950/20 to-slate-900 shadow-xl">
      <div class="max-w-2xl relative z-10">
        <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/25 text-indigo-500 dark:text-indigo-400 text-xs font-bold mb-4">
          <Sparkles class="w-3.5 h-3.5" /> High-Performance Certified Curriculum
        </div>
        <h1 class="text-3xl sm:text-4xl font-extrabold text-white tracking-tight mb-3">
          Explore University-Grade Courses &amp; Live Masterclasses
        </h1>
        <p class="text-slate-400 text-sm sm:text-base leading-relaxed mb-6">
          Architected for engineering mastery. Gain verifiable digital PDF credentials through interactive video lectures, graded assignments, live workshops, and rigorous quizzes.
        </p>

        <!-- Search Bar with Instant Clear -->
        <div class="flex items-center gap-2 max-w-lg bg-slate-950/80 border border-slate-700/80 rounded-xl p-1.5 focus-within:border-indigo-500 transition shadow-inner">
          <Search class="w-5 h-5 text-slate-400 ml-2 shrink-0" />
          <input 
            v-model="searchQuery" 
            @keyup.enter="handleSearch"
            type="text" 
            placeholder="Search by topic, architecture, technology..." 
            class="bg-transparent border-none text-white text-sm w-full outline-none px-2 py-1 placeholder:text-slate-500"
          />
          <button 
            v-if="searchQuery" 
            @click="clearSearch" 
            class="text-slate-400 hover:text-white p-1 rounded transition mr-1"
            title="Clear search"
          >
            <X class="w-4 h-4" />
          </button>
          <button @click="handleSearch" class="btn-primary text-xs py-2 px-4 rounded-lg font-bold shrink-0">
            Search
          </button>
        </div>

        <!-- Academic Trust Pills -->
        <div class="flex flex-wrap items-center gap-4 mt-6 text-xs text-slate-400 font-medium">
          <span class="flex items-center gap-1.5"><ShieldCheck class="w-4 h-4 text-emerald-500" /> Verifiable PDF Credentials</span>
          <span>&bull;</span>
          <span class="flex items-center gap-1.5"><PlayCircle class="w-4 h-4 text-indigo-500" /> Self-Paced Modules</span>
          <span>&bull;</span>
          <span class="flex items-center gap-1.5"><Video class="w-4 h-4 text-cyan-500" /> Virtual Classroom</span>
        </div>
      </div>

      <!-- Background subtle accent -->
      <div class="absolute -right-20 -bottom-20 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
    </div>

    <!-- Category Filter Bar -->
    <div class="flex items-center gap-2 overflow-x-auto pb-2 border-b border-slate-800 text-xs font-bold">
      <button 
        @click="selectedCategory = ''"
        class="px-4 py-2 rounded-lg transition shrink-0 flex items-center gap-1.5"
        :class="!selectedCategory ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' : 'bg-slate-900 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'"
      >
        <span>All Domains</span>
      </button>
      <button 
        v-for="cat in categories" 
        :key="cat.id"
        @click="selectedCategory = cat.slug"
        class="px-4 py-2 rounded-lg transition shrink-0 flex items-center gap-1.5"
        :class="selectedCategory === cat.slug ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30' : 'bg-slate-900 text-slate-400 hover:text-white hover:bg-slate-800 border border-slate-800'"
      >
        <span>{{ cat.name }}</span>
      </button>
    </div>

    <!-- Course Grid -->
    <div v-if="loading" class="text-center py-24 text-slate-500">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-3"></div>
      Loading course catalog...
    </div>

    <div v-else-if="courses.length === 0" class="text-center py-20 glass-panel border border-slate-800 p-8 rounded-2xl">
      <BookOpen class="w-12 h-12 text-slate-500 mx-auto mb-3" />
      <h3 class="text-lg font-bold text-white mb-1">No courses found</h3>
      <p class="text-xs text-slate-400 mb-4">Try clearing your search query or selecting another category.</p>
      <button @click="clearSearch(); selectedCategory = ''" class="btn-primary text-xs py-2 px-4">
        Reset Catalog Filters
      </button>
    </div>

    <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="c in courses" 
        :key="c.id"
        class="glass-panel overflow-hidden flex flex-col group hover:-translate-y-1 transition-all duration-300 border border-slate-800 hover:border-slate-700 hover:shadow-xl"
      >
        <!-- Course Thumbnail Cover -->
        <div class="relative aspect-video overflow-hidden bg-slate-900">
          <img 
            :src="c.thumbnail_url || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80'" 
            :alt="c.title"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
          <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-black/20"></div>
          
          <!-- Badges -->
          <div class="absolute top-3 left-3 flex items-center gap-1.5">
            <span class="badge shadow-sm" :class="c.is_free ? 'badge-emerald' : 'badge-amber'">
              {{ c.is_free ? 'Free Course' : c.price_display }}
            </span>
            <span class="badge badge-indigo text-[10px] shadow-sm">{{ c.level }}</span>
          </div>

          <!-- Academic Star Rating Pill -->
          <div class="absolute bottom-2.5 right-3 bg-black/75 backdrop-blur-md px-2 py-0.5 rounded-full text-[11px] font-bold text-amber-400 flex items-center gap-1">
            <Star class="w-3 h-3 fill-amber-400 text-amber-400" />
            <span>4.9</span>
          </div>
        </div>

        <!-- Course Meta & Body -->
        <div class="p-5 flex-1 flex flex-col justify-between">
          <div>
            <div class="text-[11px] font-bold text-indigo-500 dark:text-indigo-400 mb-1.5 tracking-wide uppercase">
              {{ c.category?.name || 'Computer Science' }}
            </div>
            <h3 class="text-base font-bold text-white group-hover:text-indigo-500 dark:group-hover:text-indigo-300 transition line-clamp-2 mb-2 leading-snug">
              {{ c.title }}
            </h3>
            <p class="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-4">
              {{ c.short_description || c.description }}
            </p>
          </div>

          <div class="pt-4 border-t border-slate-800/80">
            <div class="flex items-center justify-between text-xs text-slate-400 mb-4 font-medium">
              <div class="flex items-center gap-1.5">
                <PlayCircle class="w-3.5 h-3.5 text-indigo-500" />
                <span>{{ c.total_lessons || 0 }} Lessons</span>
              </div>
              <div class="flex items-center gap-1.5">
                <Clock class="w-3.5 h-3.5 text-cyan-500" />
                <span>{{ formatDuration(c.total_duration_seconds || 0) }}</span>
              </div>
            </div>

            <div class="flex items-center justify-between">
              <div class="text-xs font-semibold text-slate-300 flex items-center gap-2">
                <div class="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] font-bold text-indigo-500">
                  {{ c.instructor_name[0] }}
                </div>
                <span class="truncate max-w-[120px]">{{ c.instructor_name }}</span>
              </div>

              <router-link 
                :to="`/org/${orgSlug}/courses/${c.id}`" 
                class="btn-primary text-xs py-2 px-3.5 rounded-lg font-bold flex items-center gap-1 group-hover:shadow-indigo-500/25"
              >
                <span>View Syllabus</span>
                <ChevronRight class="w-3.5 h-3.5" />
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
