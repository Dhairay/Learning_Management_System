<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { enrollmentApi } from '../../api/enrollmentApi';
import { useAuthStore } from '../../stores/authStore';
import { useToast } from '../../composables/useToast';
import { 
  CreditCard, ShieldCheck, Lock, CheckCircle, ArrowRight, Building,
  Tag, Sparkles, Check, ArrowLeft
} from 'lucide-vue-next';

const route = useRoute();
const router = useRouter();
const authStore = useAuthStore();
const toast = useToast();

const orderId = route.params.orderId as string;
const loading = ref(false);
const paymentSuccess = ref(false);
const enrollmentsCreated = ref<string[]>([]);

// Promo code feature
const promoInput = ref('');
const appliedDiscount = ref(0);
const promoApplied = ref(false);

const basePrice = 89.00;
const finalPrice = computed(() => {
  const discountAmount = (basePrice * appliedDiscount.value) / 100;
  return Math.max(0, basePrice - discountAmount).toFixed(2);
});

function applyPromo() {
  const code = promoInput.value.trim().toUpperCase();
  if (code === 'WELCOME20') {
    appliedDiscount.value = 20;
    promoApplied.value = true;
    toast.success('Promo Code Applied!', '20% discount granted on your enrollment.');
  } else if (code === 'ACADEMY50') {
    appliedDiscount.value = 50;
    promoApplied.value = true;
    toast.success('Partner Code Applied!', '50% student scholarship discount granted.');
  } else {
    toast.error('Invalid Voucher Code', 'Try codes "WELCOME20" or "ACADEMY50"');
  }
}

async function completePayment() {
  loading.value = true;
  try {
    const res = await enrollmentApi.processPayment(orderId);
    paymentSuccess.value = true;
    enrollmentsCreated.value = res.enrollments;
    toast.success('Payment Cleared', 'Your course enrollment is now active.');
  } catch (err: any) {
    toast.error('Payment Failed', err.message || 'Payment simulation failed.');
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
  <div class="min-h-[calc(100vh-140px)] flex items-center justify-center p-4">
    <div class="max-w-md w-full glass-panel p-6 sm:p-8 shadow-2xl border border-slate-800 animate-fade-in relative">
      <div v-if="!paymentSuccess">
        <button @click="router.back()" class="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 transition mb-4">
          <ArrowLeft class="w-3.5 h-3.5" /> Cancel and Return
        </button>

        <div class="text-center mb-6">
          <div class="w-14 h-14 rounded-2xl bg-indigo-500/10 text-indigo-500 dark:text-indigo-400 mx-auto flex items-center justify-center border border-indigo-500/20 mb-3 shadow-lg">
            <CreditCard class="w-7 h-7" />
          </div>
          <h1 class="text-2xl font-bold text-white mb-1">Secure Course Checkout</h1>
          <p class="text-xs text-slate-400">Order ID: <span class="font-mono text-indigo-400">{{ orderId.slice(0, 18) }}...</span></p>
        </div>

        <!-- Order Summary Breakdown -->
        <div class="p-4 rounded-xl bg-slate-900/80 border border-slate-800 space-y-2.5 mb-5 text-xs">
          <div class="flex justify-between text-slate-400">
            <span>Course Access Entitlement</span>
            <span class="text-white font-semibold">Lifetime Masterclass</span>
          </div>
          <div class="flex justify-between text-slate-400">
            <span>Verified Certificate Credential</span>
            <span class="text-emerald-500 font-semibold">Included ($0)</span>
          </div>
          <div class="flex justify-between text-slate-400">
            <span>Payment Simulation Gateway</span>
            <span class="text-indigo-500 font-mono">Stripe Webhook Sandbox</span>
          </div>

          <div v-if="promoApplied" class="flex justify-between text-emerald-500 font-semibold pt-1 border-t border-slate-800/80">
            <span>Scholarship Discount ({{ appliedDiscount }}%)</span>
            <span>-${{ ((basePrice * appliedDiscount) / 100).toFixed(2) }}</span>
          </div>

          <div class="pt-2.5 border-t border-slate-800 flex justify-between text-base font-extrabold text-white">
            <span>Total Amount Due</span>
            <span class="text-emerald-500 font-mono">${{ finalPrice }} USD</span>
          </div>
        </div>

        <!-- Promo Code Input -->
        <div class="mb-5">
          <label class="block text-xs font-semibold text-slate-400 mb-1.5">Have a discount voucher?</label>
          <div class="flex gap-2">
            <input 
              v-model="promoInput"
              type="text" 
              placeholder="e.g. WELCOME20" 
              class="input-field text-xs uppercase font-mono py-2"
              :disabled="promoApplied"
            />
            <button 
              @click="applyPromo"
              :disabled="promoApplied || !promoInput.trim()"
              class="btn-secondary text-xs px-3 py-2 shrink-0 font-semibold"
            >
              <Check v-if="promoApplied" class="w-3.5 h-3.5 text-emerald-500" />
              <span v-else>Apply</span>
            </button>
          </div>
          <span v-if="!promoApplied" class="text-[11px] text-slate-400 mt-1 block">Tip: use code <span class="font-mono text-indigo-400 font-bold">WELCOME20</span> for 20% off.</span>
        </div>

        <button 
          @click="completePayment" 
          :disabled="loading" 
          class="btn-primary w-full justify-center py-3 text-sm font-bold shadow-xl shadow-indigo-500/25 cursor-pointer"
        >
          <span v-if="loading" class="flex items-center gap-2">
            <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
            Processing Sandbox Transaction...
          </span>
          <span v-else class="flex items-center gap-2">
            <Lock class="w-4 h-4" /> Pay ${{ finalPrice }} &amp; Activate Access
          </span>
        </button>

        <div class="mt-4 text-center text-[11px] text-slate-400 flex items-center justify-center gap-1.5">
          <ShieldCheck class="w-3.5 h-3.5 text-emerald-500" /> 256-Bit TLS End-To-End Encrypted Sandbox
        </div>
      </div>

      <!-- Payment Success State -->
      <div v-else class="text-center space-y-4 py-4 animate-fade-in">
        <div class="w-16 h-16 rounded-full bg-emerald-500/10 text-emerald-500 mx-auto flex items-center justify-center border border-emerald-500/30">
          <CheckCircle class="w-9 h-9" />
        </div>
        <h2 class="text-2xl font-bold text-white">Enrollment Activated!</h2>
        <p class="text-xs text-slate-400 leading-relaxed max-w-xs mx-auto">
          Your payment has cleared, the entitlement was granted in an atomic transaction, and full course access is now open.
        </p>

        <div class="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-400 font-medium">
          Receipt dispatched to {{ authStore.user?.email || 'your account' }}
        </div>

        <button @click="goToLearning" class="btn-primary w-full justify-center py-2.5 text-xs font-bold mt-2">
          Start Learning Now <ArrowRight class="w-4 h-4" />
        </button>
      </div>
    </div>
  </div>
</template>

