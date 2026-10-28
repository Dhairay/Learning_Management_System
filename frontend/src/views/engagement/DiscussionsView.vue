<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { engagementApi } from '../../api/engagementApi';
import type { DiscussionThread } from '../../types';
import { 
  MessageSquare, Send, Reply, ArrowLeft, User, Clock, CornerDownRight
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();

const courseId = route.params.courseId as string;
const threads = ref<DiscussionThread[]>([]);
const newTitle = ref('');
const newContent = ref('');
const replyContent = ref<Record<string, string>>({});
const showNewThreadModal = ref(false);
const loading = ref(true);

async function loadDiscussions() {
  loading.value = true;
  try {
    threads.value = await engagementApi.getDiscussions(courseId);
  } catch (e) {
    console.error('Failed to load discussions', e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadDiscussions();
});

async function createThread() {
  if (!newTitle.value.trim() || !newContent.value.trim()) return;
  try {
    await engagementApi.createDiscussion(courseId, {
      title: newTitle.value,
      content: newContent.value,
    });
    newTitle.value = '';
    newContent.value = '';
    showNewThreadModal.value = false;
    await loadDiscussions();
  } catch (e: any) {
    alert(e.message || 'Failed to post thread');
  }
}

async function postReply(threadId: string) {
  const content = replyContent.value[threadId];
  if (!content || !content.trim()) return;
  try {
    await engagementApi.replyDiscussion(threadId, { content });
    replyContent.value[threadId] = '';
    await loadDiscussions();
  } catch (e: any) {
    alert(e.message || 'Failed to post reply');
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto py-6 animate-fade-in space-y-6">
    <button @click="router.back()" class="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition">
      <ArrowLeft class="w-4 h-4" /> Return to Course
    </button>

    <div class="flex items-center justify-between border-b border-slate-800 pb-4">
      <div>
        <h1 class="text-2xl font-bold text-white flex items-center gap-2">
          <MessageSquare class="w-6 h-6 text-indigo-400" /> Course Q&amp;A &amp; Discussion Board
        </h1>
        <p class="text-xs text-slate-400 mt-1">Ask questions, share architecture diagrams, and discuss topics with peers and instructors</p>
      </div>

      <button @click="showNewThreadModal = true" class="btn-primary text-xs py-2 px-4">
        Post Question
      </button>
    </div>

    <div v-if="loading" class="text-center py-20 text-slate-500">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
      Loading discussion threads...
    </div>

    <div v-else-if="threads.length === 0" class="text-center py-16 glass-panel border border-slate-800 p-8 rounded-xl">
      <MessageSquare class="w-10 h-10 text-slate-600 mx-auto mb-2" />
      <h3 class="text-base font-bold text-white mb-1">No discussions posted yet</h3>
      <p class="text-xs text-slate-400">Be the first to ask a technical question or share insight!</p>
    </div>

    <!-- Thread List -->
    <div v-else class="space-y-4">
      <div 
        v-for="t in threads" 
        :key="t.id"
        class="glass-panel p-6 border border-slate-800 space-y-4"
      >
        <div class="flex items-start justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-full bg-slate-800 text-xs font-bold text-indigo-400 flex items-center justify-center">
              {{ t.author_name[0] }}
            </div>
            <div>
              <div class="text-xs font-bold text-white">{{ t.author_name }}</div>
              <div class="text-[10px] text-slate-500">{{ new Date(t.created_at).toLocaleDateString() }}</div>
            </div>
          </div>
          <span class="badge badge-indigo text-[10px]">{{ t.replies_count }} Replies</span>
        </div>

        <div>
          <h3 class="text-base font-bold text-white mb-1">{{ t.title }}</h3>
          <p class="text-xs text-slate-300 leading-relaxed">{{ t.content }}</p>
        </div>

        <!-- Replies List -->
        <div v-if="t.replies && t.replies.length > 0" class="pl-4 sm:pl-8 space-y-3 pt-3 border-t border-slate-800/80">
          <div 
            v-for="r in t.replies" 
            :key="r.id"
            class="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 flex items-start gap-3"
          >
            <CornerDownRight class="w-4 h-4 text-indigo-400 shrink-0 mt-0.5" />
            <div class="space-y-1 text-xs">
              <div class="flex items-center gap-2">
                <span class="font-bold text-white">{{ r.author_name }}</span>
                <span class="text-[10px] text-slate-500">{{ new Date(r.created_at).toLocaleDateString() }}</span>
              </div>
              <p class="text-slate-300 leading-relaxed">{{ r.content }}</p>
            </div>
          </div>
        </div>

        <!-- Reply Input -->
        <div class="pt-2 flex gap-2">
          <input 
            v-model="replyContent[t.id]"
            @keyup.enter="postReply(t.id)"
            type="text" 
            placeholder="Write a technical response or follow-up question..." 
            class="input-field text-xs py-2"
          />
          <button @click="postReply(t.id)" class="btn-primary text-xs py-2 px-4 shrink-0">
            <Reply class="w-3.5 h-3.5" /> Reply
          </button>
        </div>
      </div>
    </div>

    <!-- New Thread Modal -->
    <div v-if="showNewThreadModal" class="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div class="glass-panel p-6 max-w-lg w-full border border-slate-800 space-y-4 animate-fade-in">
        <h3 class="text-lg font-bold text-white">Ask Question in Course Forum</h3>
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Topic / Subject</label>
          <input v-model="newTitle" type="text" placeholder="e.g. Invariant validation in concurrent checkout" class="input-field text-sm" />
        </div>
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Details &amp; Context</label>
          <textarea v-model="newContent" rows="4" placeholder="Explain the specific scenario, edge case, or code question..." class="input-field text-sm"></textarea>
        </div>
        <div class="flex justify-end gap-2 pt-2">
          <button @click="showNewThreadModal = false" class="btn-secondary text-xs">Cancel</button>
          <button @click="createThread" class="btn-primary text-xs">Post Question</button>
        </div>
      </div>
    </div>
  </div>
</template>
