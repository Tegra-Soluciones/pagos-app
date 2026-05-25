import { frappeRequest } from "frappe-ui";

const BASE = "pagos.pagos.api.payments";

function get(method, params = {}) {
  return frappeRequest({ url: `/api/method/${BASE}.${method}`, params });
}
function post(method, params = {}) {
  return frappeRequest({ url: `/api/method/${BASE}.${method}`, method: "POST", params });
}

export const api = {
  getDashboard:        ()           => get("get_dashboard"),
  getCalendarEvents:   (start, end) => get("get_calendar_events", { start, end }),

  // Month-based list (new)
  getPaymentsByMonth:  (year, month, params = {}) =>
    get("get_payments_by_month", { year, month, ...params }),

  getPayment:          (name)       => get("get_payment", { name }),
  createPayment:       (data)       => post("create_payment", { data: JSON.stringify(data) }),
  updatePayment:       (name, data) => post("update_payment", { name, data: JSON.stringify(data) }),
  markPaid:            (name, opts = {}) => post("mark_paid", { name, ...opts }),
  deletePayment:       (name)       => post("delete_payment", { name }),

  getCategories:       ()           => get("get_categories"),
  createCategory:      (data)       => post("create_category", data),
};
