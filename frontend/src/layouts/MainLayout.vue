<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '../stores/authStore';
import { engagementApi } from '../api/engagementApi';
import { useTheme } from '../composables/useTheme';
import { useToast } from '../composables/useToast';
import type { NotificationItem } from '../types';
import { 
  GraduationCap, BookOpen, Layers, Award, Video, 
  MessageSquare, Users, Shield, Bell, LogOut, ChevronDown, CheckCircle, Code2,
  Sun, Moon, Menu, X, Check, User as UserIcon, Settings, ExternalLink,
  Sparkles
} from 'lucide-vue-next';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();
const toast = useToast();
const { isDark, toggleTheme } = useTheme();

const notifications = ref<NotificationItem[]>([]);
const showNotifications = ref(false);
const showOrgDropdown = ref(false);
const showUserDropdown = ref(false);
const showMobileMenu = ref(false);

const currentOrgSlug = computed(() => (route.params.orgSlug as string) || authStore.currentOrg?.slug || 'acme-academy');
const unreadNotificationsCount = computed(() => notifications.value.filter(n => !n.read).length);

const userInitials = computed(() => {
  const name = authStore.user?.full_name || authStore.user?.email || 'U';
  return name.slice(0, 2).toUpperCase();
});

const roleBadgeLabel = computed(() => {
  const r = authStore.user?.role?.name || authStore.user?.role_name || authStore.currentRole;
  if (authStore.user?.is_superuser || authStore.user?.is_staff || r === 'SUPER_ADMIN' || r === 'PLATFORM_ADMIN') return 'Super Admin';
  if (r === 'ADMIN' || r === 'ORG_ADMIN') return 'Institute Owner';
  if (r === 'TEACHER' || r === 'INSTRUCTOR') return 'Instructor';
  return 'Student';
});

const roleBadgeColor = computed(() => {
  const r = authStore.user?.role?.name || authStore.user?.role_name || authStore.currentRole;
  if (authStore.user?.is_superuser || authStore.user?.is_staff || r === 'SUPER_ADMIN' || r === 'PLATFORM_ADMIN') {
    return 'text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-500/15 border-rose-200 dark:border-rose-500/30';
  }
  if (r === 'ADMIN' || r === 'ORG_ADMIN') {
    return 'text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-500/15 border-emerald-200 dark:border-emerald-500/30';
  }
  if (r === 'TEACHER' || r === 'INSTRUCTOR') {
    return 'text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-500/15 border-amber-200 dark:border-amber-500/30';
  }
  return 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-500/15 border-indigo-200 dark:border-indigo-500/30';
});

function handleWindowClick(e: MouseEvent) {
  const target = e.target as HTMLElement;
  if (!target.closest('.dropdown-container')) {
    showOrgDropdown.value = false;
    showUserDropdown.value = false;
    showNotifications.value = false;
  }
}

