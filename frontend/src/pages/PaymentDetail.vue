<template>
  <div class="page-wrap w-full">

    <!-- Loading -->
    <div v-if="loading" class="flex justify-center py-20">
      <div class="w-7 h-7 border-2 border-t-transparent rounded-full animate-spin"
           style="border-color:#af282f;border-top-color:transparent;" />
    </div>

    <template v-else-if="payment">
      <!-- Back -->
      <div class="flex items-center gap-2 mb-5">
        <button class="btn-ghost px-2 py-1.5" @click="$router.back()">
          <ArrowLeftIcon class="w-4 h-4" /> Volver
        </button>
        <span class="text-gray-300">/</span>
        <span class="text-sm text-gray-500 truncate">{{ payment.title }}</span>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <!-- ── Main info ── -->
        <div class="lg:col-span-2 space-y-5">

          <!-- Header card -->
          <div class="card p-5">
            <div class="flex items-start justify-between gap-4">
              <div class="min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <StatusBadge :status="payment.status" />
                  <span v-if="payment.is_recurring"
                        class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full"
                        style="background:#fdf2f2;color:#af282f;">
                    <RepeatIcon class="w-3 h-3" />
                    {{ recurrenceLabel }}
                  </span>
                </div>
                <h1 class="text-xl font-bold text-gray-900 mt-1">{{ payment.title }}</h1>
                <p v-if="payment.related_to" class="text-sm text-gray-500 mt-0.5">{{ payment.related_to }}</p>
              </div>
              <div class="shrink-0 text-right">
                <p class="text-3xl font-bold text-gray-900">{{ formatCurrency(payment.amount, payment.currency) }}</p>
                <p class="text-xs text-gray-400 mt-1">{{ formatDate(payment.due_date) }}</p>
              </div>
            </div>

            <!-- Week deadline -->
            <div v-if="weekInfo" class="mt-4 inline-flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium"
                 :style="weekInfo.urgent
                   ? 'background:#fef2f2;color:#b91c1c;border:1px solid #fecaca'
                   : 'background:#fffbeb;color:#92400e;border:1px solid #fde68a'">
              <ClockIcon class="w-3.5 h-3.5" />
              Límite de pago: viernes {{ weekInfo.fridayLabel }}
              <span v-if="weekInfo.urgent" class="font-bold">— ¡Hoy!</span>
            </div>
          </div>

          <!-- Detail grid -->
          <div class="card p-5">
            <p class="section-title mb-4 flex items-center gap-2">
              <span class="w-4 h-0.5 rounded" style="background:#af282f;" />
              Detalles
            </p>
            <dl class="grid grid-cols-2 sm:grid-cols-3 gap-y-4 gap-x-6 text-sm">
              <div v-if="payment.category">
                <dt class="text-xs text-gray-400 mb-0.5">Categoría</dt>
                <dd class="font-medium text-gray-900">{{ payment.category }}</dd>
              </div>
              <div v-if="payment.is_recurring">
                <dt class="text-xs text-gray-400 mb-0.5">Frecuencia</dt>
                <dd class="font-medium text-gray-900">
                  Cada {{ payment.recurrence_interval }} {{ recurrenceLabel }}
                </dd>
              </div>
              <div v-if="payment.recurrence_end_date">
                <dt class="text-xs text-gray-400 mb-0.5">Fin de recurrencia</dt>
                <dd class="font-medium text-gray-900">{{ formatDate(payment.recurrence_end_date) }}</dd>
              </div>
              <div v-if="payment.currency">
                <dt class="text-xs text-gray-400 mb-0.5">Moneda</dt>
                <dd class="font-medium text-gray-900">{{ payment.currency }}</dd>
              </div>
              <div v-if="payment.owner_user">
                <dt class="text-xs text-gray-400 mb-0.5">Responsable</dt>
                <dd class="font-medium text-gray-900">{{ payment.owner_user }}</dd>
              </div>
            </dl>
            <div v-if="payment.notes" class="mt-4 pt-4 border-t border-gray-100">
              <dt class="text-xs text-gray-400 mb-1">Notas</dt>
              <dd class="text-sm text-gray-700 whitespace-pre-wrap">{{ payment.notes }}</dd>
            </div>
          </div>

          <!-- Action buttons -->
          <div class="flex flex-wrap gap-3">
            <button v-if="payment.status !== 'Paid' && payment.status !== 'Cancelled'"
                    class="btn-success"
                    @click="showMarkPaid = true">
              <CheckCircle2Icon class="w-4 h-4" />
              Marcar como Pagado
            </button>
            <RouterLink :to="`/pagos/payments/${payment.name}/edit`" class="btn-outline">
              <PencilIcon class="w-4 h-4" /> Editar
            </RouterLink>
            <button class="btn-danger ml-auto" @click="confirmDelete">
              <Trash2Icon class="w-4 h-4" /> Eliminar
            </button>
          </div>
        </div>

        <!-- ── Payment history ── -->
        <div>
          <div class="card p-5">
            <p class="section-title flex items-center gap-2 mb-4">
              <HistoryIcon class="w-3.5 h-3.5 text-gray-400" />
              Historial de pagos
            </p>
            <div v-if="!payment.logs?.length" class="text-sm text-gray-400 py-4 text-center">
              Sin pagos registrados.
            </div>
            <div v-else class="space-y-2">
              <div v-for="log in payment.logs" :key="log.name"
                   class="flex items-start justify-between gap-3 p-3 bg-emerald-50 rounded-lg border border-emerald-100">
                <div class="flex items-center gap-2">
                  <CheckCircle2Icon class="w-4 h-4 text-emerald-500 shrink-0" />
                  <div>
                    <p class="text-xs font-semibold text-emerald-900">{{ formatDate(log.paid_date) }}</p>
                    <p v-if="log.notes" class="text-xs text-emerald-600 mt-0.5">{{ log.notes }}</p>
                  </div>
                </div>
                <p class="text-xs font-bold text-emerald-700 shrink-0">
                  {{ formatCurrency(log.amount, log.currency) }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>

    <MarkPaidModal v-if="showMarkPaid && payment"
                   :payment="payment"
                   @close="showMarkPaid = false"
                   @paid="onPaid" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { RouterLink, useRouter } from "vue-router";
import {
  ArrowLeftIcon, CheckCircle2Icon, PencilIcon, Trash2Icon,
  RepeatIcon, HistoryIcon, ClockIcon,
} from "lucide-vue-next";
import { api } from "@/api";
import StatusBadge from "@/components/StatusBadge.vue";
import MarkPaidModal from "@/components/MarkPaidModal.vue";

const props = defineProps({ name: { type: String, required: true } });
const router = useRouter();
const payment = ref(null);
const loading = ref(true);
const showMarkPaid = ref(false);

const recurrenceLabels = {
  Daily: "día(s)", Weekly: "semana(s)", Monthly: "mes(es)",
  Quarterly: "trimestre(s)", Yearly: "año(s)",
};
const recurrenceLabel = computed(() => recurrenceLabels[payment.value?.recurrence_type] || "");

const weekInfo = computed(() => {
  if (!payment.value?.due_date) return null;
  if (!["Pending", "Overdue"].includes(payment.value.status)) return null;
  const due = new Date(payment.value.due_date + "T12:00:00");
  const dow = due.getDay();
  const daysFromMon = dow === 0 ? 6 : dow - 1;
  const mon = new Date(due); mon.setDate(due.getDate() - daysFromMon);
  const fri = new Date(mon); fri.setDate(mon.getDate() + 4);
  return {
    fridayLabel: fri.toLocaleDateString("es-MX", { day: "numeric", month: "long" }),
    urgent: new Date() >= fri,
  };
});

onMounted(async () => {
  try { payment.value = await api.getPayment(props.name); }
  finally { loading.value = false; }
});

async function onPaid() {
  showMarkPaid.value = false;
  loading.value = true;
  try { payment.value = await api.getPayment(props.name); }
  finally { loading.value = false; }
}

async function confirmDelete() {
  if (!confirm(`¿Eliminar "${payment.value.title}"? No se puede deshacer.`)) return;
  await api.deletePayment(props.name);
  router.push("/pagos");
}

function formatCurrency(a, c = "MXN") {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: c }).format(a || 0);
}
function formatDate(d) {
  if (!d) return "";
  return new Date(d + "T12:00:00").toLocaleDateString("es-MX", {
    day: "numeric", month: "long", year: "numeric",
  });
}
</script>
