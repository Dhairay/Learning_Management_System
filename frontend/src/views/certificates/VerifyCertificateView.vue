<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { certificateApi } from '../../api/certificateApi';
import type { Certificate } from '../../types';
import { 
  ShieldCheck, Search, CheckCircle, XCircle, Award, 
  ArrowLeft, Building, Calendar, User, Sun, Moon
} from 'lucide-vue-next';
import { useTheme } from '../../composables/useTheme';

const route = useRoute();
const router = useRouter();
const { isDark, toggleTheme } = useTheme();

const certNumber = ref((route.params.certificateNumber as string) || '');
const verificationResult = ref<{
  valid: boolean;
  certificate?: Certificate;
  message?: string;
} | null>(null);

const loading = ref(false);

async function handleVerify() {
  if (!certNumber.value.trim()) return;
  loading.value = true;
  verificationResult.value = null;
  try {
    verificationResult.value = await certificateApi.verifyCertificate(certNumber.value.trim());
  } catch (err: any) {
    verificationResult.value = {
      valid: false,
      message: err.message || 'No valid credential found with this ID.'
    };
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (certNumber.value) {
    handleVerify();
  }
});
</script>

<template>
  <div class="min-h-screen max-w-3xl mx-auto p-4 sm:p-12 space-y-8 animate-fade-in">
    <!-- Return Link & Theme Switcher -->
    <div class="flex items-center justify-between">
      <router-link to="/" class="text-xs text-slate-400 hover:text-white inline-flex items-center gap-1.5 transition">
        <ArrowLeft class="w-3.5 h-3.5" /> Return to Course Catalog
      </router-link>
      <button 
        @click="toggleTheme" 
        type="button"
        class="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-100 transition flex items-center justify-center"
        :title="isDark ? 'Switch to Educational Light Mode' : 'Switch to Dark Mode'"
      >
        <Sun v-if="isDark" class="w-3.5 h-3.5 text-amber-400" />
        <Moon v-else class="w-3.5 h-3.5 text-indigo-500" />
      </button>
    </div>

    <div class="text-center space-y-3">
      <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-emerald-500 to-cyan-500 mx-auto flex items-center justify-center shadow-lg shadow-emerald-500/20 text-white">
        <ShieldCheck class="w-7 h-7" />
      </div>
      <h1 class="text-3xl font-extrabold text-white">Official Credential Verification</h1>
      <p class="text-slate-400 text-sm max-w-md mx-auto">
        Verify the authenticity of digital certificates issued across all organizations on the LMS Enterprise platform.
      </p>
    </div>

    <!-- Verification Search Input -->
    <div class="glass-panel p-4 border border-slate-800 shadow-xl max-w-xl mx-auto">
      <div class="flex items-center gap-2">
        <Search class="w-5 h-5 text-slate-500 ml-2" />
        <input 
          v-model="certNumber"
          @keyup.enter="handleVerify"
          type="text" 
          placeholder="Enter Certificate ID (e.g. CERT-ACME-202610-A91B4C)"
          class="bg-transparent border-none text-white text-sm w-full outline-none px-2 py-1 placeholder:text-slate-500 font-mono"
        />
        <button 
          @click="handleVerify" 
          :disabled="loading"
          class="btn-primary text-xs py-2 px-5 font-bold"
        >
          {{ loading ? 'Verifying...' : 'Verify' }}
        </button>
      </div>
    </div>

    <!-- Verification Status Output -->
    <div v-if="verificationResult" class="max-w-xl mx-auto animate-fade-in">
      <!-- Valid Credential Card -->
      <div 
        v-if="verificationResult.valid && verificationResult.certificate"
        class="glass-panel p-6 sm:p-8 border border-emerald-500/40 bg-emerald-950/20 shadow-2xl relative overflow-hidden"
      >
        <div class="flex items-start gap-4 mb-6">
          <div class="w-12 h-12 rounded-xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center text-emerald-400 shrink-0">
            <CheckCircle class="w-7 h-7" />
          </div>
          <div>
            <span class="badge badge-emerald text-xs">Authentic Credential</span>
            <h2 class="text-xl font-bold text-white mt-1">Verified Certificate of Completion</h2>
            <div class="text-xs font-mono text-emerald-300 mt-0.5">{{ verificationResult.certificate.certificate_number }}</div>
          </div>
        </div>

        <div class="space-y-3.5 pt-4 border-t border-slate-800 text-xs">
          <div class="flex items-center justify-between">
            <span class="text-slate-400 flex items-center gap-1.5"><User class="w-3.5 h-3.5" /> Recipient Learner:</span>
            <strong class="text-white text-sm">{{ verificationResult.certificate.student_name }}</strong>
          </div>

          <div class="flex items-center justify-between">
            <span class="text-slate-400 flex items-center gap-1.5"><Award class="w-3.5 h-3.5" /> Course Title:</span>
            <strong class="text-amber-300 text-sm">{{ verificationResult.certificate.course_title }}</strong>
          </div>

          <div class="flex items-center justify-between">
            <span class="text-slate-400 flex items-center gap-1.5"><Building class="w-3.5 h-3.5" /> Issuing Organization:</span>
            <strong class="text-white text-sm">{{ verificationResult.certificate.organization_name }}</strong>
          </div>

          <div class="flex items-center justify-between">
            <span class="text-slate-400 flex items-center gap-1.5"><Calendar class="w-3.5 h-3.5" /> Issue Date:</span>
            <span class="text-slate-300 font-medium">{{ new Date(verificationResult.certificate.issued_at).toLocaleDateString() }}</span>
          </div>
        </div>
      </div>

      <!-- Invalid Credential -->
      <div 
        v-else 
        class="glass-panel p-6 sm:p-8 border border-rose-500/40 bg-rose-950/20 text-center"
      >
        <XCircle class="w-10 h-10 text-rose-400 mx-auto mb-2" />
        <h3 class="text-lg font-bold text-white mb-1">Invalid or Revoked Credential</h3>
        <p class="text-xs text-slate-300">{{ verificationResult.message || 'We could not verify any certificate matching this number.' }}</p>
      </div>
    </div>

    <div class="text-center pt-8">
      <router-link to="/" class="text-xs text-indigo-400 hover:underline">
        &larr; Back to LMS Platform
      </router-link>
    </div>
  </div>
</template>
