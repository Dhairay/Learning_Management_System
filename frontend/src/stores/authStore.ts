import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { authApi } from '../api/authApi';
import type { User, Organization, OrganizationMembership, Role } from '../types';

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null);
  const memberships = ref<OrganizationMembership[]>([]);
  const currentOrg = ref<Organization | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  const isAuthenticated = computed(() => !!user.value);

  const currentRole = computed<Role | null>(() => {
    if (!currentOrg.value || !memberships.value.length) return null;
    const mem = memberships.value.find(m => m.organization.id === currentOrg.value?.id || m.organization.slug === currentOrg.value?.slug);
    return mem ? mem.role : null;
  });

  const isInstructorOrAdmin = computed(() => {
    if (user.value?.is_staff) return true;
    return currentRole.value === 'PLATFORM_ADMIN' || currentRole.value === 'ORG_ADMIN' || currentRole.value === 'INSTRUCTOR';
  });

  const isOrgAdmin = computed(() => {
    if (user.value?.is_staff) return true;
    return currentRole.value === 'PLATFORM_ADMIN' || currentRole.value === 'ORG_ADMIN';
  });

  async function fetchProfile() {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    loading.value = true;
    error.value = null;
    try {
      const data = await authApi.getProfile();
      user.value = data.user;
      memberships.value = data.memberships;

      // Restore active organization from storage or pick first
      const storedSlug = localStorage.getItem('current_org_slug');
      if (storedSlug) {
        const found = memberships.value.find(m => m.organization.slug === storedSlug);
        if (found) {
          currentOrg.value = found.organization;
        }
      }
      if (!currentOrg.value && memberships.value.length > 0) {
        currentOrg.value = memberships.value[0].organization;
        localStorage.setItem('current_org_slug', currentOrg.value.slug);
      }
    } catch (err: any) {
      error.value = err.message;
      logout();
    } finally {
      loading.value = false;
    }
  }

  async function login(credentials: { email: string; password: string }) {
    loading.value = true;
    error.value = null;
    try {
      const tokens = await authApi.login(credentials);
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      await fetchProfile();
      return true;
    } catch (err: any) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  async function register(data: { email: string; password: string; first_name?: string; last_name?: string; organization_name?: string }) {
    loading.value = true;
    error.value = null;
    try {
      const resp = await authApi.register(data);
      localStorage.setItem('access_token', resp.tokens.access);
      localStorage.setItem('refresh_token', resp.tokens.refresh);
      await fetchProfile();
      return true;
    } catch (err: any) {
      error.value = err.message;
      throw err;
    } finally {
      loading.value = false;
    }
  }

  function switchOrganization(org: Organization) {
    currentOrg.value = org;
    localStorage.setItem('current_org_slug', org.slug);
  }

  function logout() {
    user.value = null;
    memberships.value = [];
    currentOrg.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('current_org_slug');
  }

  return {
    user,
    memberships,
    currentOrg,
    loading,
    error,
    isAuthenticated,
    currentRole,
    isInstructorOrAdmin,
    isOrgAdmin,
    fetchProfile,
    login,
    register,
    switchOrganization,
    logout,
  };
});
