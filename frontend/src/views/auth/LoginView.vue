<script setup lang="ts">
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import { GraduationCap, Lock, Mail, ArrowRight, ArrowLeft, Sun, Moon } from 'lucide-vue-next';
import { useTheme } from '../../composables/useTheme';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const { isDark, toggleTheme } = useTheme();

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
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4 relative">
    <div class="max-w-md w-full glass-panel p-8 sm:p-10 shadow-2xl relative z-10 border border-slate-800">
      <!-- Return Link & Theme Switcher -->
      <div class="mb-4 flex items-center justify-between">
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

      <div class="text-center mb-8">
        <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-500 to-cyan-400 mx-auto flex items-center justify-center shadow-lg shadow-indigo-500/25 mb-4">
          <GraduationCap class="w-7 h-7 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-white mb-2">Sign in to LMS Platform</h1>
        <p class="text-sm text-slate-400">Access your institute courses, quizzes, and digital credentials</p>
      </div>

      <div v-if="errorMessage" class="mb-5 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="handleLogin" class="space-y-4">
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1.5">Email Address</label>
          <div class="input-icon-wrapper">
            <Mail class="input-icon" />
            <input 
              v-model="email" 
              type="email" 
              required 
              placeholder="you@company.com" 
              class="input-field"
              autocomplete="email"
            />
          </div>
        </div>

        <div>
          <div class="flex items-center justify-between mb-1.5">
            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400">Password</label>
          </div>
          <div class="input-icon-wrapper">
            <Lock class="input-icon" />
            <input 
              v-model="password" 
              type="password" 
              required 
              placeholder="Enter your password" 
              class="input-field"
              autocomplete="current-password"
            />
          </div>
        </div>

        <button 
          type="submit" 
          :disabled="loading" 
          class="btn-primary w-full justify-center py-3 mt-3 text-sm font-semibold shadow-lg shadow-indigo-500/30"
        >
          <span v-if="loading">Signing in...</span>
          <span v-else class="flex items-center gap-1.5">Sign In <ArrowRight class="w-4 h-4" /></span>
        </button>
      </form>

      <div class="mt-8 pt-6 border-t border-slate-800 text-center text-xs text-slate-400">
        Don't have an account yet? 
        <router-link to="/register" class="text-indigo-400 hover:text-indigo-300 hover:underline font-semibold ml-1">
          Sign up
        </router-link>
      </div>
    </div>
  </div>
</template>
