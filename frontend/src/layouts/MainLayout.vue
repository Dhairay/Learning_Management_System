<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
import { engagementApi } from '../api/engagementApi';
import type { NotificationItem } from '../types';
import { 
  GraduationCap, BookOpen, Layers, Award, Video, 
  MessageSquare, Users, Shield, Bell, LogOut, ChevronDown, CheckCircle
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const notifications = ref<NotificationItem[]>([]);
const showNotifications = ref(false);
const showOrgDropdown = ref(false);

const currentOrgSlug = computed(() => (route.params.orgSlug as string) || authStore.currentOrg?.slug || 'acme-academy');
const unreadNotificationsCount = computed(() => notifications.value.filter(n => !n.read).length);

onMounted(async () => {
  if (authStore.isAuthenticated) {
    try {
      notifications.value = await engagementApi.getNotifications();
    } catch (e) {
      // Ignore
    }
  }
});

function handleSwitchOrg(org: any) {
  authStore.switchOrganization(org);
  showOrgDropdown.value = false;
  router.push(`/org/${org.slug}/catalog`);
}

function handleLogout() {
  authStore.logout();
  router.push('/login');
}

async function markRead(n: NotificationItem) {
  if (n.read) return;
  try {
    await engagementApi.markNotificationRead(n.id);
    n.read = true;
  } catch (e) {
    // Ignore
  }
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-slate-950 text-slate-100">
    <!-- Navbar -->
    <header class="sticky top-0 z-50 border-b border-slate-800/80 bg-slate-950/80 backdrop-blur-md px-4 sm:px-8 py-3.5 flex items-center justify-between">
      <div class="flex items-center gap-6">
        <router-link :to="`/org/${currentOrgSlug}/catalog`" class="flex items-center gap-2.5 group text-decoration-none">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
            <GraduationCap class="w-5 h-5 text-white" />
          </div>
          <div>
            <div class="font-display font-bold text-lg leading-tight tracking-tight text-white flex items-center gap-2">
              LMS Platform
              <span class="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">Enterprise</span>
            </div>
            <div class="text-xs text-slate-400 font-medium">Modular Architecture</div>
          </div>
        </router-link>

        <!-- Organization Tenant Selector -->
        <div class="relative" v-if="authStore.memberships.length > 0">
          <button 
            @click="showOrgDropdown = !showOrgDropdown"
            class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 hover:text-white hover:border-slate-700 transition"
          >
            <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Tenant: <strong class="text-white">{{ authStore.currentOrg?.name || currentOrgSlug }}</strong></span>
            <ChevronDown class="w-3.5 h-3.5 text-slate-400" />
          </button>

          <div 
            v-if="showOrgDropdown"
            class="absolute left-0 mt-2 w-64 rounded-xl bg-slate-900/95 border border-slate-800 shadow-2xl p-2 z-50 backdrop-blur-xl animate-fade-in"
          >
            <div class="text-[11px] font-semibold text-slate-400 px-3 py-1.5 uppercase tracking-wider">Switch Organization</div>
            <button
              v-for="m in authStore.memberships"
              :key="m.organization.id"
              @click="handleSwitchOrg(m.organization)"
              class="w-full text-left px-3 py-2 rounded-lg text-xs font-medium flex items-center justify-between hover:bg-slate-800/80 transition"
              :class="authStore.currentOrg?.slug === m.organization.slug ? 'text-indigo-400 bg-indigo-500/10' : 'text-slate-300'"
            >
              <span>{{ m.organization.name }}</span>
              <span class="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 uppercase font-mono">{{ m.role }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Navigation Links -->
      <nav class="hidden md:flex items-center gap-1.5">
        <router-link 
          :to="`/org/${currentOrgSlug}/catalog`" 
          class="px-3.5 py-1.5 rounded-lg text-sm font-medium transition"
          :class="route.name === 'Catalog' ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-900'"
        >
          <BookOpen class="w-4 h-4 inline mr-1.5 -mt-0.5" />
          Browse Courses
        </router-link>

        <router-link 
          v-if="authStore.isAuthenticated"
          :to="`/org/${currentOrgSlug}/my-learning`" 
          class="px-3.5 py-1.5 rounded-lg text-sm font-medium transition"
          :class="route.name === 'MyLearning' ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-900'"
        >
          <Layers class="w-4 h-4 inline mr-1.5 -mt-0.5" />
          My Learning
        </router-link>

        <router-link 
          v-if="authStore.isInstructorOrAdmin"
          :to="`/org/${currentOrgSlug}/instructor/dashboard`" 
          class="px-3.5 py-1.5 rounded-lg text-sm font-medium transition"
          :class="route.name === 'InstructorDashboard' ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-900'"
        >
          <Award class="w-4 h-4 inline mr-1.5 -mt-0.5" />
          Instructor Studio
        </router-link>

        <router-link 
          v-if="authStore.isOrgAdmin"
          :to="`/org/${currentOrgSlug}/admin/members`" 
          class="px-3.5 py-1.5 rounded-lg text-sm font-medium transition"
          :class="route.name === 'AdminMembers' ? 'bg-indigo-500/15 text-indigo-400 border border-indigo-500/30 font-semibold' : 'text-slate-300 hover:text-white hover:bg-slate-900'"
        >
          <Shield class="w-4 h-4 inline mr-1.5 -mt-0.5" />
          Organization Admin
        </router-link>

        <router-link 
          to="/verify-certificate" 
          class="px-3.5 py-1.5 rounded-lg text-sm font-medium text-slate-300 hover:text-white hover:bg-slate-900 transition"
        >
          Verify Credential
        </router-link>
      </nav>

      <!-- Right Side User & Notification Controls -->
      <div class="flex items-center gap-3">
        <!-- Notifications -->
        <div class="relative" v-if="authStore.isAuthenticated">
          <button 
            @click="showNotifications = !showNotifications"
            class="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 hover:text-white hover:border-slate-700 relative transition"
          >
            <Bell class="w-4 h-4" />
            <span v-if="unreadNotificationsCount > 0" class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-white text-[10px] font-bold flex items-center justify-center">
              {{ unreadNotificationsCount }}
            </span>
          </button>

          <!-- Notification Drawer -->
          <div 
            v-if="showNotifications"
            class="absolute right-0 mt-2 w-80 rounded-xl bg-slate-900/95 border border-slate-800 shadow-2xl p-3 z-50 backdrop-blur-xl animate-fade-in"
          >
            <div class="flex items-center justify-between pb-2 border-b border-slate-800 mb-2">
              <span class="text-xs font-bold text-white uppercase tracking-wider">Notifications</span>
              <span class="text-[11px] text-slate-400">{{ notifications.length }} total</span>
            </div>
            <div class="max-h-72 overflow-y-auto space-y-2">
              <div 
                v-for="n in notifications" 
                :key="n.id"
                @click="markRead(n)"
                class="p-2.5 rounded-lg text-xs cursor-pointer transition border"
                :class="n.read ? 'bg-slate-950/40 border-slate-800/40 text-slate-400' : 'bg-slate-800/60 border-indigo-500/30 text-white'"
              >
                <div class="font-semibold text-slate-200 mb-0.5 flex items-center justify-between">
                  <span>{{ n.title }}</span>
                  <span v-if="!n.read" class="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
                </div>
                <div class="text-slate-400 leading-relaxed">{{ n.message }}</div>
              </div>
              <div v-if="notifications.length === 0" class="text-center py-6 text-slate-500 text-xs">
                No notifications yet.
              </div>
            </div>
          </div>
        </div>

        <!-- Auth state -->
        <div v-if="authStore.isAuthenticated" class="flex items-center gap-3">
          <div class="text-right hidden sm:block">
            <div class="text-xs font-semibold text-white">{{ authStore.user?.full_name }}</div>
            <div class="text-[10px] text-indigo-400 font-mono">{{ authStore.currentRole || 'MEMBER' }}</div>
          </div>
          <button 
            @click="handleLogout"
            class="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-rose-400 hover:border-rose-500/30 transition"
            title="Log Out"
          >
            <LogOut class="w-4 h-4" />
          </button>
        </div>
        <div v-else class="flex items-center gap-2">
          <router-link to="/login" class="btn-secondary text-xs py-1.5 px-3">Log In</router-link>
          <router-link to="/register" class="btn-primary text-xs py-1.5 px-3">Join Free</router-link>
        </div>
      </div>
    </header>

    <!-- Main Content View -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-8">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="border-t border-slate-800/80 bg-slate-950/50 py-8 px-6 text-center text-xs text-slate-500">
      <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          Enterprise Learning Management System &copy; 2026. Architected with Django REST Framework &amp; Vue 3.
        </div>
        <div class="flex items-center gap-4 text-slate-400">
          <span>Tenant Scoped</span>
          <span>&bull;</span>
          <span>Atomic Transactions</span>
          <span>&bull;</span>
          <span>PDF Certificates</span>
        </div>
      </div>
    </footer>
  </div>
</template>
