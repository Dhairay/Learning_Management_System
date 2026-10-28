<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import { GraduationCap, Lock, Mail, User, Building, ArrowRight } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();

const email = ref('');
const password = ref('');
const firstName = ref('');
const lastName = ref('');
const organizationName = ref('');
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
      organization_name: organizationName.value || undefined
    });
    router.push(`/org/${authStore.currentOrg?.slug || 'acme-academy'}/catalog`);
  } catch (err: any) {
    errorMessage.value = err.message || 'Registration failed.';
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full glass-panel p-8 shadow-2xl border border-slate-800">
      <div class="text-center mb-6">
        <div class="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-500 to-cyan-400 mx-auto flex items-center justify-center shadow-lg shadow-indigo-500/25 mb-3">
          <GraduationCap class="w-6 h-6 text-white" />
        </div>
        <h1 class="text-2xl font-bold text-white mb-1">Create Your LMS Account</h1>
        <p class="text-xs text-slate-400">Join as an individual learner or launch an organization tenant</p>
      </div>

      <div v-if="errorMessage" class="mb-4 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-xs text-rose-300">
        {{ errorMessage }}
      </div>

      <form @submit.prevent="handleRegister" class="space-y-3.5">
        <div class="grid grid-cols-2 gap-2">
          <div>
            <label class="block text-xs font-semibold text-slate-400 mb-1">First Name</label>
            <input v-model="firstName" type="text" placeholder="Alex" class="input-field text-sm" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-400 mb-1">Last Name</label>
            <input v-model="lastName" type="text" placeholder="Mercer" class="input-field text-sm" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Email Address</label>
          <div class="relative">
            <Mail class="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input v-model="email" type="email" required placeholder="alex@company.com" class="input-field pl-9 text-sm" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Password</label>
          <div class="relative">
            <Lock class="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input v-model="password" type="password" required minlength="6" placeholder="Min. 6 characters" class="input-field pl-9 text-sm" />
          </div>
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">
            Organization Name <span class="text-slate-500 font-normal">(Optional for new tenant)</span>
          </label>
          <div class="relative">
            <Building class="w-4 h-4 text-slate-500 absolute left-3 top-3" />
            <input v-model="organizationName" type="text" placeholder="e.g. Apex Engineering Labs" class="input-field pl-9 text-sm" />
          </div>
        </div>

        <button type="submit" :disabled="loading" class="btn-primary w-full justify-center py-2.5 mt-2">
          <span v-if="loading">Creating Account...</span>
          <span v-else class="flex items-center gap-1.5">Sign Up Free <ArrowRight class="w-4 h-4" /></span>
        </button>
      </form>

      <div class="mt-6 text-center text-xs text-slate-400">
        Already have an account? 
        <router-link to="/login" class="text-indigo-400 hover:underline font-semibold">Sign in</router-link>
      </div>
    </div>
  </div>
</template>
