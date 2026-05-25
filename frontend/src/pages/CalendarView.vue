<template>
  <div class="page-wrap w-full">
    <div class="card p-4 sm:p-6 w-full">
      <FullCalendar ref="calRef" :options="calendarOptions" />
    </div>

    <!-- Event popover -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="selected"
             class="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4">
          <div class="absolute inset-0 bg-black/30" @click="selected = null" />
          <Transition name="slide-up">
            <div v-if="selected" class="relative bg-white rounded-xl shadow-2xl w-full max-w-sm z-10">
              <!-- Top accent bar -->
              <div class="h-1 w-full rounded-t-xl" :style="{ backgroundColor: selected.color }" />
              <div class="p-5">
                <div class="flex items-start justify-between mb-4 gap-3">
                  <div class="min-w-0">
                    <p class="font-bold text-gray-900 text-sm">{{ selected.title }}</p>
                    <p v-if="selected.related_to" class="text-xs text-gray-400 mt-0.5">{{ selected.related_to }}</p>
                  </div>
                  <div class="flex items-center gap-2">
                    <StatusBadge :status="selected.status" />
                    <button class="text-gray-400 hover:text-gray-600" @click="selected = null">
                      <XIcon class="w-4 h-4" />
                    </button>
                  </div>
                </div>

                <div class="space-y-2 text-sm divide-y divide-gray-100">
                  <div class="flex justify-between py-1.5">
                    <span class="text-gray-500 text-xs">Monto</span>
                    <span class="font-bold text-gray-900">{{ formatCurrency(selected.amount, selected.currency) }}</span>
                  </div>
                  <div class="flex justify-between py-1.5">
                    <span class="text-gray-500 text-xs">Vencimiento</span>
                    <span class="font-medium text-gray-700 text-xs">{{ formatDate(selected.due_date) }}</span>
                  </div>
                  <div v-if="selected.category" class="flex justify-between py-1.5">
                    <span class="text-gray-500 text-xs">Categoría</span>
                    <span class="text-xs text-gray-700">{{ selected.category }}</span>
                  </div>
                  <div v-if="selected.is_recurring" class="flex justify-between py-1.5">
                    <span class="text-gray-500 text-xs">Recurrencia</span>
                    <span class="text-xs font-medium flex items-center gap-1" style="color:#af282f;">
                      <RepeatIcon class="w-3 h-3" /> Sí
                    </span>
                  </div>
                </div>

                <div class="flex gap-2 mt-4">
                  <button class="btn-outline flex-1 text-xs"
                          @click="$router.push(`/pagos/payments/${selected.name}`); selected = null">
                    Ver detalle
                  </button>
                  <button v-if="selected.status !== 'Paid' && selected.status !== 'Cancelled'"
                          class="btn-success flex-1 text-xs"
                          @click="openMarkPaid">
                    <CheckCircle2Icon class="w-3.5 h-3.5" />
                    Pagado
                  </button>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <MarkPaidModal v-if="markPaidPayment"
                   :payment="markPaidPayment"
                   @close="markPaidPayment = null"
                   @paid="onPaid" />
  </div>
</template>

<script setup>
import { ref } from "vue";
import FullCalendar from "@fullcalendar/vue3";
import dayGridPlugin from "@fullcalendar/daygrid";
import interactionPlugin from "@fullcalendar/interaction";
import listPlugin from "@fullcalendar/list";
import esLocale from "@fullcalendar/core/locales/es";
import { CheckCircle2Icon, RepeatIcon, XIcon } from "lucide-vue-next";
import { api } from "@/api";
import StatusBadge from "@/components/StatusBadge.vue";
import MarkPaidModal from "@/components/MarkPaidModal.vue";

const selected = ref(null);
const markPaidPayment = ref(null);
const calRef = ref(null);

async function fetchEvents(info, successCallback, failureCallback) {
  try {
    const events = await api.getCalendarEvents(
      info.startStr.split("T")[0],
      info.endStr.split("T")[0],
    );
    successCallback(Array.isArray(events) ? events : []);
  } catch (e) {
    console.error("Calendar error:", e);
    failureCallback(e);
  }
}

const calendarOptions = {
  plugins: [dayGridPlugin, interactionPlugin, listPlugin],
  locale: esLocale,
  initialView: "dayGridMonth",
  headerToolbar: { left: "prev,next today", center: "title", right: "dayGridMonth,listMonth" },
  events: fetchEvents,
  eventClick({ event }) {
    const ep = event.extendedProps;
    selected.value = {
      name: event.id,
      title: ep.title_clean || event.title.split(" $")[0],
      ...ep,
      due_date: event.startStr,
      color: event.backgroundColor,
    };
  },
  height: "auto",
  displayEventTime: false,
  eventDisplay: "block",
};

function openMarkPaid() {
  markPaidPayment.value = { ...selected.value };
  selected.value = null;
}
async function onPaid() {
  markPaidPayment.value = null;
  calRef.value?.getApi()?.refetchEvents();
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
