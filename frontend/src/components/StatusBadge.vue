<template>
  <span class="badge" :class="`badge-${status.toLowerCase()}`">
    <span class="w-1.5 h-1.5 rounded-full shrink-0" :class="dotClass" />
    {{ labels[status] || status }}
  </span>
</template>

<script setup>
import { computed } from "vue";
const props = defineProps({ status: { type: String, required: true } });
const labels = { Pending: "Pendiente", Paid: "Pagado", Overdue: "Vencido", Cancelled: "Cancelado" };
const dotClass = computed(() => ({
  "bg-amber-500":   props.status === "Pending",
  "bg-emerald-500": props.status === "Paid",
  "bg-red-500":     props.status === "Overdue",
  "bg-gray-400":    props.status === "Cancelled",
}));
</script>
