import { createRouter, createWebHistory } from "vue-router";

const routes = [
  {
    path: "/pagos",
    component: () => import("@/layouts/AppLayout.vue"),
    children: [
      {
        path: "",
        name: "Dashboard",
        component: () => import("@/pages/Dashboard.vue"),
      },
      {
        path: "calendar",
        name: "Calendar",
        component: () => import("@/pages/CalendarView.vue"),
      },
      {
        path: "payments",
        name: "Payments",
        component: () => import("@/pages/PaymentsList.vue"),
      },
      {
        path: "payments/new",
        name: "NewPayment",
        component: () => import("@/pages/PaymentForm.vue"),
      },
      {
        path: "payments/:name",
        name: "PaymentDetail",
        component: () => import("@/pages/PaymentDetail.vue"),
        props: true,
      },
      {
        path: "payments/:name/edit",
        name: "EditPayment",
        component: () => import("@/pages/PaymentForm.vue"),
        props: true,
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    redirect: "/pagos",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
