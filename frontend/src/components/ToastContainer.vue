<script setup lang="ts">
import { useToast } from '../composables/useToast';
import { CheckCircle2, AlertCircle, Info, AlertTriangle, X } from 'lucide-vue-next';

const { toasts, removeToast } = useToast();
</script>

<template>
  <div class="fixed bottom-5 right-5 z-[99999] flex flex-col gap-2.5 max-w-sm w-full pointer-events-none p-2 sm:p-0">
    <TransitionGroup name="toast">
      <div 
        v-for="t in toasts" 
        :key="t.id"
        class="pointer-events-auto rounded-xl p-3.5 shadow-2xl border flex items-start gap-3 backdrop-blur-xl transition-all duration-300"
        :class="{
          'bg-emerald-50 dark:bg-emerald-950/80 border-emerald-200 dark:border-emerald-500/40 text-emerald-950 dark:text-emerald-100': t.type === 'success',
          'bg-rose-50 dark:bg-rose-950/80 border-rose-200 dark:border-rose-500/40 text-rose-950 dark:text-rose-100': t.type === 'error',
          'bg-amber-50 dark:bg-amber-950/80 border-amber-200 dark:border-amber-500/40 text-amber-950 dark:text-amber-100': t.type === 'warning',
          'bg-indigo-50 dark:bg-indigo-950/80 border-indigo-200 dark:border-indigo-500/40 text-indigo-950 dark:text-indigo-100': t.type === 'info',
        }"
      >
        <div class="shrink-0 mt-0.5">
          <CheckCircle2 v-if="t.type === 'success'" class="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          <AlertCircle v-else-if="t.type === 'error'" class="w-5 h-5 text-rose-600 dark:text-rose-400" />
          <AlertTriangle v-else-if="t.type === 'warning'" class="w-5 h-5 text-amber-600 dark:text-amber-400" />
          <Info v-else class="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
        </div>

        <div class="flex-1 min-w-0 pr-1">
          <div class="font-bold text-xs leading-snug">{{ t.title }}</div>
          <div v-if="t.message" class="text-[11px] opacity-85 leading-relaxed mt-0.5 whitespace-pre-line">
            {{ t.message }}
          </div>
        </div>

        <button 
          @click="removeToast(t.id)" 
          class="shrink-0 opacity-60 hover:opacity-100 p-0.5 rounded transition"
          aria-label="Close notification"
        >
          <X class="w-4 h-4" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
}
.toast-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.95);
}
.toast-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>
