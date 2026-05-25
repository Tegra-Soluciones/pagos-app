app_name = "pagos"
app_title = "Pagos"
app_publisher = "Ixoom"
app_description = "Recordatorio y calendarización de pagos — SPA sobre ERPNext v15"
app_email = "hola@ixoom.com.mx"
app_license = "mit"
app_version = "0.1.0"

required_apps = ["frappe"]

# ── Desk / Apps screen icon ────────────────────────────────────────────────────
add_to_apps_screen = [
    {
        "name": "pagos",
        "logo": "/assets/pagos/images/logo.svg",
        "title": "Pagos",
        "route": "/pagos",
        "has_permission": "pagos.utils.has_app_permission",
    }
]

# ── SPA sub-route catch-all ────────────────────────────────────────────────────
website_route_rules = [
    {"from_route": "/pagos/<path:app_path>", "to_route": "pagos"},
]

# ── Scheduled tasks ────────────────────────────────────────────────────────────
scheduler_events = {
    "daily": [
        "pagos.tasks.update_overdue_payments",
        "pagos.tasks.generate_recurring_payments",
    ],
}
