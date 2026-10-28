<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { liveSessionApi } from '../../api/liveSessionApi';
import { 
  Video, Users, MessageSquare, ArrowLeft, Mic, MicOff, 
  Camera, CameraOff, PhoneOff, Shield, Radio
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();

const sessionId = route.params.sessionId as string;
const orgSlug = route.params.orgSlug as string;

const sessionData = ref<{
  session_id: string;
  title: string;
  room_url: string;
  provider: string;
  is_instructor: boolean;
} | null>(null);

const loading = ref(true);
const isMicOn = ref(true);
const isCamOn = ref(true);

onMounted(async () => {
  try {
    sessionData.value = await liveSessionApi.joinSession(sessionId);
  } catch (e: any) {
    alert(e.message || 'Failed to join live session.');
    router.back();
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="h-[calc(100vh-120px)] flex flex-col glass-panel overflow-hidden border border-slate-800 animate-fade-in">
    <!-- Classroom Top Bar -->
    <div class="p-4 px-6 border-b border-slate-800/80 bg-slate-900/60 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="router.back()" class="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition">
          <ArrowLeft class="w-4 h-4" />
        </button>
        <div>
          <div class="flex items-center gap-2">
            <span class="w-2 h-2 rounded-full bg-rose-500 animate-ping"></span>
            <span class="text-xs font-bold text-rose-400 uppercase tracking-wider">Live Broadcast &amp; Classroom</span>
          </div>
          <h2 class="text-base font-bold text-white">{{ sessionData?.title || 'Interactive Live Workshop' }}</h2>
        </div>
      </div>

      <div class="flex items-center gap-2">
        <span class="badge badge-emerald text-xs">
          <Shield class="w-3.5 h-3.5" /> Attendance Verified
        </span>
      </div>
    </div>

    <!-- Live Stream Video / Meeting Container -->
    <div class="flex-1 bg-black relative flex items-center justify-center overflow-hidden">
      <iframe 
        v-if="sessionData?.room_url"
        :src="sessionData.room_url"
        allow="camera; microphone; fullscreen; display-capture"
        class="w-full h-full border-none"
      ></iframe>
      <div v-else class="text-center p-8 text-slate-500">
        <Video class="w-12 h-12 mx-auto mb-2 text-slate-600 animate-pulse" />
        Connecting to live video conference adapter...
      </div>
    </div>

    <!-- Classroom Controls -->
    <div class="p-3 bg-slate-950/90 border-t border-slate-800 flex items-center justify-center gap-3">
      <button 
        @click="isMicOn = !isMicOn"
        class="p-3 rounded-full transition"
        :class="isMicOn ? 'bg-slate-800 text-white hover:bg-slate-700' : 'bg-rose-500 text-white'"
      >
        <Mic v-if="isMicOn" class="w-5 h-5" />
        <MicOff v-else class="w-5 h-5" />
      </button>

      <button 
        @click="isCamOn = !isCamOn"
        class="p-3 rounded-full transition"
        :class="isCamOn ? 'bg-slate-800 text-white hover:bg-slate-700' : 'bg-rose-500 text-white'"
      >
        <Camera v-if="isCamOn" class="w-5 h-5" />
        <CameraOff v-else class="w-5 h-5" />
      </button>

      <button 
        @click="router.back()"
        class="p-3 px-5 rounded-full bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold flex items-center gap-2 transition"
      >
        <PhoneOff class="w-4 h-4" /> Leave Session
      </button>
    </div>
  </div>
</template>
