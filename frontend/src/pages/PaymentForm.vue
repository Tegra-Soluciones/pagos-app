<template>
  <div class="page-wrap w-full">
    <!-- Go back -->
    <div class="flex items-center gap-2 mb-5">
      <button class="btn-ghost px-2 py-1.5" @click="$router.back()">
        <ArrowLeftIcon class="w-4 h-4" />
        Volver
      </button>
      <span class="text-gray-300">/</span>
      <span class="text-sm text-gray-600 font-medium">{{ isEdit ? "Editar Pago" : "Nuevo Pago" }}</span>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- ── Form ── -->
      <div class="lg:col-span-2">
        <div class="card p-6 space-y-6">

          <!-- Error -->
          <div v-if="errorMsg" class="flex items-center gap-2 text-sm px-4 py-3 rounded-lg"
               style="background:#fef2f2;color:#b91c1c;border:1px solid #fecaca;">
            <AlertCircleIcon class="w-4 h-4 shrink-0" />
            {{ errorMsg }}
          </div>

          <!-- Información básica -->
          <div class="space-y-4">
            <p class="section-title flex items-center gap-2">
              <span class="w-4 h-0.5 rounded" style="background:#af282f;" />
              Información básica
            </p>
            <div>
              <label class="field-label">Título <span class="text-red-500 normal-case font-normal">*</span></label>
              <input v-model="form.title" type="text" class="field-input"
                     placeholder="Renta, Netflix, CFE, etc." required />
            </div>
            <div>
              <label class="field-label">Corresponde a</label>
              <input v-model="form.related_to" type="text" class="field-input"
                     placeholder="¿A qué servicio o concepto corresponde?" />
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="field-label">Categoría</label>
                <div class="flex gap-2">
                  <select v-model="form.category" class="field-select flex-1">
                    <option value="">Sin categoría</option>
                    <option v-for="c in categories" :key="c.name" :value="c.name">
                      {{ c.category_name }}
                    </option>
                  </select>
                  <button type="button" class="btn-outline px-3" title="Nueva categoría"
                          @click="showCatModal = true">
                    <PlusIcon class="w-4 h-4" />
                  </button>
                </div>
              </div>
              <div v-if="isEdit">
                <label class="field-label">Estado</label>
                <select v-model="form.status" class="field-select">
                  <option value="Pending">Pendiente</option>
                  <option value="Paid">Pagado</option>
                  <option value="Overdue">Vencido</option>
                  <option value="Cancelled">Cancelado</option>
                </select>
              </div>
            </div>
          </div>

          <div class="border-t border-gray-100" />

          <!-- Monto y fecha -->
          <div class="space-y-4">
            <p class="section-title flex items-center gap-2">
              <span class="w-4 h-0.5 rounded" style="background:#af282f;" />
              Monto y fecha
            </p>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div class="sm:col-span-2">
                <label class="field-label">Cantidad <span class="text-red-500 normal-case font-normal">*</span></label>
                <div class="relative">
                  <span class="absolute left-3.5 top-1/2 -translate-y-1/2 text-sm font-medium text-gray-400">$</span>
                  <input v-model.number="form.amount" type="number" step="0.01" min="0"
                         class="field-input pl-8" placeholder="0.00" required />
                </div>
              </div>
              <div>
                <label class="field-label">Moneda</label>
                <select v-model="form.currency" class="field-select">
                  <option value="MXN">MXN</option>
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                </select>
              </div>
            </div>
            <div>
              <label class="field-label">Fecha de Vencimiento <span class="text-red-500 normal-case font-normal">*</span></label>
              <input v-model="form.due_date" type="date" class="field-input sm:w-60" required />
              <p v-if="fridayDeadline" class="text-xs mt-1.5 flex items-center gap-1" style="color:#af282f;">
                <ClockIcon class="w-3.5 h-3.5" />
                Esta semana → pagar antes del viernes {{ fridayDeadline }}
              </p>
            </div>
          </div>

          <div class="border-t border-gray-100" />

          <!-- Recurrencia -->
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <RepeatIcon class="w-4 h-4" style="color:#af282f;" />
                <p class="text-sm font-semibold text-gray-800">Pago recurrente / suscripción</p>
              </div>
              <!-- Toggle -->
              <button type="button"
                      class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none"
                      :style="form.is_recurring ? 'background:#af282f' : 'background:#e5e7eb'"
                      @click="form.is_recurring = !form.is_recurring">
                <span class="inline-block w-4 h-4 transform rounded-full bg-white shadow transition-transform"
                      :class="form.is_recurring ? 'translate-x-6' : 'translate-x-1'" />
              </button>
            </div>

            <Transition name="slide-up">
              <div v-if="form.is_recurring" class="grid grid-cols-1 sm:grid-cols-3 gap-4 pl-6">
                <div>
                  <label class="field-label">Frecuencia</label>
                  <select v-model="form.recurrence_type" class="field-select">
                    <option value="Daily">Diario</option>
                    <option value="Weekly">Semanal</option>
                    <option value="Monthly">Mensual</option>
                    <option value="Quarterly">Trimestral</option>
                    <option value="Yearly">Anual</option>
                  </select>
                </div>
                <div>
                  <label class="field-label">Cada cuántos</label>
                  <input v-model.number="form.recurrence_interval" type="number" min="1"
                         class="field-input" placeholder="1" />
                </div>
                <div>
                  <label class="field-label">Fecha fin (opcional)</label>
                  <input v-model="form.recurrence_end_date" type="date" class="field-input" />
                </div>
                <p class="sm:col-span-3 text-xs text-gray-400 flex items-center gap-1">
                  <InfoIcon class="w-3.5 h-3.5" />
                  {{ recurrenceHint }} — Al marcar como pagado se genera automáticamente la siguiente ocurrencia.
                </p>
              </div>
            </Transition>
          </div>

          <div class="border-t border-gray-100" />

          <!-- Notas -->
          <div>
            <label class="field-label">Notas</label>
            <textarea v-model="form.notes" rows="3" class="field-textarea"
                      placeholder="Referencia de cuenta, proveedor, etc." />
          </div>

          <!-- Actions -->
          <div class="flex flex-col sm:flex-row gap-3 pt-1">
            <button type="button" class="btn-outline" @click="$router.back()">Cancelar</button>
            <button class="btn-primary flex-1" :disabled="saving" @click.prevent="submit">
              <span v-if="saving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              {{ saving ? "Guardando…" : isEdit ? "Guardar cambios" : "Crear Pago" }}
            </button>
          </div>
        </div>
      </div>

      <!-- ── Sidebar tips ── -->
      <div class="space-y-4">
        <div class="card p-4 border-l-4" style="border-left-color:#af282f;">
          <p class="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-1.5">
            <CalendarIcon class="w-3.5 h-3.5" style="color:#af282f;" />
            Regla de pago semanal
          </p>
          <p class="text-xs text-gray-500 leading-relaxed">
            Todos los pagos que venzan dentro de una semana (lunes a domingo) se procesan el
            <strong>viernes</strong> de esa semana. El dashboard te mostrará la alerta de límite.
          </p>
        </div>
        <div v-if="form.is_recurring" class="card p-4 border-l-4 border-emerald-400">
          <p class="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-1.5">
            <RepeatIcon class="w-3.5 h-3.5 text-emerald-600" />
            Recurrencia automática
          </p>
          <p class="text-xs text-gray-500 leading-relaxed">
            Cuando marques este pago como pagado, el sistema creará automáticamente el siguiente
            con la fecha calculada según la frecuencia elegida.
          </p>
        </div>
      </div>
    </div>

    <!-- Category modal -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="showCatModal" class="fixed inset-0 z-50 flex items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/30" @click="showCatModal = false" />
          <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-xs p-5 z-10">
            <h3 class="font-semibold text-gray-900 text-sm mb-4">Nueva Categoría</h3>
            <div class="space-y-3">
              <div>
                <label class="field-label">Nombre</label>
                <input v-model="newCat.name" class="field-input" placeholder="Servicios, Renta…" />
              </div>
              <div>
                <label class="field-label">Color</label>
                <input v-model="newCat.color" type="color"
                       class="h-10 w-full rounded-lg border border-gray-200 p-1 cursor-pointer" />
              </div>
              <div>
                <label class="field-label">Ícono Lucide (opcional)</label>
                <input v-model="newCat.icon" class="field-input" placeholder="home, car, wifi…" />
              </div>
            </div>
            <div class="flex gap-2 mt-4">
              <button class="btn-outline flex-1" @click="showCatModal = false">Cancelar</button>
              <button class="btn-primary flex-1" @click="saveCategory">Crear</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import {
  ArrowLeftIcon, PlusIcon, RepeatIcon, ClockIcon,
  AlertCircleIcon, InfoIcon, CalendarIcon,
} from "lucide-vue-next";
import { api } from "@/api";

