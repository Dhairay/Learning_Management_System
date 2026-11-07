<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import { 
  GraduationCap, Lock, Mail, User, Building, ArrowRight, ArrowLeft, 
  BookOpen, Award, Shield, Check, Sun, Moon
} from 'lucide-vue-next';
import { useTheme } from '../../composables/useTheme';

const router = useRouter();
const authStore = useAuthStore();
const { isDark, toggleTheme } = useTheme();

type RegisterRole = 'STUDENT' | 'INSTRUCTOR';

const selectedRole = ref<RegisterRole>('STUDENT');
const email = ref('');
const password = ref('');
const firstName = ref('');
const lastName = ref('');
const errorMessage = ref('');
const loading = ref(false);

async function handleRegister() {
  errorMessage.value = '';
  loading.value = true;
  try {
    await authStore.register({
      email: email.value,
      password: password.value,
      first_name: firstName.value,
      last_name: lastName.value,
      role: selectedRole.value,
    });
    
    // Redirect based on role
    const orgSlug = authStore.currentOrg?.slug || 'acme-academy';
    if (selectedRole.value === 'INSTRUCTOR') {
      router.push(`/org/${orgSlug}/instructor/dashboard`);
    } else {
      router.push(`/org/${orgSlug}/catalog`);
    }
  } catch (err: any) {
    errorMessage.value = err.message || 'Registration failed. Please verify your details.';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4 relative">
    <div class="max-w-lg w-full glass-panel p-8 sm:p-10 shadow-2xl relative z-10 border border-slate-800">
      <!-- Return Link & Theme Switcher -->
      <div class="mb-4 flex items-center justify-between">
        <router-link to="/login" class="text-xs text-slate-400 hover:text-white inline-flex items-center gap-1.5 transition">
          <ArrowLeft class="w-3.5 h-3.5" /> Back to Sign In
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

      <div class="text-center mb-6">
        <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-500 to-cyan-400 mx-auto flex items-center justify-center shadow-lg shadow-indigo-500/25 mb-3">
          <GraduationCap class="w-6 h-6 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-white mb-1">Create Your LMS Account</h1>
        <p class="text-xs text-slate-400">Select your account role and get started in seconds</p>
      </div>

      <!-- Role Selector -->
      <div class="mb-6">
        <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">Select Your Role</label>
        <div class="grid grid-cols-2 gap-3">
          <!-- Student Card -->
          <button
            type="button"
            @click="selectedRole = 'STUDENT'"
            class="p-3.5 rounded-xl border text-center transition flex flex-col items-center justify-center gap-1.5 relative cursor-pointer"
            :class="selectedRole === 'STUDENT' ? 'bg-indigo-600/20 border-indigo-500 text-white shadow-lg shadow-indigo-500/20' : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-800/60 hover:text-white'"
          >
            <div 
              class="w-9 h-9 rounded-lg flex items-center justify-center"
              :class="selectedRole === 'STUDENT' ? 'bg-indigo-500 text-white' : 'bg-slate-800 text-slate-400'"
            >
              <BookOpen class="w-4 h-4" />
            </div>
            <span class="text-xs font-bold leading-tight">Student</span>
            <span class="text-[10px] text-slate-400 leading-tight">Enroll &amp; Learn</span>
            <div v-if="selectedRole === 'STUDENT'" class="absolute top-2 right-2 w-2 h-2 rounded-full bg-indigo-400"></div>
          </button>

          <!-- Teacher / Instructor Card -->
          <button
            type="button"
            @click="selectedRole = 'INSTRUCTOR'"
            class="p-3.5 rounded-xl border text-center transition flex flex-col items-center justify-center gap-1.5 relative cursor-pointer"
            :class="selectedRole === 'INSTRUCTOR' ? 'bg-amber-500/20 border-amber-500 text-white shadow-lg shadow-amber-500/20' : 'bg-slate-900/60 border-slate-800 text-slate-400 hover:bg-slate-800/60 hover:text-white'"
          >
            <div 
              class="w-9 h-9 rounded-lg flex items-center justify-center"
              :class="selectedRole === 'INSTRUCTOR' ? 'bg-amber-500 text-white' : 'bg-slate-800 text-slate-400'"
            >
              <Award class="w-4 h-4" />
            </div>
            <span class="text-xs font-bold leading-tight">Teacher</span>
            <span class="text-[10px] text-slate-400 leading-tight">Teach &amp; Author</span>
            <div v-if="selectedRole === 'INSTRUCTOR'" class="absolute top-2 right-2 w-2 h-2 rounded-full bg-amber-400"></div>
          </button>
        </div>
      </div>

      <div v-if="errorMessage" class="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="handleRegister" class="space-y-4">
        <!-- First & Last Name -->
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">First Name</label>
            <input 
              v-model="firstName" 
              type="text" 
              required
              placeholder="Alex" 
              class="input-field" 
            />
          </div>
          <div>
            <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Last Name</label>
            <input 
              v-model="lastName" 
              type="text" 
              required
              placeholder="Mercer" 
              class="input-field" 
            />
          </div>
        </div>

        <!-- Email -->
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Email Address</label>
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

        <!-- Password -->
        <div>
          <label class="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-1">Password</label>
          <div class="input-icon-wrapper">
            <Lock class="input-icon" />
            <input 
              v-model="password" 
              type="password" 
              required 
              minlength="6" 
              placeholder="Minimum 6 characters" 
              class="input-field" 
              autocomplete="new-password"
            />
          </div>
        </div>

        <!-- Submit Button -->
        <button 
          type="submit" 
          :disabled="loading" 
          class="btn-primary w-full justify-center py-3 mt-3 text-sm font-semibold shadow-lg shadow-indigo-500/30"
        >
          <span v-if="loading">Creating Account...</span>
          <span v-else class="flex items-center gap-1.5">
            Sign Up as {{ selectedRole === 'INSTRUCTOR' ? 'Teacher' : 'Student' }}
            <ArrowRight class="w-4 h-4" />
          </span>
        </button>
      </form>

      <div class="mt-6 pt-5 border-t border-slate-800 text-center text-xs text-slate-400">
        Already have an account? 
        <router-link to="/login" class="text-indigo-400 hover:text-indigo-300 hover:underline font-semibold ml-1">
          Sign in
        </router-link>
      </div>
    </div>
  </div>
</template>
