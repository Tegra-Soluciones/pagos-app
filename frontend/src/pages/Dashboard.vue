<template>
  <div class="w-full min-h-full">

    <!-- Loading -->
    <div v-if="loading" class="flex items-center justify-center h-64">
      <div class="w-7 h-7 border-2 border-t-transparent rounded-full animate-spin"
           style="border-color:#af282f;border-top-color:transparent;" />
    </div>

    <template v-else-if="data">
      <!-- ── Week summary bar ── -->
      <div class="w-full bg-white border-b border-gray-200 px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex flex-wrap gap-4 items-center justify-between">
          <!-- Week label -->
          <div class="flex items-center gap-3">
            <div class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
                 style="background:#fdf2f2;">
              <CalendarIcon class="w-5 h-5" style="color:#af282f;" />
            </div>
            <div>
              <p class="text-xs text-gray-500">Semana actual · {{ weekLabel }}</p>
              <p class="text-xs font-semibold" style="color:#af282f;">
                Límite de pago: viernes {{ formatDateLong(data.week_bounds.friday) }}
              </p>
            </div>
          </div>

          <!-- KPI chips -->
          <div class="flex flex-wrap gap-2">
            <div v-for="kpi in kpis" :key="kpi.label"
                 class="flex items-center gap-2 bg-gray-50 border border-gray-100 rounded-lg px-3 py-1.5">
              <span class="text-lg font-bold leading-none"
                    :style="kpi.color ? `color:${kpi.color}` : 'color:#111827'">{{ kpi.value }}</span>
              <span class="text-xs text-gray-400 leading-tight">{{ kpi.label }}</span>
            </div>
          </div>

          <!-- Week total + New -->
          <div class="flex items-center gap-4 ml-auto">
            <div class="text-right hidden sm:block">
              <p class="text-xs text-gray-400">Total semana</p>
              <p class="text-lg font-bold text-gray-900">{{ formatCurrency(data.week_total) }}</p>
            </div>
            <RouterLink to="/pagos/payments/new" class="btn-primary">
              <PlusIcon class="w-4 h-4" /> Nuevo pago
            </RouterLink>
          </div>
        </div>
      </div>

      <!-- ── Content ── -->
      <div class="page-wrap space-y-8">

        <!-- Urgent banner -->
        <div v-if="isUrgentWeek && data.this_week.length"
             class="flex items-start gap-3 border rounded-xl px-4 py-3"
             style="background:#fef2f2;border-color:#fca5a5;">
          <AlertTriangleIcon class="w-5 h-5 shrink-0 mt-0.5" style="color:#b91c1c;" />
          <div>
            <p class="text-sm font-semibold" style="color:#991b1b;">¡Hoy es el día límite!</p>
            <p class="text-xs mt-0.5" style="color:#b91c1c;">
              Los pagos de esta semana debían pagarse a más tardar hoy viernes.
            </p>
          </div>
        </div>

        <!-- ── Esta semana (solo Pending/Overdue) ── -->
        <section>
          <SectionHeader label="Esta semana — por pagar" :count="data.this_week.length"
                         color="#af282f" />
          <div v-if="!data.this_week.length" class="card px-6 py-8 text-center">
            <CheckCircle2Icon class="w-8 h-8 text-emerald-400 mx-auto mb-2" />
            <p class="text-sm text-gray-500">Sin pagos pendientes esta semana 🎉</p>
          </div>
          <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3 mt-3">
            <PaymentCard v-for="p in data.this_week" :key="p.name" :payment="p"
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

        <!-- Empty total -->
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
import { PlusIcon, AlertTriangleIcon, CheckCircle2Icon, WalletIcon, CalendarIcon } from "lucide-vue-next";
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

const isUrgentWeek = computed(() => {
  if (!data.value?.week_bounds) return false;
  return new Date() >= new Date(data.value.week_bounds.friday + "T12:00:00");
});

const weekLabel = computed(() => {
  if (!data.value?.week_bounds) return "";
  const fmt = (d) => new Date(d + "T12:00:00").toLocaleDateString("es-MX", { day: "numeric", month: "short" });
  return `${fmt(data.value.week_bounds.monday)} – ${fmt(data.value.week_bounds.sunday)}`;
});

const kpis = computed(() => {
  const c = data.value?.counts || {};
  return [
    { value: c.pending || 0,         label: "Pendientes", color: "#d97706" },
    { value: c.overdue  || 0,        label: "Vencidos",   color: "#dc2626" },
    { value: c.paid_this_month || 0, label: "Pagados mes", color: "#059669" },
    { value: data.value?.this_week?.length || 0, label: "Esta semana", color: "#af282f" },
  ];
});

const isEmpty = computed(() =>
  !data.value?.this_week.length && !data.value?.upcoming.length &&
  !data.value?.overdue.length && !data.value?.paid_this_month.length
);

function formatCurrency(a, c = "MXN") {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: c }).format(a || 0);
}
function formatDateLong(d) {
  if (!d) return "";
  return new Date(d + "T12:00:00").toLocaleDateString("es-MX", { day: "numeric", month: "long" });
}
</script>
