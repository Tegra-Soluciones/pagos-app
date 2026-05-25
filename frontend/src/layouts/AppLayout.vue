<template>
  <div class="flex h-screen w-screen overflow-hidden bg-gray-50">

    <!-- Mobile overlay -->
    <Transition name="fade">
      <div v-if="sidebarOpen && isMobile"
           class="fixed inset-0 z-30 bg-black/30 lg:hidden"
           @click="sidebarOpen = false" />
    </Transition>

    <!-- ── Sidebar ── -->
    <aside
      class="fixed lg:static inset-y-0 left-0 z-40 flex flex-col w-56 bg-white border-r border-gray-200 shrink-0
             transition-transform duration-300 ease-out lg:translate-x-0"
      :class="sidebarOpen ? 'translate-x-0' : '-translate-x-full'"
    >
      <!-- Logo -->
      <div class="flex items-center gap-2.5 px-4 py-4 border-b border-gray-100">
        <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0"
             style="background-color: #af282f;">
          <WalletIcon class="w-4.5 h-4.5 text-white" style="width:18px;height:18px;" />
        </div>
        <div class="min-w-0">
          <p class="font-bold text-gray-900 text-sm leading-tight">Pagos</p>
          <p class="text-xs text-gray-400 truncate">Recordatorio</p>
        </div>
        <button class="ml-auto lg:hidden p-1 text-gray-400 hover:text-gray-600" @click="sidebarOpen = false">
          <XIcon class="w-4 h-4" />
        </button>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto">
        <RouterLink
          v-for="item in navItems"
          :key="item.name"
          :to="item.to"
          class="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-100"
          :class="isActive(item)
            ? 'text-[#af282f] bg-[#fdf2f2]'
            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'"
          @click="isMobile && (sidebarOpen = false)"
        >
          <component :is="item.icon"
                     class="w-4 h-4 shrink-0"
                     :style="isActive(item) ? 'color:#af282f' : ''" />
          {{ item.label }}
          <!-- Active indicator -->
          <span v-if="isActive(item)"
                class="ml-auto w-1.5 h-1.5 rounded-full"
                style="background-color:#af282f;" />
        </RouterLink>
      </nav>

      <!-- New payment -->
      <div class="px-2 py-3 border-t border-gray-100">
        <RouterLink
          to="/pagos/payments/new"
          class="btn-primary w-full"
          @click="isMobile && (sidebarOpen = false)"
        >
          <PlusIcon class="w-4 h-4" />
          Nuevo Pago
        </RouterLink>
      </div>
    </aside>

    <!-- ── Main ── -->
    <div class="flex-1 flex flex-col min-w-0 overflow-hidden">

      <!-- Top bar -->
      <header class="w-full bg-white border-b border-gray-200 px-4 sm:px-6 h-13 flex items-center justify-between shrink-0 shadow-none"
              style="height:52px;">
        <div class="flex items-center gap-3">
          <button class="lg:hidden p-1.5 rounded-lg text-gray-500 hover:bg-gray-100"
                  @click="sidebarOpen = true">
            <MenuIcon class="w-5 h-5" />
          </button>
          <div>
            <h1 class="text-sm font-semibold text-gray-900 leading-none">{{ pageTitle }}</h1>
            <p class="text-xs text-gray-400 mt-0.5 hidden sm:block">{{ todayFormatted }}</p>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <a href="/app" class="btn-ghost text-xs px-2.5 py-1.5 hidden sm:inline-flex">
            <ExternalLinkIcon class="w-3.5 h-3.5" />
            ERPNext
          </a>
        </div>
      </header>

      <!-- Page -->
      <main class="flex-1 overflow-y-auto w-full">
        <Transition name="fade" mode="out-in">
          <RouterView :key="$route.fullPath" />
        </Transition>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from "vue";
import { RouterLink, RouterView, useRoute } from "vue-router";
import {
  LayoutDashboardIcon, CalendarIcon, ListIcon, PlusIcon,
  WalletIcon, XIcon, MenuIcon, ExternalLinkIcon,
} from "lucide-vue-next";

const route = useRoute();
const sidebarOpen = ref(false);
const isMobile = ref(false);
function checkMobile() { isMobile.value = window.innerWidth < 1024; }
onMounted(() => { checkMobile(); window.addEventListener("resize", checkMobile); });
onUnmounted(() => window.removeEventListener("resize", checkMobile));

const navItems = [
  { name: "Dashboard", label: "Dashboard",       to: "/pagos",          icon: LayoutDashboardIcon },
  { name: "Calendar",  label: "Calendario",      to: "/pagos/calendar", icon: CalendarIcon },
  { name: "Payments",  label: "Todos los pagos", to: "/pagos/payments", icon: ListIcon },
];

const pageTitles = {
  Dashboard: "Dashboard", Calendar: "Calendario", Payments: "Pagos",
  NewPayment: "Nuevo Pago", EditPayment: "Editar Pago", PaymentDetail: "Detalle",
};
const pageTitle = computed(() => pageTitles[route.name] || "Pagos");

function isActive(item) {
  if (item.name === "Dashboard") return route.path === "/pagos" || route.path === "/pagos/";
  if (item.name === "Payments") return route.path.startsWith("/pagos/payments");
  return route.path.startsWith(item.to);
}

const todayFormatted = computed(() =>
  new Date().toLocaleDateString("es-MX", { weekday: "long", day: "numeric", month: "long" })
);
</script>
