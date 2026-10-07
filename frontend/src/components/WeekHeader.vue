<template>
  <div class="flex items-center justify-between border-b border-gray-200 pb-1.5">
    <div class="flex items-baseline gap-2">
      <h3 class="text-sm font-semibold text-gray-800">
        Pagar el viernes {{ week.friday.toLocaleDateString("es-MX", { day: "numeric", month: "short" }) }}
      </h3>
    </div>
    <span class="text-xs text-gray-500">
      {{ week.items.length }} · <span class="font-semibold text-gray-800">{{ fmt(week.total) }}</span>
    </span>
  </div>
</template>

<script setup>
defineProps({ week: Object, fmt: Function });
</script>
