<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { assessmentApi } from '../../api/assessmentApi';
import type { Assignment, AssignmentSubmission } from '../../types';
import { 
  Award, FileText, CheckCircle2, Clock, ArrowLeft, Send, AlertCircle
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();

const assignmentId = route.params.assignmentId as string;
const orgSlug = route.params.orgSlug as string;

const assignment = ref<Assignment | null>(null);
const submission = ref<AssignmentSubmission | null>(null);

const submissionText = ref('');
const fileUrl = ref('');
const loading = ref(true);
const submitting = ref(false);

async function loadData() {
  loading.value = true;
  try {
    const data = await assessmentApi.getAssignment(assignmentId);
    assignment.value = data.assignment;
    submission.value = data.submission || null;
    if (submission.value) {
      submissionText.value = submission.value.content_text;
      fileUrl.value = submission.value.file_url || '';
    }
  } catch (e: any) {
    alert(e.message || 'Failed to load assignment.');
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadData();
});

async function handleSubmit() {
  if (!submissionText.value.trim() && !fileUrl.value.trim()) {
    alert('Please provide your solution text or reference link.');
    return;
  }
  submitting.value = true;
  try {
    submission.value = await assessmentApi.submitAssignment(assignmentId, {
      content_text: submissionText.value,
      file_url: fileUrl.value
    });
    alert('Assignment submission uploaded successfully!');
  } catch (e: any) {
    alert(e.message || 'Submission failed.');
  } finally {
    submitting.value = false;
  }
}
</script>

<template>
  <div class="max-w-4xl mx-auto py-6 animate-fade-in space-y-6">
    <button @click="router.back()" class="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition">
      <ArrowLeft class="w-4 h-4" /> Return to Course
    </button>

    <div v-if="loading" class="text-center py-24 text-slate-500">
      <div class="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
      Loading assignment specifications...
    </div>

    <div v-else-if="assignment" class="space-y-6">
      <!-- Header -->
      <div class="glass-panel p-6 sm:p-8 border border-slate-800">
        <div class="flex items-start justify-between gap-4 mb-4">
          <div>
            <div class="inline-flex items-center gap-1.5 text-xs font-semibold text-rose-400 mb-2">
              <Award class="w-4 h-4" /> Capstone Project &amp; Assignment
            </div>
            <h1 class="text-2xl font-bold text-white">{{ assignment.title }}</h1>
            <div class="text-xs text-slate-400 mt-1">Course: {{ assignment.course_title }}</div>
          </div>
          <div class="text-right shrink-0">
            <span class="badge badge-rose text-xs font-bold">{{ assignment.passing_score }}% Passing Score</span>
          </div>
        </div>

        <div class="grid grid-cols-2 sm:grid-cols-3 gap-4 pt-4 border-t border-slate-800 text-xs text-slate-400">
          <div>
            <span class="text-slate-500 block">Maximum Score</span>
            <strong class="text-white text-sm">{{ assignment.max_score }} Points</strong>
          </div>
          <div>
            <span class="text-slate-500 block">Passing Threshold</span>
            <strong class="text-white text-sm">{{ assignment.passing_score }} Points</strong>
          </div>
          <div>
            <span class="text-slate-500 block">Due Date</span>
            <strong class="text-white text-sm">{{ assignment.due_at ? new Date(assignment.due_at).toLocaleDateString() : 'Self-Paced' }}</strong>
          </div>
        </div>
      </div>

      <!-- Instructions -->
      <div class="glass-panel p-6 sm:p-8 border border-slate-800 space-y-3">
        <h3 class="text-sm font-bold text-white uppercase tracking-wider">Project Instructions &amp; Deliverables</h3>
        <div class="text-sm text-slate-300 leading-relaxed whitespace-pre-line bg-slate-900/50 p-5 rounded-xl border border-slate-800/80">
          {{ assignment.instructions }}
        </div>
      </div>

      <!-- Submission & Grading Status -->
      <div class="glass-panel p-6 sm:p-8 border border-slate-800 space-y-5">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-bold text-white uppercase tracking-wider">Your Submission (v{{ submission?.version || 1 }})</h3>
          <span 
            v-if="submission" 
            class="badge"
            :class="{
              'badge-amber': submission.status === 'SUBMITTED',
              'badge-emerald': submission.status === 'GRADED',
              'badge-rose': submission.status === 'RESUBMISSION_REQUIRED'
            }"
          >
            {{ submission.status }}
          </span>
        </div>

        <!-- Grade Banner if Graded -->
        <div v-if="submission?.grade" class="p-4 rounded-xl bg-slate-900 border border-emerald-500/30 flex items-start justify-between">
          <div>
            <div class="text-xs text-slate-400">Instructor Evaluation</div>
            <div class="text-lg font-bold text-emerald-400 mt-0.5">
              Score: {{ submission.grade.score }} / {{ assignment.max_score }}
            </div>
            <p class="text-xs text-slate-300 mt-2 leading-relaxed italic">
              "{{ submission.grade.feedback }}"
            </p>
          </div>
          <span class="badge badge-emerald">Graded by {{ submission.grade.grader_name }}</span>
        </div>

        <!-- Submission Form -->
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-400 mb-1">Architecture Summary / Solution Writeup</label>
            <textarea 
              v-model="submissionText" 
              rows="6" 
              placeholder="Paste your architecture rationale, database schema design, and technical decisions..."
              class="input-field text-sm"
            ></textarea>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-400 mb-1">Repository / Deliverable URL (GitHub / Cloud Storage)</label>
            <input 
              v-model="fileUrl" 
              type="url" 
              placeholder="https://github.com/organization/project-delivery"
              class="input-field text-sm"
            />
          </div>

          <div class="flex justify-end pt-2">
            <button 
              @click="handleSubmit" 
              :disabled="submitting" 
              class="btn-primary text-xs py-2.5 px-6 font-bold"
            >
              <Send class="w-4 h-4" /> {{ submitting ? 'Uploading...' : 'Submit Solution' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
