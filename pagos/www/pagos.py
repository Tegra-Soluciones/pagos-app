import frappe
from frappe.sessions import get_csrf_token

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/pagos"
        raise frappe.Redirect

    context.no_header = 1
    context.no_breadcrumbs = 1
    context.site_name = frappe.local.site
    context.csrf_token = get_csrf_token()
