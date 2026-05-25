import frappe
from frappe.model.document import Document
from frappe.utils import today, add_days, add_months, getdate


class PagoProgramado(Document):
    def before_insert(self):
        if not self.owner_user:
            self.owner_user = frappe.session.user

    def validate(self):
        if self.is_recurring and not self.recurrence_type:
            frappe.throw("Selecciona el tipo de recurrencia para pagos recurrentes.")
        if self.is_recurring and self.recurrence_end_date:
            if getdate(self.recurrence_end_date) < getdate(self.due_date):
                frappe.throw("La fecha de fin de recurrencia debe ser posterior a la fecha de vencimiento.")
        # Auto-mark overdue
        if self.status == "Pending" and getdate(self.due_date) < getdate(today()):
            self.status = "Overdue"

    def get_next_due_date(self):
        """Calculate next occurrence from current due_date."""
        base = getdate(self.due_date)
        interval = self.recurrence_interval or 1
        t = self.recurrence_type

        if t == "Daily":
            return add_days(base, interval)
        elif t == "Weekly":
            return add_days(base, 7 * interval)
        elif t == "Monthly":
            return add_months(base, interval)
        elif t == "Quarterly":
            return add_months(base, 3 * interval)
        elif t == "Yearly":
            return add_months(base, 12 * interval)
        return None
