<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { certificateApi } from '../../api/certificateApi';
import { useToast } from '../../composables/useToast';
import type { Certificate } from '../../types';
import { 
  Award, Download, ShieldCheck, CheckCircle, ArrowLeft, 
  ExternalLink, Share2, Copy, Printer
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const certificateId = route.params.certificateId as string;
const orgSlug = route.params.orgSlug as string;

const certificate = ref<Certificate | null>(null);
const loading = ref(true);
const copied = ref(false);

onMounted(async () => {
  try {
    certificate.value = await certificateApi.getCertificate(certificateId);
  } catch (e: any) {
    toast.error('Credential Error', e.message || 'Failed to load certificate.');
    router.back();
  } finally {
    loading.value = false;
  }
});

function copyVerificationLink() {
  if (!certificate.value) return;
  const url = `${window.location.origin}/verify/${certificate.value.certificate_number}`;
  navigator.clipboard.writeText(url);
  copied.value = true;
  toast.success('Link Copied!', 'Credential verification link copied to clipboard.');
  setTimeout(() => { copied.value = false; }, 2500);
}

function handlePrint() {
  window.print();
}
</script>

<template>
  <div class="max-w-4xl mx-auto py-8 animate-fade-in space-y-8">
    <div class="flex items-center justify-between no-print">
      <button @click="router.back()" class="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition">
        <ArrowLeft class="w-4 h-4" /> Return to My Learning
      </button>

      <span class="badge badge-emerald text-xs">
        <ShieldCheck class="w-3.5 h-3.5" /> Authenticated Digital Credential
      </span>
    </div>

    <div v-if="loading" class="text-center py-24 text-slate-500">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
      Loading cryptographic certificate credential...
    </div>

    <div v-else-if="certificate" class="space-y-8">
      <!-- Certificate Preview Card (Luxury Digital Frame) -->
      <div class="rounded-3xl p-6 sm:p-12 bg-white dark:bg-slate-900 border-4 sm:border-8 border-amber-500/70 shadow-2xl relative overflow-hidden text-center transition-colors">
        <!-- Corner Medallions / Academic Filigree -->
        <div class="absolute top-3 left-3 w-8 h-8 border-t-2 border-l-2 border-amber-400/60 pointer-events-none"></div>
        <div class="absolute top-3 right-3 w-8 h-8 border-t-2 border-r-2 border-amber-400/60 pointer-events-none"></div>
        <div class="absolute bottom-3 left-3 w-8 h-8 border-b-2 border-l-2 border-amber-400/60 pointer-events-none"></div>
        <div class="absolute bottom-3 right-3 w-8 h-8 border-b-2 border-r-2 border-amber-400/60 pointer-events-none"></div>

        <!-- Inner gold border -->
        <div class="border-2 border-dashed border-amber-400/50 p-6 sm:p-10 rounded-2xl relative bg-amber-500/[0.02]">
          <div class="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto mb-4 text-amber-500 shadow-xl">
            <Award class="w-8 h-8" />
          </div>

          <div class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 font-mono">
            {{ certificate.organization_name }}
          </div>

          <h1 class="text-2xl sm:text-4xl font-extrabold text-slate-900 dark:text-white tracking-tight mb-2 font-display">
            CERTIFICATE OF COMPLETION
          </h1>

          <p class="text-xs text-slate-500 dark:text-slate-400 italic mb-6">This official credential certifies that</p>

          <h2 class="text-3xl sm:text-5xl font-black text-indigo-600 dark:text-cyan-300 font-display mb-2">
            {{ certificate.student_name }}
          </h2>
          <div class="w-48 h-0.5 bg-gradient-to-r from-transparent via-indigo-500 to-transparent mx-auto mb-6"></div>

          <p class="text-xs sm:text-sm text-slate-600 dark:text-slate-300 max-w-xl mx-auto leading-relaxed mb-4">
            has successfully fulfilled all curriculum, lesson, quiz, and project requirements for the certified mastery of
          </p>

          <h3 class="text-xl sm:text-3xl font-extrabold text-amber-600 dark:text-amber-300 mb-8 font-display">
            {{ certificate.course_title }}
          </h3>

          <div class="pt-6 border-t border-slate-200 dark:border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 dark:text-slate-400 gap-4">
            <div>
              <span class="text-slate-400 block text-[11px]">Issue Date</span>
              <strong class="text-slate-800 dark:text-white font-medium">{{ new Date(certificate.issued_at).toLocaleDateString() }}</strong>
            </div>
            <div>
              <span class="text-slate-400 block text-[11px]">Credential ID</span>
              <span class="font-mono text-indigo-600 dark:text-indigo-400 font-bold">{{ certificate.certificate_number }}</span>
            </div>
            <div>
              <span class="text-slate-400 block text-[11px]">Verification</span>
              <span class="badge badge-emerald">100% Cryptographically Verified</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons (Hidden when printing) -->
      <div class="flex flex-wrap items-center justify-center gap-4 no-print">
        <a 
          v-if="certificate.download_url"
          :href="certificate.download_url" 
          target="_blank" 
          download
          class="btn-primary py-3 px-6 font-bold text-sm shadow-xl shadow-indigo-500/25"
        >
          <Download class="w-4 h-4" /> Download PDF Certificate
        </a>

        <button @click="handlePrint" class="btn-primary py-3 px-6 font-bold text-sm shadow-xl shadow-indigo-500/25">
          <Printer class="w-4 h-4" /> Print / Save as PDF
        </button>

        <button @click="copyVerificationLink" class="btn-secondary py-3 px-6 text-sm">
          <Copy class="w-4 h-4" /> {{ copied ? 'Verification Link Copied!' : 'Copy Verification URL' }}
        </button>

        <router-link 
          :to="`/verify/${certificate.certificate_number}`" 
          class="btn-secondary py-3 px-6 text-sm"
        >
          <ShieldCheck class="w-4 h-4 text-emerald-500" /> Public Verification Page
        </router-link>
      </div>
    </div>
  </div>
</template>

<style scoped>
@media print {
  .no-print {
    display: none !important;
  }
}
</style>