const props = defineProps({ name: { type: String, default: null } });
const router = useRouter();
const categories = ref([]);
const saving = ref(false);
const errorMsg = ref("");
const showCatModal = ref(false);
const newCat = reactive({ name: "", color: "#af282f", icon: "" });
const isEdit = computed(() => !!props.name);

const today = new Date().toISOString().split("T")[0];
const form = reactive({
  title: "", related_to: "", amount: null, currency: "MXN",
  due_date: today, category: "", status: "Pending",
  is_recurring: false, recurrence_type: "Monthly",
  recurrence_interval: 1, recurrence_end_date: "", notes: "",
});

const recurrenceHint = computed(() => {
  const n = form.recurrence_interval || 1;
  const labels = { Daily: "día", Weekly: "semana", Monthly: "mes", Quarterly: "trimestre", Yearly: "año" };
  const unit = labels[form.recurrence_type] || "período";
  return n === 1 ? `Cada ${unit}` : `Cada ${n} ${unit}s`;
});

const fridayDeadline = computed(() => {
  if (!form.due_date) return null;
  const due = new Date(form.due_date + "T12:00:00");
  const today_d = new Date(); today_d.setHours(0, 0, 0, 0);
  if (due < today_d) return null;
  const dow = due.getDay();
  const daysFromMon = dow === 0 ? 6 : dow - 1;
  const mon = new Date(due); mon.setDate(due.getDate() - daysFromMon);
  const todayMon = new Date(today_d);
  todayMon.setDate(today_d.getDate() - (today_d.getDay() === 0 ? 6 : today_d.getDay() - 1));
  const todaySun = new Date(todayMon); todaySun.setDate(todayMon.getDate() + 6);
  if (due < todayMon || due > todaySun) return null;
  const fri = new Date(mon); fri.setDate(mon.getDate() + 4);
  return fri.toLocaleDateString("es-MX", { day: "numeric", month: "long" });
});

