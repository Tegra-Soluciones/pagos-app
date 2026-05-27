<template>
  <div class="w-full min-h-full">

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="w-7 h-7 border-2 border-t-transparent rounded-full animate-spin"
           style="border-color:#af282f;border-top-color:transparent;" />
    </div>

    <template v-else-if="data">
      <!-- ── Summary bar ── -->
      <div class="w-full bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex flex-wrap gap-4 items-center justify-between">
          <!-- KPI chips -->
          <div class="flex flex-wrap gap-2">
            <div v-for="kpi in kpis" :key="kpi.label"
                 class="flex items-center gap-2 bg-gray-50 border border-gray-100 rounded-lg px-3 py-1.5">
              <span class="text-lg font-bold leading-none"
                    :style="kpi.color ? `color:${kpi.color}` : 'color:#111827'">{{ kpi.value }}</span>
              <span class="text-xs text-gray-400 leading-tight">{{ kpi.label }}</span>
            </div>
          </div>

          <!-- New payment button -->
          <div class="ml-auto">
            <RouterLink to="/pagos/payments/new" class="btn-primary">
              <PlusIcon class="w-4 h-4" /> Nuevo pago
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- ── Content ── -->
      <div class="page-wrap space-y-8">

        <!-- ── Vencen pronto ── -->
        <section v-if="data.due_soon.length">
          <SectionHeader label="Vencen pronto" :count="data.due_soon.length" color="#d97706" />
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 mt-3">
            <PaymentCard v-for="p in data.due_soon" :key="p.name" :payment="p"
                         @mark-paid="openMarkPaid(p)" @refresh="reloadDashboard" />
          </div>
        </section>

        <!-- ── Vencidos ── -->
        <section v-if="data.overdue.length">
          <SectionHeader label="Vencidos" :count="data.overdue.length" color="#dc2626" />
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 mt-3">
            <PaymentCard v-for="p in data.overdue" :key="p.name" :payment="p"
                         @mark-paid="openMarkPaid(p)" @refresh="reloadDashboard" />
          </div>
        </section>

        <!-- ── Próximos 30 días ── -->
        <section v-if="data.upcoming.length">
          <SectionHeader label="Próximos 30 días" :count="data.upcoming.length" color="#6b7280" />
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 mt-3">
            <PaymentCard v-for="p in data.upcoming" :key="p.name" :payment="p"
                         @mark-paid="openMarkPaid(p)" @refresh="reloadDashboard" />
          </div>
        </section>

        <!-- ── Pagados este mes ── -->
        <section v-if="data.paid_this_month.length">
          <SectionHeader label="Pagados este mes" :count="data.paid_this_month.length" color="#059669" />
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 mt-3">
            <PaymentCard v-for="p in data.paid_this_month" :key="p.name" :payment="p" />
          </div>
        </section>

        <!-- Empty state -->
        <div v-if="isEmpty" class="card px-8 py-16 text-center">
          <div class="w-14 h-14 rounded-xl mx-auto mb-4 flex items-center justify-center"
               style="background:#fdf2f2;">
            <WalletIcon class="w-7 h-7" style="color:#af282f;" />
          </div>
          <h3 class="text-base font-semibold text-gray-700">Sin pagos registrados</h3>
          <p class="text-sm text-gray-400 mt-1 mb-5">Empieza registrando tu primer pago.</p>
          <RouterLink to="/pagos/payments/new" class="btn-primary inline-flex">
            <PlusIcon class="w-4 h-4" /> Registrar primer pago
          </RouterLink>
        </div>
      </div>
    </template>

    <MarkPaidModal v-if="markPaidTarget" :payment="markPaidTarget"
                   @close="markPaidTarget = null"
                   @paid="onPaid" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { RouterLink } from "vue-router";
import { PlusIcon, WalletIcon } from "lucide-vue-next";
import { api } from "@/api";
import PaymentCard from "@/components/PaymentCard.vue";
import MarkPaidModal from "@/components/MarkPaidModal.vue";
import SectionHeader from "@/components/SectionHeader.vue";

const data = ref(null);
const loading = ref(true);
const markPaidTarget = ref(null);

async function reloadDashboard() {
  loading.value = true;
  try { data.value = await api.getDashboard(); }
  finally { loading.value = false; }
}
onMounted(reloadDashboard);

function openMarkPaid(p) { markPaidTarget.value = p; }
async function onPaid() { markPaidTarget.value = null; await reloadDashboard(); }

const kpis = computed(() => {
  const c = data.value?.counts || {};
  return [
    { value: c.due_soon       || 0, label: "Vencen pronto", color: "#d97706" },
    { value: c.overdue        || 0, label: "Vencidos",      color: "#dc2626" },
    { value: c.pending        || 0, label: "Pendientes",    color: "#6b7280" },
    { value: c.paid_this_month || 0, label: "Pagados mes",  color: "#059669" },
  ];
});

const isEmpty = computed(() =>
  !data.value?.due_soon.length && !data.value?.overdue.length &&
  !data.value?.upcoming.length && !data.value?.paid_this_month.length
);
</script>
