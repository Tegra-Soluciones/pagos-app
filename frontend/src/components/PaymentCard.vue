<template>
  <div class="card-hover p-4 flex items-start gap-3.5">

    <!-- Status icon — click goes to detail -->
    <div class="shrink-0 w-9 h-9 rounded-lg flex items-center justify-center cursor-pointer"
         :class="iconBg" @click="goDetail">
      <component :is="statusIcon" class="w-4.5 h-4.5" style="width:18px;height:18px;" :class="iconColor" />
    </div>

    <!-- Body -->
    <div class="flex-1 min-w-0 cursor-pointer" @click="goDetail">
      <div class="flex items-start justify-between gap-2">
        <div class="min-w-0">
          <p class="font-semibold text-gray-900 text-sm truncate">{{ payment.title }}</p>
          <p v-if="payment.related_to" class="text-xs text-gray-400 mt-0.5 truncate">
            {{ payment.related_to }}
          </p>
        </div>
        <div class="shrink-0 text-right">
          <p class="font-bold text-gray-900 text-sm">{{ fmt(payment.amount, payment.currency) }}</p>
          <p class="text-xs text-gray-400 mt-0.5">{{ fmtDate(payment.due_date) }}</p>
        </div>
      </div>

      <!-- Tags -->
      <div class="flex flex-wrap items-center gap-1.5 mt-2">
        <StatusBadge :status="payment.status" />
        <span v-if="payment.is_recurring"
              class="inline-flex items-center gap-1 text-xs font-medium px-2 py-0.5 rounded-full"
              style="background:#fdf2f2;color:#af282f;">
          <RepeatIcon class="w-3 h-3" />{{ recurrenceLabel }}
        </span>
        <span v-if="payment.category"
              class="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded-full">
          {{ payment.category }}
        </span>
      </div>

      <!-- Due soon alert -->
      <div v-if="payment.days_until_due !== undefined && payment.days_until_due >= 0" class="mt-2">
        <span class="inline-flex items-center gap-1.5 text-xs font-medium px-2 py-0.5 rounded-md"
              :style="payment.days_until_due === 0
                ? 'background:#fef2f2;color:#b91c1c;border:1px solid #fecaca'
                : 'background:#fffbeb;color:#92400e;border:1px solid #fde68a'">
          <ClockIcon class="w-3 h-3" />
          {{ dueSoonLabel(payment.days_until_due) }}
        </span>
      </div>
      <div v-if="payment.days_overdue" class="mt-2">
        <span class="inline-flex items-center gap-1.5 text-xs font-semibold px-2 py-0.5 rounded-md"
              style="background:#fef2f2;color:#b91c1c;border:1px solid #fecaca;">
          <AlertCircleIcon class="w-3 h-3" />{{ payment.days_overdue }} días vencido
        </span>
      </div>
    </div>

    <!-- Quick pay button (only for Pending/Overdue) -->
    <button v-if="payment.status === 'Pending' || payment.status === 'Overdue'"
            class="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center transition-colors
                   border border-gray-200 hover:border-emerald-300 hover:bg-emerald-50"
            title="Marcar como pagado"
            @click.stop="$emit('mark-paid', payment)">
      <CheckCircle2Icon class="w-4 h-4 text-gray-400 hover:text-emerald-600" />
    </button>
  </div>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import {
  RepeatIcon, ClockIcon, AlertCircleIcon, CheckCircle2Icon,
  CheckCircle2Icon as DoneIcon, AlertTriangleIcon, TimerIcon, BanIcon,
} from "lucide-vue-next";
import StatusBadge from "./StatusBadge.vue";

const props = defineProps({ payment: { type: Object, required: true } });
const emit = defineEmits(["mark-paid", "refresh"]);
const router = useRouter();
function goDetail() { router.push(`/pagos/payments/${props.payment.name}`); }

const recurrenceLabels = {
  Daily: "Diario", Weekly: "Semanal", Monthly: "Mensual",
  Quarterly: "Trimestral", Yearly: "Anual",
};
const recurrenceLabel = computed(() => recurrenceLabels[props.payment.recurrence_type] || "Recurrente");

const iconBg = computed(() => ({
  "bg-amber-50":   props.payment.status === "Pending",
  "bg-emerald-50": props.payment.status === "Paid",
  "bg-red-50":     props.payment.status === "Overdue",
  "bg-gray-100":   props.payment.status === "Cancelled",
}));
const iconColor = computed(() => ({
  "text-amber-500":   props.payment.status === "Pending",
  "text-emerald-600": props.payment.status === "Paid",
  "text-red-600":     props.payment.status === "Overdue",
  "text-gray-400":    props.payment.status === "Cancelled",
}));
const statusIcon = computed(() => ({
  Pending: TimerIcon, Paid: CheckCircle2Icon,
  Overdue: AlertTriangleIcon, Cancelled: BanIcon,
}[props.payment.status] || TimerIcon));

function fmt(a, c = "MXN") {
  return new Intl.NumberFormat("es-MX", { style: "currency", currency: c }).format(a || 0);
}
function fmtDate(d) {
  if (!d) return "";
  return new Date(d + "T12:00:00").toLocaleDateString("es-MX", {
    weekday: "short", day: "numeric", month: "short",
  });
}
function dueSoonLabel(days) {
  if (days === 0) return "¡Vence hoy!";
  if (days === 1) return "Vence mañana";
  return `Vence en ${days} días`;
}
</script>
