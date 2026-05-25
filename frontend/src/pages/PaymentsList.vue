<template>
  <div class="w-full min-h-full">

    <!-- ── Month navigation bar ── -->
    <div class="w-full bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-3
                flex flex-wrap items-center justify-between gap-3 sticky top-0 z-10">
      <!-- Month picker -->
      <div class="flex items-center gap-2">
        <button class="btn-outline px-2.5 py-1.5 text-xs" @click="changeMonth(-1)">
          <ChevronLeftIcon class="w-4 h-4" />
        </button>
        <h2 class="text-sm font-semibold text-gray-900 min-w-[130px] text-center capitalize">
          {{ monthLabel }}
        </h2>
        <button class="btn-outline px-2.5 py-1.5 text-xs" @click="changeMonth(1)">
          <ChevronRightIcon class="w-4 h-4" />
        </button>
        <button v-if="!isCurrentMonth" class="btn-ghost text-xs px-2.5 py-1.5" @click="goToday">
          Hoy
        </button>
      </div>

      <!-- Totals -->
      <div v-if="monthData" class="flex items-center gap-4 text-sm">
        <div class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-amber-400" />
          <span class="text-gray-500 text-xs">Por pagar</span>
          <span class="font-bold text-gray-900">{{ fmt(monthData.total_pending) }}</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-emerald-400" />
          <span class="text-gray-500 text-xs">Pagado</span>
          <span class="font-bold text-emerald-700">{{ fmt(monthData.total_paid) }}</span>
        </div>
      </div>

      <!-- Filters -->
      <div class="flex items-center gap-2 ml-auto">
        <select v-model="filterCategory" class="field-select text-xs w-36 py-1.5" @change="fetchMonth">
          <option value="">Todas las categorías</option>
          <option v-for="c in categories" :key="c.name" :value="c.name">{{ c.category_name }}</option>
        </select>
        <RouterLink to="/pagos/payments/new" class="btn-primary text-xs py-1.5 px-3">
          <PlusIcon class="w-3.5 h-3.5" /> Nuevo
        </RouterLink>
      </div>
    </div>

    <!-- ── Content ── -->
    <div class="page-wrap space-y-8">

      <!-- Loading -->
      <div v-if="loading" class="flex justify-center py-16">
        <div class="w-6 h-6 border-2 border-t-transparent rounded-full animate-spin"
             style="border-color:#af282f;border-top-color:transparent;" />
      </div>

      <template v-else-if="monthData">

        <!-- ── Pendientes ── -->
        <section>
          <SectionHeader label="Pendientes de pago"
                         :count="monthData.pending.length"
                         color="#af282f" />
          <div v-if="!monthData.pending.length"
               class="card px-6 py-8 text-center mt-3">
            <CheckCircle2Icon class="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            <p class="text-sm text-gray-500">Sin pagos pendientes en {{ monthLabel }}</p>
          </div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 mt-3">
            <PaymentCard v-for="p in monthData.pending" :key="p.name" :payment="p"
                         @mark-paid="openMarkPaid(p)" @refresh="fetchMonth" />
          </div>
        </section>

        <!-- ── Pagados ── -->
        <section>
          <SectionHeader label="Pagados"
                         :count="monthData.paid.length"
                         color="#059669" />
          <div v-if="!monthData.paid.length"
               class="card px-6 py-6 text-center mt-3 border-dashed">
            <p class="text-sm text-gray-400">Sin pagos registrados aún en {{ monthLabel }}</p>
          </div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 mt-3">
            <PaymentCard v-for="p in monthData.paid" :key="p.name" :payment="p" />
          </div>
        </section>

        <!-- ── Cancelados (solo si hay) ── -->
        <section v-if="monthData.cancelled.length">
          <SectionHeader label="Cancelados" :count="monthData.cancelled.length" color="#9ca3af" />
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 mt-3">
            <PaymentCard v-for="p in monthData.cancelled" :key="p.name" :payment="p" />
          </div>
        </section>

        <!-- Empty month -->
        <div v-if="!monthData.all.length" class="card px-8 py-14 text-center">
          <CalendarOffIcon class="w-10 h-10 text-gray-300 mx-auto mb-3" />
          <p class="text-sm font-medium text-gray-600">Sin pagos en {{ monthLabel }}</p>
          <RouterLink to="/pagos/payments/new" class="btn-primary inline-flex mt-4">
            <PlusIcon class="w-4 h-4" /> Registrar pago
          </RouterLink>
        </div>
      </template>
    </div>

    <MarkPaidModal v-if="markPaidTarget" :payment="markPaidTarget"
                   @close="markPaidTarget = null"
                   @paid="onPaid" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { RouterLink } from "vue-router";
import { PlusIcon, ChevronLeftIcon, ChevronRightIcon,
         CheckCircle2Icon, CalendarOffIcon } from "lucide-vue-next";
import { api } from "@/api";
import PaymentCard from "@/components/PaymentCard.vue";
import MarkPaidModal from "@/components/MarkPaidModal.vue";
import SectionHeader from "@/components/SectionHeader.vue";

const today = new Date();
const currentYear  = ref(today.getFullYear());
const currentMonth = ref(today.getMonth() + 1); // 1-based

const monthData = ref(null);
const categories = ref([]);
const loading = ref(false);
const filterCategory = ref("");
const markPaidTarget = ref(null);

const isCurrentMonth = computed(
  () => currentYear.value === today.getFullYear() && currentMonth.value === today.getMonth() + 1
);

const monthLabel = computed(() =>
  new Date(currentYear.value, currentMonth.value - 1, 1)
    .toLocaleDateString("es-MX", { month: "long", year: "numeric" })
);

function changeMonth(delta) {
  let m = currentMonth.value + delta;
  let y = currentYear.value;
  if (m < 1) { m = 12; y--; }
  if (m > 12) { m = 1; y++; }
  currentMonth.value = m;
  currentYear.value = y;
  fetchMonth();
}
function goToday() {
  currentMonth.value = today.getMonth() + 1;
  currentYear.value = today.getFullYear();
  fetchMonth();
}

async function fetchMonth() {
  loading.value = true;
  try {
    const params = {};
    if (filterCategory.value) params.category = filterCategory.value;
    monthData.value = await api.getPaymentsByMonth(
      currentYear.value, currentMonth.value, params
    );
  } finally {
    loading.value = false;
  }
}

function openMarkPaid(p) { markPaidTarget.value = p; }
async function onPaid() { markPaidTarget.value = null; await fetchMonth(); }

onMounted(async () => {
  categories.value = await api.getCategories();
  await fetchMonth();
});

function fmt(a, c = "MXN") {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: c }).format(a || 0);
}
</script>
