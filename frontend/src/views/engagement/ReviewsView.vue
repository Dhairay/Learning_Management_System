<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { engagementApi } from '../../api/engagementApi';
import { useToast } from '../../composables/useToast';
import type { CourseReview } from '../../types';
import { 
  Star, ArrowLeft, Send, CheckCircle2, MessageSquare, Award, ThumbsUp
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const courseId = route.params.courseId as string;
const reviewsData = ref<{
  course_id: string;
  average_rating: number;
  total_reviews: number;
  reviews: CourseReview[];
}>({
  course_id: courseId,
  average_rating: 0,
  total_reviews: 0,
  reviews: []
});

const myRating = ref(5);
const myReviewText = ref('');
const submitting = ref(false);
const loading = ref(true);

async function loadReviews() {
  loading.value = true;
  try {
    reviewsData.value = await engagementApi.getReviews(courseId);
  } catch (e) {
    console.error('Failed to load reviews', e);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadReviews();
});

async function submitReview() {
  if (!myReviewText.value.trim()) {
    toast.error('Review Required', 'Please share brief feedback on your course experience.');
    return;
  }
  submitting.value = true;
  try {
    await engagementApi.submitReview(courseId, {
      rating: myRating.value,
      review_text: myReviewText.value
    });
    toast.success('Review Published!', 'Thank you! Your verified student review is live.');
    myReviewText.value = '';
    await loadReviews();
  } catch (err: any) {
    toast.error('Review Not Allowed', err.message || 'Only enrolled students who accessed lessons can submit reviews.');
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

    <div class="border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold text-white flex items-center gap-2">
        <Star class="w-6 h-6 text-amber-400 fill-amber-400" /> Student Reviews &amp; Course Ratings
      </h1>
      <p class="text-xs text-slate-400 mt-1">Verified evaluations from enrolled learners who completed curriculum modules</p>
    </div>

    <!-- Rating Summary Header -->
    <div class="grid sm:grid-cols-3 gap-6 items-center glass-panel p-6 sm:p-8 border border-slate-800">
      <div class="text-center sm:text-left">
        <div class="text-4xl font-extrabold text-white mb-1">{{ reviewsData.average_rating }}</div>
        <div class="flex items-center justify-center sm:justify-start gap-1 text-amber-400 mb-1">
          <Star v-for="i in 5" :key="i" class="w-4 h-4" :class="i <= Math.round(reviewsData.average_rating) ? 'fill-amber-400' : 'text-slate-600'" />
        </div>
        <div class="text-xs text-slate-400">{{ reviewsData.total_reviews }} Verified Student Reviews</div>
      </div>

      <div class="sm:col-span-2 text-xs text-slate-400 space-y-1.5 border-t sm:border-t-0 sm:border-l border-slate-800 pt-4 sm:pt-0 sm:pl-6">
        <div>Ratings are only permitted for actively enrolled students who accessed the curriculum.</div>
        <div class="text-emerald-400 font-semibold flex items-center gap-1.5">
          <CheckCircle2 class="w-3.5 h-3.5" /> 100% Authentic Learner Feedback
        </div>
      </div>
    </div>

    <!-- Leave Review Form -->
    <div class="glass-panel p-6 border border-slate-800 space-y-4">
      <h3 class="text-sm font-bold text-white uppercase tracking-wider">Leave a Verified Review</h3>
      
      <div>
        <label class="block text-xs font-semibold text-slate-400 mb-1.5">Your Rating</label>
        <div class="flex items-center gap-2">
          <button 
            v-for="star in 5" 
            :key="star"
            @click="myRating = star"
            type="button"
            class="p-1 hover:scale-125 transition-transform"
          >
            <Star 
              class="w-6 h-6 transition-colors"
              :class="star <= myRating ? 'text-amber-400 fill-amber-400' : 'text-slate-600 hover:text-amber-400'"
            />
          </button>
          <span class="text-xs text-slate-400 font-bold ml-2">{{ myRating }} of 5 Stars</span>
        </div>
      </div>

      <div>
        <label class="block text-xs font-semibold text-slate-400 mb-1">Review Comments</label>
        <textarea 
          v-model="myReviewText" 
          rows="3" 
          placeholder="Share what you liked, what you learned, and how the exercises helped..."
          class="input-field text-sm"
        ></textarea>
      </div>

      <div class="flex justify-end">
        <button 
          @click="submitReview" 
          :disabled="submitting"
          class="btn-primary text-xs py-2 px-5 font-bold"
        >
          <Send class="w-3.5 h-3.5" /> {{ submitting ? 'Submitting...' : 'Submit Course Review' }}
        </button>
      </div>
    </div>

    <!-- Review List -->
    <div v-if="reviewsData.reviews.length === 0" class="glass-panel p-8 text-center border border-slate-800 rounded-xl">
      <MessageSquare class="w-10 h-10 text-slate-500 mx-auto mb-2" />
      <h3 class="text-base font-bold text-white mb-1">No reviews published yet</h3>
      <p class="text-xs text-slate-400">Enrolled students: be the first to rate this masterclass!</p>
    </div>

    <div v-else class="space-y-4">
      <div 
        v-for="rev in reviewsData.reviews" 
        :key="rev.id"
        class="glass-panel p-6 border border-slate-800 space-y-3"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <div class="w-8 h-8 rounded-full bg-slate-800 text-xs font-bold text-indigo-400 flex items-center justify-center">
              {{ rev.student_name[0] }}
            </div>
            <div>
              <div class="text-xs font-bold text-white">{{ rev.student_name }}</div>
              <div class="text-[10px] text-slate-500">{{ new Date(rev.created_at).toLocaleDateString() }}</div>
            </div>
          </div>
          <div class="flex items-center gap-1 text-amber-400">
            <Star v-for="i in rev.rating" :key="i" class="w-3.5 h-3.5 fill-amber-400" />
          </div>
        </div>
        <p class="text-xs text-slate-300 leading-relaxed">{{ rev.review_text }}</p>
      </div>
    </div>
  </div>
</template>
