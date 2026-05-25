<template>
  <div class="flex items-center gap-2">
    <span class="w-1 h-5 rounded-full shrink-0" :style="{ background: color }" />
    <h3 class="section-title">{{ label }}</h3>
    <span v-if="count !== undefined"
          class="text-xs font-semibold px-2 py-0.5 rounded-full ml-1"
          :style="{ background: bgColor, color: color }">
      {{ count }}
    </span>
  </div>
</template>

<script setup>
import { computed } from "vue";
const props = defineProps({
  label: String,
  count: { type: Number, default: undefined },
  color: { type: String, default: "#6b7280" },
});
// Lighten the color for background — just use opacity trick via hex
const bgColor = computed(() => props.color + "18"); // ~10% opacity
</script>
