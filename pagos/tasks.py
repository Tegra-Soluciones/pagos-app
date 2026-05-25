"""Scheduled background tasks."""

import frappe
from frappe.utils import today, getdate, add_days


def update_overdue_payments():
    """Mark Pending payments as Overdue if their due_date has passed."""
    today_d = getdate(today())
    overdue = frappe.get_all(
        "Pago Programado",
        filters={"status": "Pending", "due_date": ["<", today_d.isoformat()]},
        fields=["name"],
    )
    for p in overdue:
        frappe.db.set_value("Pago Programado", p["name"], "status", "Overdue")
    frappe.db.commit()


def generate_recurring_payments():
    """
    For recurring payments that were just paid (status=Paid) and have no
    future pending occurrence yet, pre-generate the next one.
    This is a safety net; the primary generation happens in mark_paid().
    """
    pass  # Handled on mark_paid via the API
