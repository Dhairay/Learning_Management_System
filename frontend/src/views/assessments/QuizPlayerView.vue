<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { assessmentApi } from '../../api/assessmentApi';
import type { Quiz, QuizAttempt } from '../../types';
import { 
  HelpCircle, Clock, CheckCircle, XCircle, ArrowLeft, ArrowRight, 
  RotateCcw, Award, Check
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();

const quizId = route.params.quizId as string;
const orgSlug = route.params.orgSlug as string;

const quiz = ref<Quiz | null>(null);
const pastAttempts = ref<QuizAttempt[]>([]);
const canAttempt = ref(true);

const currentAttemptId = ref<string | null>(null);
const answers = ref<Record<string, string[]>>({});
const submissionResult = ref<{
  score: number;
  passed: boolean;
  pass_percentage: number;
  message: string;
} | null>(null);

const loading = ref(true);
const submitting = ref(false);

async function loadQuiz() {
  loading.value = true;
  try {
    const data = await assessmentApi.getQuiz(quizId);
    quiz.value = data.quiz;
    pastAttempts.value = data.past_attempts;
    canAttempt.value = data.can_attempt;
  } catch (e: any) {
    alert(e.message || 'Failed to load quiz');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadQuiz();
});

async function startAttempt() {
  try {
    const attempt = await assessmentApi.startQuizAttempt(quizId);
    currentAttemptId.value = attempt.id;
    answers.value = {};
    submissionResult.value = null;
  } catch (e: any) {
    alert(e.message || 'Failed to start quiz attempt');
  }
}

function selectOption(qId: string, optId: string, qType: string) {
  if (qType === 'SINGLE_CHOICE') {
    answers.value[qId] = [optId];
  } else {
    if (!answers.value[qId]) answers.value[qId] = [];
    const idx = answers.value[qId].indexOf(optId);
    if (idx > -1) {
      answers.value[qId].splice(idx, 1);
    } else {
      answers.value[qId].push(optId);
    }
  }
}

async function submitQuiz() {
  if (!currentAttemptId.value) return;
  submitting.value = true;
  try {
    submissionResult.value = await assessmentApi.submitQuiz(currentAttemptId.value, answers.value);
    await loadQuiz();
  } catch (e: any) {
    alert(e.message || 'Failed to submit quiz');
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto py-6 animate-fade-in space-y-6">
    <button @click="router.back()" class="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition">
      <ArrowLeft class="w-4 h-4" /> Return to Course Curriculum
    </button>

    <div v-if="loading" class="text-center py-20 text-slate-500">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
      Loading interactive assessment...
    </div>

    <div v-else-if="quiz" class="space-y-6">
      <!-- Quiz Header -->
      <div class="glass-panel p-6 sm:p-8 border border-slate-800">
        <div class="flex items-start justify-between gap-4 mb-4">
          <div>
            <div class="inline-flex items-center gap-1.5 text-xs font-semibold text-amber-400 mb-2">
              <HelpCircle class="w-4 h-4" /> Comprehensive Knowledge Assessment
            </div>
            <h1 class="text-2xl font-bold text-white">{{ quiz.title }}</h1>
            <p class="text-xs text-slate-400 mt-1 leading-relaxed">{{ quiz.description || 'Answer all questions. Minimum passing percentage required to unlock certificate.' }}</p>
          </div>
          <div class="text-right shrink-0">
            <span class="badge badge-amber text-xs font-bold">{{ quiz.pass_percentage }}% To Pass</span>
          </div>
        </div>

        <div class="grid grid-cols-3 gap-3 pt-4 border-t border-slate-800/80 text-xs text-slate-400">
          <div>
            <span class="text-slate-500 block">Questions</span>
            <strong class="text-white text-sm">{{ quiz.total_questions }} Items</strong>
          </div>
          <div>
            <span class="text-slate-500 block">Time Limit</span>
            <strong class="text-white text-sm">{{ quiz.time_limit_minutes }} Minutes</strong>
          </div>
          <div>
            <span class="text-slate-500 block">Max Attempts</span>
            <strong class="text-white text-sm">{{ quiz.max_attempts }} Allowed</strong>
          </div>
        </div>
      </div>

      <!-- Result Banner if Evaluated -->
      <div v-if="submissionResult" class="glass-panel p-6 border" :class="submissionResult.passed ? 'border-emerald-500/50 bg-emerald-950/20' : 'border-rose-500/50 bg-rose-950/20'">
        <div class="flex items-center gap-3">
          <CheckCircle v-if="submissionResult.passed" class="w-8 h-8 text-emerald-400 shrink-0" />
          <XCircle v-else class="w-8 h-8 text-rose-400 shrink-0" />
          <div>
            <h3 class="text-lg font-bold text-white">
              Score: {{ submissionResult.score }}% — {{ submissionResult.passed ? 'Passed!' : 'Did Not Pass' }}
            </h3>
            <p class="text-xs text-slate-300">{{ submissionResult.message }}</p>
          </div>
        </div>
      </div>

      <!-- Start Attempt Screen -->
      <div v-if="!currentAttemptId && !submissionResult" class="glass-panel p-8 text-center border border-slate-800">
        <div class="w-12 h-12 rounded-xl bg-indigo-500/20 text-indigo-400 flex items-center justify-center mx-auto mb-3">
          <Clock class="w-6 h-6" />
        </div>
        <h3 class="text-lg font-bold text-white mb-2">Ready to Start?</h3>
        <p class="text-xs text-slate-400 max-w-md mx-auto mb-6">
          Once started, your answers will be timed and submitted directly to the grading engine for evaluation.
        </p>
        <button 
          v-if="canAttempt" 
          @click="startAttempt" 
          class="btn-primary py-2.5 px-6 font-bold"
        >
          Begin Quiz Attempt
        </button>
        <div v-else class="text-rose-400 text-xs font-semibold">
          Maximum attempts limit reached for this quiz.
        </div>

        <!-- Past Attempts History -->
        <div v-if="pastAttempts.length > 0" class="mt-8 pt-6 border-t border-slate-800/80 text-left">
          <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Past Attempts</h4>
          <div class="space-y-2">
            <div 
              v-for="att in pastAttempts" 
              :key="att.id"
              class="p-3 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between text-xs"
            >
              <div>
                <span class="font-bold text-white">Attempt #{{ att.attempt_number }}</span>
                <span class="text-slate-500 ml-2">{{ new Date(att.started_at).toLocaleDateString() }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="font-bold" :class="att.passed ? 'text-emerald-400' : 'text-rose-400'">
                  {{ att.score }}%
                </span>
                <span class="badge" :class="att.passed ? 'badge-emerald' : 'badge-rose'">
                  {{ att.passed ? 'Passed' : 'Failed' }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Active Attempt Runner -->
      <div v-else-if="currentAttemptId && !submissionResult" class="space-y-6">
        <div 
          v-for="(q, idx) in quiz.questions" 
          :key="q.id"
          class="glass-panel p-6 border border-slate-800"
        >
          <div class="flex items-start justify-between gap-3 mb-3">
            <span class="text-xs font-bold text-indigo-400 uppercase tracking-wide">Question {{ idx + 1 }} of {{ quiz.total_questions }}</span>
            <span class="text-[11px] text-slate-500 font-mono">{{ q.points }} Points</span>
          </div>
          <h3 class="text-base font-semibold text-white mb-4 leading-relaxed">{{ q.text }}</h3>

          <div class="space-y-2">
            <button
              v-for="opt in q.options"
              :key="opt.id"
              @click="selectOption(q.id, opt.id, q.question_type)"
              class="w-full text-left p-3 rounded-xl border text-xs font-medium transition flex items-center gap-3"
              :class="answers[q.id]?.includes(opt.id) ? 'bg-indigo-600/20 border-indigo-500 text-indigo-200' : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:bg-slate-800/60'"
            >
              <div 
                class="w-4 h-4 rounded-full border flex items-center justify-center shrink-0"
                :class="answers[q.id]?.includes(opt.id) ? 'border-indigo-400 bg-indigo-500' : 'border-slate-600'"
              >
                <div v-if="answers[q.id]?.includes(opt.id)" class="w-1.5 h-1.5 rounded-full bg-white"></div>
              </div>
              <span>{{ opt.text }}</span>
            </button>
          </div>
        </div>

        <div class="flex justify-end gap-3 pt-4">
          <button @click="currentAttemptId = null" class="btn-secondary text-xs">Cancel Attempt</button>
          <button @click="submitQuiz" :disabled="submitting" class="btn-primary text-xs font-bold py-2.5 px-6">
            {{ submitting ? 'Evaluating Answers...' : 'Submit Assessment for Grading' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
