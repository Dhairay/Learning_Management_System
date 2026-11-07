<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../../stores/authStore';
import { authApi } from '../../api/authApi';
import { useToast } from '../../composables/useToast';
import { useTheme } from '../../composables/useTheme';
import type { Organization } from '../../types';
import { Building, Plus, ArrowRight, Shield, ArrowLeft, Sun, Moon } from 'lucide-vue-next';

const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();
const { isDark, toggleTheme } = useTheme();

const allOrgs = ref<Organization[]>([]);
const newOrgName = ref('');
const newOrgDesc = ref('');
const showCreateModal = ref(false);
const loading = ref(false);

onMounted(async () => {
  try {
    allOrgs.value = await authApi.getOrganizations();
  } catch (e) {
    // Ignore
  }
});

function selectOrg(org: Organization) {
  authStore.switchOrganization(org);
  toast.info('Workspace Selected', `Switched to ${org.name}`);
  router.push(`/org/${org.slug}/catalog`);
}

async function createOrg() {
  if (!newOrgName.value.trim()) {
    toast.error('Name Required', 'Please enter an organization tenant name.');
    return;
  }
  loading.value = true;
  try {
    const created = await authApi.createOrganization({
      name: newOrgName.value,
      description: newOrgDesc.value
    });
    authStore.switchOrganization(created);
    await authStore.fetchProfile();
    toast.success('Organization Provisioned!', `Tenant workspace for ${created.name} is ready.`);
    showCreateModal.value = false;
    router.push(`/org/${created.slug}/catalog`);
  } catch (err: any) {
    toast.error('Provisioning Failed', err.message || 'Failed to create organization');
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen max-w-4xl mx-auto p-4 sm:p-12 animate-fade-in">
    <!-- Top Nav Controls -->
    <div class="flex items-center justify-between mb-8">
      <button @click="router.back()" class="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition">
        <ArrowLeft class="w-3.5 h-3.5" /> Return to Previous
      </button>

      <button 
        @click="toggleTheme" 
        class="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white transition flex items-center justify-center"
        :title="isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
      >
        <Sun v-if="isDark" class="w-4 h-4 text-amber-400" />
        <Moon v-else class="w-4 h-4 text-indigo-500" />
      </button>
    </div>

    <div class="text-center mb-10">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-semibold mb-3">
        <Building class="w-3.5 h-3.5" /> Multi-Tenant Workspace Architecture
      </div>
      <h1 class="text-3xl font-extrabold text-white mb-2">Select an Organization Tenant</h1>
      <p class="text-slate-400 text-sm max-w-lg mx-auto">
        Each organization runs in an isolated tenant domain with dedicated courses, enrollments, instructors, and certificates.
      </p>
    </div>

    <div class="grid sm:grid-cols-2 gap-4 mb-8">
      <div 
        v-for="org in allOrgs" 
        :key="org.id"
        @click="selectOrg(org)"
        class="glass-panel p-6 cursor-pointer group hover:border-indigo-500 transition-all"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="w-12 h-12 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center group-hover:scale-105 group-hover:border-indigo-500/50 transition">
            <Building class="w-6 h-6 text-indigo-400" />
          </div>
          <span class="badge badge-emerald">Active</span>
        </div>
        <h3 class="text-lg font-bold text-white group-hover:text-indigo-300 transition mb-1">{{ org.name }}</h3>
        <p class="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-4">{{ org.description || 'Enterprise educational tenant with verified course catalog.' }}</p>
        <div class="flex items-center justify-between text-xs text-indigo-400 font-semibold">
          <span>Enter Workspace</span>
          <ArrowRight class="w-4 h-4 transform group-hover:translate-x-1 transition" />
        </div>
      </div>
    </div>

    <div class="text-center">
      <button @click="showCreateModal = true" class="btn-secondary">
        <Plus class="w-4 h-4" /> Provision New Organization Tenant
      </button>
    </div>

    <!-- Create Org Modal -->
    <Teleport to="body">
      <div v-if="showCreateModal" class="modal-backdrop-wrap" @click.self="showCreateModal = false">
        <div class="modal-box max-w-md space-y-4">
          <h3 class="text-lg font-bold text-white mb-1">Provision Organization Tenant</h3>
          <p class="text-xs text-slate-400 mb-3">Creates a new isolated multi-tenant organization boundary.</p>
          <div class="space-y-3 mb-5">
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1.5">Organization Name</label>
              <input v-model="newOrgName" type="text" placeholder="e.g. Apex Engineering Labs" class="input-field text-sm" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-300 mb-1.5">Description</label>
              <textarea v-model="newOrgDesc" rows="3" placeholder="Brief mission statement..." class="input-field text-sm"></textarea>
            </div>
          </div>
          <div class="flex justify-end gap-2.5 pt-3 border-t border-slate-800">
            <button @click="showCreateModal = false" class="btn-secondary text-xs px-4 py-2">Cancel</button>
            <button @click="createOrg" :disabled="loading" class="btn-primary text-xs px-4 py-2">
              {{ loading ? 'Provisioning...' : 'Provision Tenant' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