onMounted(async () => {
  await loadCategories();
  if (isEdit.value) {
    const data = await api.getPayment(props.name);
    Object.assign(form, {
      title: data.title, related_to: data.related_to || "",
      amount: data.amount, currency: data.currency || "MXN",
      due_date: data.due_date, category: data.category || "",
      status: data.status, is_recurring: !!data.is_recurring,
      recurrence_type: data.recurrence_type || "Monthly",
      recurrence_interval: data.recurrence_interval || 1,
      recurrence_end_date: data.recurrence_end_date || "",
      notes: data.notes || "",
    });
  }
});

async function loadCategories() {
  try { categories.value = await api.getCategories(); } catch {}
}

async function submit() {
  saving.value = true;
  errorMsg.value = "";
  try {
    const payload = { ...form };
    if (!payload.is_recurring) {
      payload.recurrence_type = "";
      payload.recurrence_interval = 1;
      payload.recurrence_end_date = "";
    }
    if (isEdit.value) {
      await api.updatePayment(props.name, payload);
      router.push(`/pagos/payments/${props.name}`);
    } else {
      const res = await api.createPayment(payload);
      router.push(`/pagos/payments/${res.name}`);
    }
  } catch (e) {
    errorMsg.value = e.message || "Error al guardar. Verifica los datos.";
    window.scrollTo({ top: 0, behavior: "smooth" });
  } finally {
    saving.value = false;
  }
}

async function saveCategory() {
  if (!newCat.name) return;
  try {
    await api.createCategory({ category_name: newCat.name, color: newCat.color, icon: newCat.icon });
    await loadCategories();
    form.category = newCat.name;
    showCatModal.value = false;
    Object.assign(newCat, { name: "", color: "#af282f", icon: "" });
  } catch (e) { alert(e.message || "Error al crear categoría"); }
}
</script>