onMounted(async () => {
  window.addEventListener('click', handleWindowClick);
  if (authStore.isAuthenticated) {
    try {
      notifications.value = await engagementApi.getNotifications();
    } catch (e) {
      // Ignore
    }
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('click', handleWindowClick);
});

function handleSwitchOrg(org: any) {
  authStore.switchOrganization(org);
  showOrgDropdown.value = false;
  toast.info('Institute switched', `Now browsing ${org.name}`);
  router.push(`/org/${org.slug}/catalog`);
}

function handleLogout() {
  showUserDropdown.value = false;
  authStore.logout();
  toast.info('Signed out', 'You have been safely signed out.');
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

async function markAllNotificationsRead() {
  for (const n of notifications.value) {
    if (!n.read) {
      markRead(n);
    }
  }
  toast.success('All caught up!', 'All notifications marked as read.');
}
</script>

<template>
  <div class="min-h-screen flex flex-col bg-slate-950 text-slate-100 transition-colors duration-200">
    <!-- Main Top Navigation Bar -->
    <header class="sticky top-0 z-40 border-b border-slate-800 bg-slate-950/85 backdrop-blur-md px-4 sm:px-8 py-3 flex items-center justify-between transition-colors">
      <!-- Left: Brand Logo & Tenant Switcher -->
      <div class="flex items-center gap-5">
        <router-link :to="`/org/${currentOrgSlug}/catalog`" class="flex items-center gap-3 group text-decoration-none">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-indigo-600 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition-transform">
            <GraduationCap class="w-5 h-5 text-white" />
          </div>
          <div>
            <div class="font-display font-extrabold text-lg leading-tight tracking-tight text-white flex items-center gap-1.5">
              <span>LMS Platform</span>
              <span class="text-[9px] uppercase tracking-wider font-bold px-1.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-500 dark:text-indigo-400 border border-indigo-500/25">
                Academy
              </span>
            </div>
            <div class="text-[11px] text-slate-400 font-medium">Enterprise Learning Hub</div>
          </div>
        </router-link>

        <!-- Organization Tenant Selector -->
        <div class="relative hidden sm:block dropdown-container" v-if="authStore.memberships.length > 0">
          <button 
            @click="showOrgDropdown = !showOrgDropdown"
            class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs font-medium text-slate-300 hover:text-white hover:border-slate-700 transition"
          >
            <span class="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>Institute: <strong class="text-white font-semibold">{{ authStore.currentOrg?.name || currentOrgSlug }}</strong></span>
            <ChevronDown class="w-3.5 h-3.5 text-slate-400" />
          </button>

          <div 
            v-if="showOrgDropdown"
            class="absolute left-0 mt-2 w-72 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl p-2 z-50 backdrop-blur-xl animate-fade-in"
          >
            <div class="text-[11px] font-bold text-slate-400 px-3 py-1.5 uppercase tracking-wider">Switch Organization</div>
            <button
              v-for="m in authStore.memberships"
              :key="m.organization.id"
              @click="handleSwitchOrg(m.organization)"
              class="w-full text-left px-3 py-2.5 rounded-lg text-xs font-medium flex items-center justify-between hover:bg-slate-800 transition my-0.5"
              :class="authStore.currentOrg?.slug === m.organization.slug ? 'text-indigo-500 dark:text-indigo-400 bg-indigo-500/10 font-bold' : 'text-slate-300'"
            >
              <div>
                <div class="text-white font-medium">{{ m.organization.name }}</div>
                <div class="text-[10px] text-slate-400 font-mono">{{ m.organization.slug }}</div>
              </div>
              <span class="text-[10px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 uppercase font-mono font-bold">
                {{ m.role }}
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Center: Navigation Links (Desktop) -->
      <nav class="hidden lg:flex items-center gap-1">
        <router-link 
          :to="`/org/${currentOrgSlug}/catalog`" 
          class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
          :class="route.name === 'Catalog' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/25' : 'text-slate-400 hover:text-white hover:bg-slate-900'"
        >
          <BookOpen class="w-3.5 h-3.5" />
          Browse Courses
        </router-link>

        <router-link 
          v-if="authStore.isAuthenticated"
          :to="`/org/${currentOrgSlug}/my-learning`" 
          class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
          :class="route.name === 'MyLearning' ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/25' : 'text-slate-400 hover:text-white hover:bg-slate-900'"
        >
          <Layers class="w-3.5 h-3.5" />
          My Learning
        </router-link>

        <!-- Teacher Studio (Teacher, Institute Owner, Super Admin) -->
        <router-link 
          v-if="authStore.isInstructorOrAdmin"
          :to="`/org/${currentOrgSlug}/instructor/dashboard`" 
          class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
          :class="route.name === 'InstructorDashboard' ? 'bg-amber-500 text-white shadow-md shadow-amber-500/25' : 'text-slate-400 hover:text-white hover:bg-slate-900'"
        >
          <Award class="w-3.5 h-3.5" />
          Teacher Studio
        </router-link>

        <!-- Institute Admin (Institute Owner / Admin, Super Admin) -->
        <router-link 
          v-if="authStore.isOrgAdmin"
          :to="`/org/${currentOrgSlug}/admin/members`" 
          class="px-3.5 py-1.5 rounded-lg text-xs font-semibold transition flex items-center gap-1.5"
          :class="route.name === 'AdminMembers' ? 'bg-emerald-600 text-white shadow-md shadow-emerald-600/25' : 'text-slate-400 hover:text-white hover:bg-slate-900'"
        >
          <Shield class="w-3.5 h-3.5" />
          Institute Admin
        </router-link>

        <router-link 
          to="/verify-certificate" 
          class="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-900 transition flex items-center gap-1.5"
          :class="route.name === 'VerifyCertificate' ? 'text-white bg-slate-900' : ''"
        >
          <CheckCircle class="w-3.5 h-3.5 text-emerald-500" />
          Verify Credential
        </router-link>

        <a 
          href="/api/docs/"
          target="_blank"
          class="px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-white hover:bg-slate-900 transition flex items-center gap-1.5"
          title="Open Swagger OpenAPI Documentation"
        >
          <Code2 class="w-3.5 h-3.5 text-cyan-500" />
          <span>API Docs</span>
        </a>
      </nav>

      <!-- Right: Theme, Notifications, User Menu, Mobile Toggle -->
      <div class="flex items-center gap-2.5">
        <!-- Theme Toggle (Light / Dark) -->
        <button 
          @click="toggleTheme" 
          class="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 transition flex items-center justify-center relative"
          :title="isDark ? 'Switch to Educational Light Mode' : 'Switch to Dark Mode'"
          aria-label="Toggle color theme"
        >
          <Sun v-if="isDark" class="w-4 h-4 text-amber-400 animate-fade-in" />
          <Moon v-else class="w-4 h-4 text-indigo-500 animate-fade-in" />
        </button>

        <!-- Notifications -->
        <div class="relative dropdown-container" v-if="authStore.isAuthenticated">
          <button 
            @click="showNotifications = !showNotifications; showUserDropdown = false"
            class="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 relative transition"
            title="Notifications"
          >
            <Bell class="w-4 h-4" />
            <span v-if="unreadNotificationsCount > 0" class="absolute -top-1 -right-1 w-4 h-4 rounded-full bg-rose-500 text-white text-[10px] font-bold flex items-center justify-center animate-pulse">
              {{ unreadNotificationsCount }}
            </span>
          </button>

          <!-- Notification Drawer -->
          <div 
            v-if="showNotifications"
            class="absolute right-0 mt-2 w-80 sm:w-96 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl p-3.5 z-50 backdrop-blur-xl animate-fade-in"
          >
            <div class="flex items-center justify-between pb-2.5 border-b border-slate-800 mb-2">
              <span class="text-xs font-bold text-white uppercase tracking-wider">Academic Notifications</span>
              <button 
                v-if="unreadNotificationsCount > 0" 
                @click="markAllNotificationsRead"
                class="text-[11px] text-indigo-400 hover:underline font-semibold"
              >
                Mark all as read
              </button>
            </div>
            <div class="max-h-72 overflow-y-auto space-y-2">
              <div 
                v-for="n in notifications" 
                :key="n.id"
                @click="markRead(n)"
                class="p-3 rounded-lg text-xs cursor-pointer transition border"
                :class="n.read ? 'bg-slate-950/40 border-slate-800/40 text-slate-400' : 'bg-slate-800/60 border-indigo-500/30 text-white'"
              >
                <div class="font-bold text-slate-200 mb-0.5 flex items-center justify-between">
                  <span>{{ n.title }}</span>
                  <span v-if="!n.read" class="w-2 h-2 rounded-full bg-indigo-500"></span>
                </div>
                <div class="text-slate-400 leading-relaxed text-[11px]">{{ n.message }}</div>
              </div>
              <div v-if="notifications.length === 0" class="text-center py-8 text-slate-400 text-xs">
                No notifications right now.
              </div>
            </div>
          </div>
        </div>

        <!-- User Profile Dropdown Menu (Logged In) -->
        <div class="relative dropdown-container" v-if="authStore.isAuthenticated">
          <button 
            @click="showUserDropdown = !showUserDropdown; showNotifications = false"
            class="flex items-center gap-2 p-1.5 sm:px-2.5 sm:py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-slate-700 transition"
          >
            <div class="w-7 h-7 rounded-full bg-gradient-to-tr from-indigo-500 to-cyan-400 flex items-center justify-center text-white text-xs font-bold shadow-sm">
              {{ userInitials }}
            </div>
            <div class="text-left hidden md:block">
              <div class="text-xs font-bold text-white leading-tight">
                {{ authStore.user?.full_name || authStore.user?.email?.split('@')[0] }}
              </div>
              <div class="text-[10px] text-slate-400 font-medium leading-none mt-0.5">
                {{ roleBadgeLabel }}
              </div>
            </div>
            <ChevronDown class="w-3.5 h-3.5 text-slate-400 hidden sm:block" />
          </button>

          <!-- User Menu Dropdown -->
          <div 
            v-if="showUserDropdown"
            class="absolute right-0 mt-2 w-64 rounded-xl bg-slate-900 border border-slate-800 shadow-2xl p-2 z-50 backdrop-blur-xl animate-fade-in"
          >
            <!-- User Info Header -->
            <div class="p-3 border-b border-slate-800 mb-1">
              <div class="text-xs font-bold text-white truncate">{{ authStore.user?.full_name || 'Enrolled User' }}</div>
              <div class="text-[11px] text-slate-400 truncate">{{ authStore.user?.email }}</div>
              <div class="mt-2 inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase tracking-wider" :class="roleBadgeColor">
                {{ roleBadgeLabel }}
              </div>
            </div>

            <!-- Links -->
            <div class="space-y-0.5 text-xs font-medium">
              <router-link 
                :to="`/org/${currentOrgSlug}/my-learning`" 
                @click="showUserDropdown = false"
                class="flex items-center gap-2 px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition"
              >
                <Layers class="w-4 h-4 text-indigo-400" />
                <span>My Learning Dashboard</span>
              </router-link>

              <router-link 
                v-if="authStore.isInstructorOrAdmin"
                :to="`/org/${currentOrgSlug}/instructor/dashboard`" 
                @click="showUserDropdown = false"
                class="flex items-center gap-2 px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition"
              >
                <Award class="w-4 h-4 text-amber-400" />
                <span>Teacher Studio</span>
              </router-link>

              <router-link 
                v-if="authStore.isOrgAdmin"
                :to="`/org/${currentOrgSlug}/admin/members`" 
                @click="showUserDropdown = false"
                class="flex items-center gap-2 px-3 py-2 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition"
              >
                <Shield class="w-4 h-4 text-emerald-400" />
                <span>Institute Admin</span>
              </router-link>

              <a 
                v-if="authStore.user?.is_staff"
                href="http://127.0.0.1:8000/admin/" 
                target="_blank"
                class="flex items-center gap-2 px-3 py-2 rounded-lg text-rose-600 dark:text-rose-400 hover:bg-rose-500/10 transition"
              >
                <Shield class="w-4 h-4 text-rose-500" />
                <span>Super Admin Django</span>
                <ExternalLink class="w-3 h-3 ml-auto opacity-70" />
              </a>

              <div class="border-t border-slate-800 my-1"></div>

              <button 
                @click="handleLogout"
                class="w-full text-left flex items-center gap-2 px-3 py-2 rounded-lg text-rose-600 dark:text-rose-400 hover:bg-rose-500/10 transition font-semibold"
              >
                <LogOut class="w-4 h-4" />
                <span>Sign Out</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Auth buttons (Logged Out) -->
        <div v-else class="flex items-center gap-2">
          <router-link to="/login" class="btn-secondary text-xs py-1.5 px-3 font-semibold">Sign In</router-link>
          <router-link to="/register" class="btn-primary text-xs py-1.5 px-3.5 font-bold shadow-md shadow-indigo-600/20">Sign Up Free</router-link>
        </div>

        <!-- Mobile Menu Toggle Button (Visible on < lg screens) -->
        <button 
          @click="showMobileMenu = !showMobileMenu"
          class="lg:hidden p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700 transition"
          aria-label="Open navigation menu"
        >
          <Menu v-if="!showMobileMenu" class="w-5 h-5" />
          <X v-else class="w-5 h-5" />
        </button>
      </div>
    </header>

    <!-- Mobile Navigation Drawer -->
    <div 
      v-if="showMobileMenu" 
      class="lg:hidden border-b border-slate-800 bg-slate-950 p-4 space-y-2 animate-fade-in shadow-xl"
    >
      <router-link 
        :to="`/org/${currentOrgSlug}/catalog`" 
        @click="showMobileMenu = false"
        class="flex items-center gap-2.5 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition"
        :class="route.name === 'Catalog' ? 'bg-indigo-600 text-white' : 'text-slate-300 hover:bg-slate-900'"
      >
        <BookOpen class="w-4 h-4" />
        <span>Browse Courses</span>
      </router-link>

      <router-link 
        v-if="authStore.isAuthenticated"
        :to="`/org/${currentOrgSlug}/my-learning`" 
        @click="showMobileMenu = false"
        class="flex items-center gap-2.5 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition"
        :class="route.name === 'MyLearning' ? 'bg-indigo-600 text-white' : 'text-slate-300 hover:bg-slate-900'"
      >
        <Layers class="w-4 h-4" />
        <span>My Learning</span>
      </router-link>

      <router-link 
        v-if="authStore.isInstructorOrAdmin"
        :to="`/org/${currentOrgSlug}/instructor/dashboard`" 
        @click="showMobileMenu = false"
        class="flex items-center gap-2.5 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition"
        :class="route.name === 'InstructorDashboard' ? 'bg-amber-500 text-white' : 'text-slate-300 hover:bg-slate-900'"
      >
        <Award class="w-4 h-4 text-amber-400" />
        <span>Teacher Studio</span>
      </router-link>

      <router-link 
        v-if="authStore.isOrgAdmin"
        :to="`/org/${currentOrgSlug}/admin/members`" 
        @click="showMobileMenu = false"
        class="flex items-center gap-2.5 px-3.5 py-2.5 rounded-lg text-sm font-semibold transition"
        :class="route.name === 'AdminMembers' ? 'bg-emerald-600 text-white' : 'text-slate-300 hover:bg-slate-900'"
      >
        <Shield class="w-4 h-4 text-emerald-400" />
        <span>Institute Admin</span>
      </router-link>

      <router-link 
        to="/verify-certificate" 
        @click="showMobileMenu = false"
        class="flex items-center gap-2.5 px-3.5 py-2.5 rounded-lg text-sm font-semibold text-slate-300 hover:bg-slate-900 transition"
      >
        <CheckCircle class="w-4 h-4 text-emerald-500" />
        <span>Verify Credential</span>
      </router-link>

      <a 
        href="/api/docs/" 
        target="_blank"
        class="flex items-center gap-2.5 px-3.5 py-2.5 rounded-lg text-sm font-semibold text-slate-300 hover:bg-slate-900 transition"
      >
        <Code2 class="w-4 h-4 text-cyan-400" />
        <span>OpenAPI Swagger Docs</span>
      </a>
    </div>

    <!-- Main Content Container -->
    <main class="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-8">
      <router-view />
    </main>

    <!-- Professional Educational Footer -->
    <footer class="border-t border-slate-800 bg-slate-950 py-10 px-6 text-xs text-slate-400 transition-colors">
      <div class="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-6">
        <div class="flex items-center gap-3">
          <div class="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold">
            <GraduationCap class="w-4 h-4" />
          </div>
          <div>
            <div class="font-bold text-white text-sm">Enterprise Learning Management System</div>
            <div class="text-[11px] text-slate-400">&copy; 2026 Modular Monolith Architecture. All rights reserved.</div>
          </div>
        </div>

        <div class="flex flex-wrap items-center gap-4 text-slate-400 font-medium">
          <span class="flex items-center gap-1.5"><Shield class="w-3.5 h-3.5 text-indigo-500" /> Multi-Tenant Boundary</span>
          <span>&bull;</span>
          <span class="flex items-center gap-1.5"><CheckCircle2 class="w-3.5 h-3.5 text-emerald-500" /> Verifiable PDF Credentials</span>
          <span>&bull;</span>
          <span class="flex items-center gap-1.5"><Video class="w-3.5 h-3.5 text-cyan-500" /> Virtual Classroom</span>
        </div>
      </div>
    </footer>
  </div>
</template>
