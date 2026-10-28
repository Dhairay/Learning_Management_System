<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { enrollmentApi } from '../../api/enrollmentApi';
import { useAuthStore } from '../../stores/authStore';
import { 
  CreditCard, ShieldCheck, Lock, CheckCircle, ArrowRight, Building
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();

const orderId = route.params.orderId as string;
const loading = ref(false);
const paymentSuccess = ref(false);
const enrollmentsCreated = ref<string[]>([]);

async function completePayment() {
  loading.value = true;
  try {
    const res = await enrollmentApi.processPayment(orderId);
    paymentSuccess.value = true;
    enrollmentsCreated.value = res.enrollments;
  } catch (err: any) {
    alert(err.message || 'Payment simulation failed.');
  } finally {
    loading.value = false;
  }
}

function goToLearning() {
  const orgSlug = authStore.currentOrg?.slug || 'acme-academy';
  router.push(`/org/${orgSlug}/my-learning`);
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center p-4">
    <div class="max-w-md w-full glass-panel p-8 shadow-2xl border border-slate-800 animate-fade-in">
      <div v-if="!paymentSuccess">
        <div class="text-center mb-6">
          <div class="w-14 h-14 rounded-2xl bg-indigo-500/20 text-indigo-400 mx-auto flex items-center justify-center border border-indigo-500/30 mb-3 shadow-lg">
            <CreditCard class="w-7 h-7" />
          </div>
          <h1 class="text-2xl font-bold text-white mb-1">Secure Course Checkout</h1>
          <p class="text-xs text-slate-400">Order ID: <span class="font-mono">{{ orderId.slice(0, 18) }}...</span></p>
        </div>

        <div class="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2 mb-6 text-xs">
          <div class="flex justify-between text-slate-400">
            <span>Course Enrollment</span>
            <span class="text-white font-semibold">Masterclass Entitlement</span>
          </div>
          <div class="flex justify-between text-slate-400">
            <span>Provider Integration</span>
            <span class="text-indigo-400 font-mono">Stripe / Webhook Simulation</span>
          </div>
          <div class="pt-2 border-t border-slate-800 flex justify-between text-sm font-bold text-white">
            <span>Total Billed</span>
            <span class="text-emerald-400">$89.00 USD</span>
          </div>
        </div>

        <button 
          @click="completePayment" 
          :disabled="loading" 
          class="btn-primary w-full justify-center py-3 text-sm font-bold shadow-xl shadow-indigo-500/30"
        >
          <span v-if="loading">Confirming Payment with Gateway...</span>
          <span v-else class="flex items-center gap-2">
            <Lock class="w-4 h-4" /> Pay &amp; Activate Enrollment
          </span>
        </button>

        <div class="mt-4 text-center text-[11px] text-slate-500 flex items-center justify-center gap-1.5">
          <ShieldCheck class="w-3.5 h-3.5 text-emerald-400" /> 256-Bit TLS End-To-End Encrypted Transaction
        </div>
      </div>

      <!-- Payment Success State -->
      <div v-else class="text-center space-y-4 py-4 animate-fade-in">
        <div class="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center border border-emerald-500/40">
          <CheckCircle class="w-9 h-9" />
        </div>
        <h2 class="text-2xl font-bold text-white">Enrollment Activated!</h2>
        <p class="text-xs text-slate-300 leading-relaxed max-w-xs mx-auto">
          Your payment has cleared, the entitlement was granted in an atomic transaction, and full course access is now open.
        </p>

        <button @click="goToLearning" class="btn-primary w-full justify-center py-2.5 text-xs font-bold mt-2">
          Start Course Now <ArrowRight class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>
