<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from './stores/authStore';
import ToastContainer from './components/ToastContainer.vue';

const authStore = useAuthStore();

onMounted(async () => {
  if (localStorage.getItem('access_token')) {
    await authStore.fetchProfile();
  }
});
</script>

<template>
  <router-view />
  <ToastContainer />
</template>
