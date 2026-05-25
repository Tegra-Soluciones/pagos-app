<template>
  <Teleport to="body">
    <Transition name="fade">
      <div class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4">
        <div class="absolute inset-0 bg-black/30" @click="$emit('close')" />
        <Transition name="slide-up">
          <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-md z-10">
            <!-- Header -->
            <div class="flex items-center gap-3 px-5 pt-5 pb-4 border-b border-gray-100">
              <div class="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center">
                <CheckCircle2Icon class="w-5 h-5 text-emerald-600" />
              </div>
              <div>
                <h2 class="text-sm font-semibold text-gray-900">Registrar Pago</h2>
                <p class="text-xs text-gray-400 mt-0.5 truncate max-w-xs">{{ payment.title }}</p>
              </div>
              <button class="ml-auto p-1 text-gray-400 hover:text-gray-600" @click="$emit('close')">
                <XIcon class="w-4 h-4" />
              </button>
            </div>

            <!-- Form -->
            <form @submit.prevent="submit" class="px-5 py-4 space-y-4">
              <p v-if="errorMsg" class="text-xs text-red-600 bg-red-50 px-3 py-2 rounded-lg">{{ errorMsg }}</p>

              <div class="grid grid-cols-2 gap-3">
                <div>
                  <label class="field-label">Fecha</label>
                  <input v-model="form.paid_date" type="date" class="field-input" required />
                </div>
                <div>
                  <label class="field-label">Monto</label>
                  <input v-model.number="form.amount" type="number" step="0.01"
                         class="field-input" required />
                </div>
              </div>
              <div>
                <label class="field-label">Notas (opcional)</label>
                <textarea v-model="form.notes" rows="2"
                          class="field-textarea"
                          placeholder="Banco, referencia, etc." />
              </div>
              <div class="flex gap-3 pt-1">
                <button type="button" class="btn-outline flex-1" @click="$emit('close')">Cancelar</button>
                <button type="submit" class="btn-success flex-1" :disabled="saving">
                  <span v-if="saving" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  <CheckCircle2Icon v-else class="w-4 h-4" />
                  {{ saving ? "Guardando…" : "Confirmar" }}
                </button>
              </div>
            </form>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, reactive } from "vue";
import { CheckCircle2Icon, XIcon } from "lucide-vue-next";
import { api } from "@/api";

const props = defineProps({ payment: { type: Object, required: true } });
const emit = defineEmits(["close", "paid"]);

const today = new Date().toISOString().split("T")[0];
const form = reactive({ paid_date: today, amount: props.payment.amount, notes: "" });
const saving = ref(false);
const errorMsg = ref("");

async function submit() {
  saving.value = true;
  errorMsg.value = "";
  try {
    const res = await api.markPaid(props.payment.name, {
      paid_date: form.paid_date,
      amount: String(form.amount),
      notes: form.notes,
    });
    emit("paid", res);
  } catch (e) {
    errorMsg.value = e.message || "Error al registrar el pago";
  } finally {
    saving.value = false;
  }
}
</script>
