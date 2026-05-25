import frappe


def has_app_permission():
    return frappe.has_permission("Payment Schedule", "read")
