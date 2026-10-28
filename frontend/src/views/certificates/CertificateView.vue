<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { certificateApi } from '../../api/certificateApi';
import type { Certificate } from '../../types';
import { 
  Award, Download, ShieldCheck, CheckCircle, ArrowLeft, 
  ExternalLink, Share2, Copy
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();

const certificateId = route.params.certificateId as string;
const orgSlug = route.params.orgSlug as string;

const certificate = ref<Certificate | null>(null);
const loading = ref(true);
const copied = ref(false);

onMounted(async () => {
  try {
    certificate.value = await certificateApi.getCertificate(certificateId);
  } catch (e: any) {
    alert(e.message || 'Failed to load certificate.');
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
  setTimeout(() => { copied.value = false; }, 2500);
}
</script>

<template>
  <div class="max-w-4xl mx-auto py-8 animate-fade-in space-y-8">
    <button @click="router.back()" class="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition">
      <ArrowLeft class="w-4 h-4" /> Return to My Learning
    </button>

    <div v-if="loading" class="text-center py-24 text-slate-500">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
      Loading cryptographic certificate credential...
    </div>

    <div v-else-if="certificate" class="space-y-8">
      <!-- Certificate Preview Card (Luxury Digital Frame) -->
      <div class="rounded-2xl p-8 sm:p-12 bg-slate-900 border-4 border-amber-500/60 shadow-2xl relative overflow-hidden text-center">
        <!-- Inner gold border -->
        <div class="border border-amber-400/40 p-6 sm:p-10 rounded-xl relative">
          <div class="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto mb-4 text-amber-400 shadow-xl">
            <Award class="w-8 h-8" />
          </div>

          <div class="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
            {{ certificate.organization_name }}
          </div>

          <h1 class="text-2xl sm:text-3xl font-extrabold text-white tracking-tight mb-2">
            CERTIFICATE OF COMPLETION
          </h1>

          <p class="text-xs text-slate-400 italic mb-6">This certifies that</p>

          <h2 class="text-2xl sm:text-4xl font-black text-cyan-300 font-display mb-1">
            {{ certificate.student_name }}
          </h2>
          <div class="w-40 h-0.5 bg-gradient-to-r from-transparent via-cyan-400 to-transparent mx-auto mb-6"></div>

          <p class="text-xs sm:text-sm text-slate-300 max-w-xl mx-auto leading-relaxed mb-4">
            has successfully fulfilled all curriculum, lesson, quiz, and project requirements for the certified mastery of
          </p>

          <h3 class="text-xl sm:text-2xl font-bold text-amber-300 mb-8 font-display">
            {{ certificate.course_title }}
          </h3>

          <div class="pt-6 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-4">
            <div>
              <span class="text-slate-500 block">Issue Date</span>
              <strong class="text-white">{{ new Date(certificate.issued_at).toLocaleDateString() }}</strong>
            </div>
            <div>
              <span class="text-slate-500 block">Credential ID</span>
              <span class="font-mono text-indigo-400 font-bold">{{ certificate.certificate_number }}</span>
            </div>
            <div>
              <span class="text-slate-500 block">Status</span>
              <span class="badge badge-emerald">Verified Active</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-wrap items-center justify-center gap-4">
        <a 
          v-if="certificate.download_url"
          :href="certificate.download_url" 
          target="_blank" 
          download
          class="btn-primary py-3 px-6 font-bold text-sm shadow-xl shadow-indigo-500/25"
        >
          <Download class="w-4 h-4" /> Download Official PDF Certificate
        </a>

        <button @click="copyVerificationLink" class="btn-secondary py-3 px-6 text-sm">
          <Copy class="w-4 h-4" /> {{ copied ? 'Verification Link Copied!' : 'Copy Verification URL' }}
        </button>

        <router-link 
          :to="`/verify/${certificate.certificate_number}`" 
          class="btn-secondary py-3 px-6 text-sm"
        >
          <ShieldCheck class="w-4 h-4 text-emerald-400" /> Test Public Verification
        </router-link>
      </div>
    </div>
  </div>
</template>
