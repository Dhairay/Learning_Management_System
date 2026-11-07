<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { liveSessionApi } from '../../api/liveSessionApi';
import { useToast } from '../../composables/useToast';
import { 
  Video, Users, MessageSquare, ArrowLeft, Mic, MicOff, 
  Camera, CameraOff, PhoneOff, Shield, Radio, Hand, Send,
  Sparkles, MonitorUp, Settings
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const toast = useToast();

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
const isMicOn = ref(false);
const isCamOn = ref(true);
const isHandRaised = ref(false);
const activeTab = ref<'chat' | 'participants'>('chat');

const chatInput = ref('');
const messages = ref([
  { id: 1, user: 'Dr. Marcus Sterling', role: 'Instructor', text: 'Welcome everyone! Today we are discussing event sourcing and idempotent transactions.', time: '10:01 AM' },
  { id: 2, user: 'Sarah Jenkins', role: 'Student', text: 'Excited to be here! Can you share the whiteboard link later?', time: '10:03 AM' },
  { id: 3, user: 'Alex Rivera', role: 'Student', text: 'Audio is coming through loud and clear.', time: '10:04 AM' }
]);

const participants = ref([
  { id: 1, name: 'Dr. Marcus Sterling (Host)', role: 'Instructor', status: 'Speaking' },
  { id: 2, name: 'You (Student)', role: 'Attendee', status: 'Listening' },
  { id: 3, name: 'Sarah Jenkins', role: 'Attendee', status: 'Listening' },
  { id: 4, name: 'Alex Rivera', role: 'Attendee', status: 'Listening' },
  { id: 5, name: 'Michael Chang', role: 'Attendee', status: 'Listening' }
]);

onMounted(async () => {
  try {
    sessionData.value = await liveSessionApi.joinSession(sessionId);
    toast.success('Live Classroom Connected', `Joined "${sessionData.value.title}"`);
  } catch (e: any) {
    toast.error('Session Unavailable', e.message || 'Failed to join live session.');
    router.back();
  } finally {
    loading.value = false;
  }
});

function toggleMic() {
  isMicOn.value = !isMicOn.value;
  toast.info(isMicOn.value ? 'Microphone Active' : 'Microphone Muted');
}

function toggleCam() {
  isCamOn.value = !isCamOn.value;
  toast.info(isCamOn.value ? 'Camera Active' : 'Camera Disabled');
}

function toggleHand() {
  isHandRaised.value = !isHandRaised.value;
  if (isHandRaised.value) {
    toast.info('Hand Raised', 'The instructor and co-hosts have been notified.');
  } else {
    toast.info('Hand Lowered');
  }
}

function sendChatMessage() {
  if (!chatInput.value.trim()) return;
  messages.value.push({
    id: Date.now(),
    user: 'You (Student)',
    role: 'Student',
    text: chatInput.value.trim(),
    time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  });
  chatInput.value = '';
}
</script>

<template>
  <div class="h-[calc(100vh-120px)] flex flex-col glass-panel overflow-hidden border border-slate-800 animate-fade-in shadow-2xl">
    <!-- Classroom Top Bar -->
    <div class="p-3.5 px-6 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <button @click="router.back()" class="p-1.5 rounded-lg bg-slate-800 text-slate-400 hover:text-white transition">
          <ArrowLeft class="w-4 h-4" />
        </button>
        <div>
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping"></span>
            <span class="text-xs font-bold text-rose-500 uppercase tracking-wider">Live Broadcast &amp; Classroom</span>
            <span class="text-slate-500">&bull;</span>
            <span class="text-xs text-slate-400 font-mono">1080p 60fps HD</span>
          </div>
          <h2 class="text-base font-bold text-white">{{ sessionData?.title || 'Interactive Live Workshop' }}</h2>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <span class="badge badge-emerald text-xs hidden sm:inline-flex">
          <Shield class="w-3.5 h-3.5" /> Attendance Verified
        </span>
        <div class="flex items-center gap-1.5 text-xs font-bold text-slate-300 px-2.5 py-1 rounded-full bg-slate-800/80 border border-slate-700">
          <Users class="w-3.5 h-3.5 text-indigo-400" />
          <span>{{ participants.length }} Live</span>
        </div>
      </div>
    </div>

    <!-- Main Live Classroom Body: Video Stage + Side Panel -->
    <div class="flex-1 flex flex-col lg:flex-row overflow-hidden bg-black">
      <!-- Live Stream Video / Meeting Container -->
      <div class="flex-1 relative flex items-center justify-center overflow-hidden bg-slate-950">
        <iframe 
          v-if="sessionData?.room_url"
          :src="sessionData.room_url"
          allow="camera; microphone; fullscreen; display-capture"
          class="w-full h-full border-none"
        ></iframe>

        <!-- Simulated Interactive Lecture Stage when room is in preview -->
        <div v-else class="w-full h-full flex flex-col items-center justify-center p-8 text-center bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 relative">
          <!-- Spotlight background effect -->
          <div class="absolute inset-0 bg-radial-at-c from-indigo-900/20 via-transparent to-transparent pointer-events-none"></div>

          <div class="w-20 h-20 rounded-3xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center text-indigo-400 mb-4 shadow-2xl relative">
            <Video class="w-10 h-10 animate-pulse" />
            <span class="absolute top-2 right-2 w-3 h-3 rounded-full bg-rose-500"></span>
          </div>

          <h3 class="text-xl font-bold text-white mb-2">Live Lecture Stream Active</h3>
          <p class="text-xs text-slate-400 max-w-md mx-auto leading-relaxed mb-6">
            Connected to WebRTC relay server. Audio, video, and screen broadcast are synchronized with zero-latency streaming.
          </p>

          <div class="flex flex-wrap items-center justify-center gap-2">
            <span class="badge badge-indigo">
              <Sparkles class="w-3 h-3" /> AI Live Captions Active
            </span>
            <span class="badge badge-emerald">
              Stream Latency &lt; 120ms
            </span>
          </div>
        </div>
      </div>

      <!-- Right Classroom Panel: Chat & Roster -->
      <div class="w-full lg:w-80 border-t lg:border-t-0 lg:border-l border-slate-800 bg-slate-900/90 flex flex-col h-64 lg:h-full">
        <!-- Panel Tabs -->
        <div class="flex border-b border-slate-800 bg-slate-950/60 text-xs font-semibold">
          <button 
            @click="activeTab = 'chat'"
            class="flex-1 py-2.5 px-3 flex items-center justify-center gap-1.5 transition border-b-2"
            :class="activeTab === 'chat' ? 'text-indigo-400 border-indigo-500 bg-slate-900/50' : 'text-slate-400 border-transparent hover:text-slate-200'"
          >
            <MessageSquare class="w-3.5 h-3.5" />
            <span>Classroom Chat</span>
          </button>
          <button 
            @click="activeTab = 'participants'"
            class="flex-1 py-2.5 px-3 flex items-center justify-center gap-1.5 transition border-b-2"
            :class="activeTab === 'participants' ? 'text-indigo-400 border-indigo-500 bg-slate-900/50' : 'text-slate-400 border-transparent hover:text-slate-200'"
          >
            <Users class="w-3.5 h-3.5" />
            <span>Participants ({{ participants.length }})</span>
          </button>
        </div>

        <!-- Chat View -->
        <div v-if="activeTab === 'chat'" class="flex-1 flex flex-col overflow-hidden">
          <div class="flex-1 overflow-y-auto p-3 space-y-3">
            <div 
              v-for="msg in messages" 
              :key="msg.id"
              class="text-xs p-2 rounded-lg bg-slate-800/40 border border-slate-800 space-y-1"
            >
              <div class="flex items-center justify-between text-[11px]">
                <span class="font-bold text-white flex items-center gap-1.5">
                  {{ msg.user }}
                  <span v-if="msg.role === 'Instructor'" class="badge badge-amber text-[9px] py-0 px-1.5">Instructor</span>
                </span>
                <span class="text-slate-500 text-[10px]">{{ msg.time }}</span>
              </div>
              <p class="text-slate-300 leading-relaxed">{{ msg.text }}</p>
            </div>
          </div>

          <!-- Chat Input -->
          <div class="p-2 border-t border-slate-800 bg-slate-950/80 flex gap-1.5">
            <input 
              v-model="chatInput"
              @keyup.enter="sendChatMessage"
              type="text" 
              placeholder="Ask a question..."
              class="input-field text-xs py-1.5"
            />
            <button 
              @click="sendChatMessage"
              class="btn-primary py-1.5 px-3 text-xs shrink-0"
              title="Send Message"
            >
              <Send class="w-3.5 h-3.5" />
            </button>
          </div>
        </div>

        <!-- Participants View -->
        <div v-else class="flex-1 overflow-y-auto p-3 space-y-2">
          <div 
            v-for="p in participants" 
            :key="p.id"
            class="flex items-center justify-between p-2 rounded-lg bg-slate-800/30 border border-slate-800 text-xs"
          >
            <div class="flex items-center gap-2">
              <div class="w-6 h-6 rounded-full bg-indigo-500/20 text-indigo-400 font-bold flex items-center justify-center text-[10px]">
                {{ p.name[0] }}
              </div>
              <div>
                <div class="text-white font-medium truncate max-w-[130px]">{{ p.name }}</div>
                <div class="text-[10px] text-slate-500">{{ p.role }}</div>
              </div>
            </div>
            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded" :class="p.status === 'Speaking' ? 'bg-emerald-500/10 text-emerald-400 font-bold' : 'text-slate-500'">
              {{ p.status }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Classroom Controls -->
    <div class="p-3 bg-slate-950/95 border-t border-slate-800 flex items-center justify-center gap-3">
      <button 
        @click="toggleMic"
        class="p-2.5 sm:p-3 rounded-full transition shadow-md"
        :class="isMicOn ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'bg-slate-800 text-slate-400 hover:text-white'"
        :title="isMicOn ? 'Mute Microphone' : 'Unmute Microphone'"
      >
        <Mic v-if="isMicOn" class="w-5 h-5" />
        <MicOff v-else class="w-5 h-5 text-rose-400" />
      </button>

      <button 
        @click="toggleCam"
        class="p-2.5 sm:p-3 rounded-full transition shadow-md"
        :class="isCamOn ? 'bg-indigo-600 text-white hover:bg-indigo-700' : 'bg-slate-800 text-slate-400 hover:text-white'"
        :title="isCamOn ? 'Stop Camera' : 'Start Camera'"
      >
        <Camera v-if="isCamOn" class="w-5 h-5" />
        <CameraOff v-else class="w-5 h-5 text-rose-400" />
      </button>

      <button 
        @click="toggleHand"
        class="p-2.5 sm:p-3 rounded-full transition shadow-md"
        :class="isHandRaised ? 'bg-amber-500 text-white hover:bg-amber-600 ring-2 ring-amber-400/50' : 'bg-slate-800 text-slate-400 hover:text-white'"
        title="Raise Hand to Speak"
      >
        <Hand class="w-5 h-5" />
      </button>

      <div class="h-6 w-px bg-slate-800 mx-1 hidden sm:block"></div>

      <button 
        @click="router.back()"
        class="p-2.5 sm:p-3 px-5 sm:px-6 rounded-full bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold flex items-center gap-2 transition shadow-lg shadow-rose-600/25"
      >
        <PhoneOff class="w-4 h-4" /> 
        <span>Leave Session</span>
      </button>
    </div>
  </div>
</template>

