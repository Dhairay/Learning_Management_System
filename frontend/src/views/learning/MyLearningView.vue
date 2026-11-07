<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { enrollmentApi } from '../../api/enrollmentApi';
import { certificateApi } from '../../api/certificateApi';
import { useToast } from '../../composables/useToast';
import type { Enrollment } from '../../types';
import { 
  BookOpen, PlayCircle, Award, CheckCircle, Clock, 
  Sparkles, ArrowRight, Download, ShieldCheck
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const toast = useToast();

const enrollments = ref<Enrollment[]>([]);
const loading = ref(true);
const issuing = ref<string | null>(null);

const orgSlug = ref(route.params.orgSlug as string || 'acme-academy');

async function loadEnrollments() {
  loading.value = true;
  try {
    enrollments.value = await enrollmentApi.getMyEnrollments();
  } catch (e: any) {
    toast.error('Failed to load courses', e.message);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadEnrollments();
});

async function claimCertificate(enrollmentId: string) {
  issuing.value = enrollmentId;
  try {
    const cert = await certificateApi.issueCertificate(enrollmentId);
    toast.success('Certificate Issued!', `Official Credential ID: ${cert.certificate_number}`);
    router.push(`/org/${orgSlug.value}/certificates/${cert.id}`);
  } catch (err: any) {
    toast.warning('Certificate Ineligible', err.message || 'Complete all required lessons, quizzes, and assignments first.');
  } finally {
    issuing.value = null;
  }
}
</script>

<template>
  <div class="space-y-8 animate-fade-in">
    <div class="border-b border-slate-800 pb-5">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-xs font-semibold mb-2">
        <Sparkles class="w-3.5 h-3.5" /> Learner Hub
      </div>
      <h1 class="text-3xl font-extrabold text-white">My Enrolled Courses</h1>
      <p class="text-xs text-slate-400 mt-1">Track curriculum progress, complete modules, and claim verified credentials</p>
    </div>

    <div v-if="loading" class="text-center py-24 text-slate-500">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
      Loading learning journey...
    </div>

    <div v-else-if="enrollments.length === 0" class="text-center py-20 glass-panel border border-slate-800 p-8 rounded-2xl">
      <BookOpen class="w-12 h-12 text-slate-600 mx-auto mb-3" />
      <h3 class="text-lg font-bold text-white mb-1">You are not enrolled in any courses yet</h3>
      <p class="text-xs text-slate-400 mb-5">Explore our certified catalog and start learning today.</p>
      <router-link :to="`/org/${orgSlug}/catalog`" class="btn-primary text-xs py-2 px-4">
        Browse Course Catalog
      </router-link>
    </div>

    <div v-else class="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
      <div 
        v-for="enr in enrollments" 
        :key="enr.id"
        class="glass-panel overflow-hidden flex flex-col justify-between border border-slate-800"
      >
        <div>
          <!-- Thumbnail -->
          <div class="aspect-video bg-slate-900 relative overflow-hidden">
            <img 
              :src="enr.course.thumbnail_url || 'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80'" 
              :alt="enr.course.title"
              class="w-full h-full object-cover"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent"></div>
            <div class="absolute top-3 left-3">
              <span class="badge" :class="enr.status === 'COMPLETED' ? 'badge-emerald' : 'badge-indigo'">
                {{ enr.status }}
              </span>
            </div>
          </div>

          <div class="p-5">
            <div class="text-[11px] font-semibold text-indigo-400 mb-1 uppercase tracking-wide">
              {{ enr.course.organization_name }}
            </div>
            <h3 class="text-base font-bold text-white mb-3 line-clamp-2">
              {{ enr.course.title }}
            </h3>

            <!-- Progress Bar -->
            <div class="space-y-1.5 mb-4">
              <div class="flex items-center justify-between text-xs text-slate-400">
                <span>Progress</span>
                <span class="font-bold text-white">{{ enr.progress_percentage }}%</span>
              </div>
              <div class="w-full h-2 rounded-full bg-slate-800 overflow-hidden">
                <div 
                  class="h-full bg-gradient-to-r from-indigo-500 to-cyan-400"
                  :style="{ width: `${enr.progress_percentage}%` }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div class="p-5 pt-0 space-y-2">
          <router-link 
            :to="`/org/${orgSlug}/courses/${enr.course.id}`" 
            class="btn-primary w-full justify-center text-xs py-2 font-semibold"
          >
            {{ enr.status === 'COMPLETED' ? 'Review Course Material' : 'Continue Learning' }} <ArrowRight class="w-3.5 h-3.5" />
          </router-link>

          <button 
            @click="claimCertificate(enr.id)"
            :disabled="issuing === enr.id"
            class="btn-secondary w-full justify-center text-xs py-2 font-semibold border-amber-500/30 text-amber-300 hover:bg-amber-500/10"
          >
            <Award class="w-3.5 h-3.5 text-amber-400" />
            <span>{{ issuing === enr.id ? 'Evaluating & Issuing...' : 'Claim PDF Certificate' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
