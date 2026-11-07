<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { authApi } from '../../api/authApi';
import { useToast } from '../../composables/useToast';
import type { OrganizationMembership } from '../../types';
import { 
  Shield, UserPlus, Users, Mail, UserCheck, Check, AlertCircle
} from 'lucide-vue-next';

const route = useRoute();
const toast = useToast();
const orgSlug = ref(route.params.orgSlug as string || 'acme-academy');

const members = ref<OrganizationMembership[]>([]);
const inviteEmail = ref('');
const inviteRole = ref('STUDENT');
const loading = ref(true);
const inviting = ref(false);

async function loadMembers() {
  loading.value = true;
  try {
    members.value = await authApi.getOrgMembers(orgSlug.value);
  } catch (e: any) {
    console.error('Failed to load members', e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadMembers();
});

async function sendInvite() {
  if (!inviteEmail.value.trim()) {
    toast.warning('Please enter an email address');
    return;
  }
  inviting.value = true;
  try {
    await authApi.inviteMember(orgSlug.value, {
      email: inviteEmail.value.trim(),
      role: inviteRole.value
    });
    toast.success('Invitation Sent!', `An invite link has been dispatched to ${inviteEmail.value.trim()}.`);
    inviteEmail.value = '';
    await loadMembers();
  } catch (err: any) {
    toast.error('Failed to send invitation', err.message);
  } finally {
    inviting.value = false;
  }
}

async function changeRole(membershipId: string, newRole: string) {
  try {
    await authApi.updateMemberRole(orgSlug.value, membershipId, newRole);
    toast.success('Role Updated!', `Member permissions updated to ${newRole}.`);
    await loadMembers();
  } catch (err: any) {
    toast.error('Failed to update member role', err.message);
  }
}
</script>

<template>
  <div class="space-y-8 animate-fade-in max-w-5xl mx-auto">
    <div class="border-b border-slate-800 pb-5">
      <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 text-indigo-400 text-xs font-semibold mb-2">
        <Shield class="w-3.5 h-3.5" /> Tenant Administration
      </div>
      <h1 class="text-3xl font-extrabold text-white">Organization Members &amp; Roles</h1>
      <p class="text-xs text-slate-400 mt-1">Manage user memberships, role assignments, and member invitations for <strong class="text-white">{{ orgSlug }}</strong></p>
    </div>

    <!-- Invite Member Box -->
    <div class="glass-panel p-6 border border-slate-800">
      <h3 class="text-sm font-bold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
        <UserPlus class="w-4 h-4 text-indigo-400" /> Invite Colleague or Student to Organization
      </h3>
      <div class="grid sm:grid-cols-3 gap-3">
        <div class="sm:col-span-2">
          <input 
            v-model="inviteEmail" 
            type="email" 
            placeholder="colleague@enterprise.com" 
            class="input-field text-sm"
          />
        </div>
        <div class="flex gap-2">
          <select v-model="inviteRole" class="input-field text-sm">
            <option value="STUDENT">Student</option>
            <option value="INSTRUCTOR">Teacher</option>
          </select>
          <button 
            @click="sendInvite" 
            :disabled="inviting"
            class="btn-primary text-xs py-2 px-4 shrink-0"
          >
            {{ inviting ? 'Sending...' : 'Invite' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Members Table -->
    <div class="glass-panel overflow-hidden border border-slate-800">
      <div class="p-4 bg-slate-900/60 border-b border-slate-800 flex items-center justify-between">
        <h3 class="text-sm font-bold text-white flex items-center gap-2">
          <Users class="w-4 h-4 text-slate-400" /> Active Organization Members ({{ members.length }})
        </h3>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left text-xs">
          <thead class="bg-slate-950/40 text-slate-400 uppercase tracking-wider border-b border-slate-800">
            <tr>
              <th class="p-3.5 px-4 font-semibold">Member</th>
              <th class="p-3.5 px-4 font-semibold">Assigned Role</th>
              <th class="p-3.5 px-4 font-semibold">Status</th>
              <th class="p-3.5 px-4 font-semibold">Joined Date</th>
              <th class="p-3.5 px-4 font-semibold text-right">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-800/50">
            <tr v-for="m in members" :key="m.id" class="hover:bg-slate-800/30 transition">
              <td class="p-3.5 px-4">
                <div class="font-bold text-white">{{ m.user?.full_name || 'User' }}</div>
                <div class="text-[11px] text-slate-400 font-mono">{{ m.user?.email }}</div>
              </td>
              <td class="p-3.5 px-4">
                <span class="badge" :class="{
                  'badge-emerald': m.role === 'ORG_ADMIN',
                  'badge-amber': m.role === 'INSTRUCTOR',
                  'badge-indigo': m.role === 'STUDENT',
                }">
                  {{ m.role }}
                </span>
              </td>
              <td class="p-3.5 px-4">
                <span class="text-emerald-400 font-medium">{{ m.status }}</span>
              </td>
              <td class="p-3.5 px-4 text-slate-400">
                {{ new Date(m.joined_at).toLocaleDateString() }}
              </td>
              <td class="p-3.5 px-4 text-right">
                <select 
                  :value="m.role" 
                  @change="changeRole(m.id, ($event.target as HTMLSelectElement).value)"
                  class="bg-slate-900 border border-slate-800 rounded px-2 py-1 text-[11px] text-slate-300 outline-none"
                >
                  <option value="STUDENT">Set Student</option>
                  <option value="INSTRUCTOR">Set Teacher</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
