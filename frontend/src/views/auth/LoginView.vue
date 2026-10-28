<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import { GraduationCap, Lock, Mail, ArrowRight, Shield, Award, UserCheck } from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const errorMessage = ref('');
const loading = ref(false);

async function handleLogin() {
  errorMessage.value = '';
  loading.value = true;
  try {
    await authStore.login({ email: email.value, password: password.value });
    const redirect = (route.query.redirect as string) || `/org/${authStore.currentOrg?.slug || 'acme-academy'}/catalog`;
    router.push(redirect);
  } catch (err: any) {
    errorMessage.value = err.message || 'Login failed. Please check your credentials.';
  } finally {
    loading.value = false;
  }
}

function fillCredentials(e: string, p: string) {
  email.value = e;
  password.value = p;
  handleLogin();
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4 relative">
    <div class="max-w-md w-full glass-panel p-8 shadow-2xl relative z-10 border border-slate-800">
      <div class="text-center mb-8">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-cyan-400 mx-auto flex items-center justify-center shadow-lg shadow-indigo-500/25 mb-4">
          <GraduationCap class="w-7 h-7 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-white mb-2">Sign in to Enterprise LMS</h1>
        <p class="text-sm text-slate-400">Access your organization courses, quizzes &amp; credentials</p>
      </div>

      <div v-if="errorMessage" class="mb-5 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">Email Address</label>
          <div class="relative">
            <Mail class="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input 
              v-model="email" 
              type="email" 
              required 
              placeholder="you@company.com" 
              class="input-field pl-9"
            />
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">Password</label>
          <div class="relative">
            <Lock class="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input 
              v-model="password" 
              type="password" 
              required 
              placeholder="••••••••" 
              class="input-field pl-9"
            />
          </div>
        </div>

        <button 
          type="submit" 
          :disabled="loading" 
          class="btn-primary w-full justify-center py-2.5 mt-2"
        >
          <span v-if="loading">Signing in...</span>
          <span v-else class="flex items-center gap-1.5">Continue to Platform <ArrowRight class="w-4 h-4" /></span>
        </button>
      </form>

      <!-- Quick Demo Sign-In Buttons -->
      <div class="mt-8 pt-6 border-t border-slate-800">
        <div class="text-[11px] font-semibold text-slate-500 uppercase tracking-wider text-center mb-3">Quick Demo Profiles (1-Click)</div>
        <div class="grid grid-cols-2 gap-2">
          <button 
            @click="fillCredentials('student@lms.local', 'StudentPass123!')"
            class="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-indigo-500/50 text-left transition"
          >
            <div class="flex items-center gap-1.5 text-xs font-semibold text-indigo-400">
              <UserCheck class="w-3.5 h-3.5" /> Sarah (Student)
            </div>
            <div class="text-[10px] text-slate-500">Enrolled &amp; Certified</div>
          </button>

          <button 
            @click="fillCredentials('instructor@lms.local', 'InstructorPass123!')"
            class="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-amber-500/50 text-left transition"
          >
            <div class="flex items-center gap-1.5 text-xs font-semibold text-amber-400">
              <Award class="w-3.5 h-3.5" /> Dr. Marcus (Inst.)
            </div>
            <div class="text-[10px] text-slate-500">Author &amp; Grader</div>
          </button>

          <button 
            @click="fillCredentials('admin@lms.local', 'AdminPass123!')"
            class="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-emerald-500/50 text-left transition"
          >
            <div class="flex items-center gap-1.5 text-xs font-semibold text-emerald-400">
              <Shield class="w-3.5 h-3.5" /> Eleanor (Admin)
            </div>
            <div class="text-[10px] text-slate-500">Org &amp; Platform Admin</div>
          </button>

          <button 
            @click="fillCredentials('tanish@lms.local', 'TanishPass123!')"
            class="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:border-cyan-500/50 text-left transition"
          >
            <div class="flex items-center gap-1.5 text-xs font-semibold text-cyan-400">
              <UserCheck class="w-3.5 h-3.5" /> Tanish (Dev)
            </div>
            <div class="text-[10px] text-slate-500">Personalized Demo</div>
          </button>
        </div>
      </div>

      <div class="mt-6 text-center text-xs text-slate-400">
        New learner or organization? 
        <router-link to="/register" class="text-indigo-400 hover:underline font-semibold">Create account</router-link>
      </div>
    </div>
  </div>
</template>
