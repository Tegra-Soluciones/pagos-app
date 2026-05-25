import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { api } from "@/api";

export const usePaymentsStore = defineStore("payments", () => {
  const dashboard = ref(null);
  const categories = ref([]);
  const loading = ref(false);
  const error = ref(null);

  async function fetchDashboard() {
    loading.value = true;
    error.value = null;
    try {
      dashboard.value = await api.getDashboard();
    } catch (e) {
      error.value = e.message || "Error al cargar el dashboard";
    } finally {
      loading.value = false;
    }
  }

  async function fetchCategories() {
    try {
      categories.value = await api.getCategories();
    } catch {}
  }

  const categoryMap = computed(() => {
    const m = {};
    for (const c of categories.value) m[c.name] = c;
    return m;
  });

  return { dashboard, categories, categoryMap, loading, error, fetchDashboard, fetchCategories };
});
