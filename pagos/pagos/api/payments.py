"""
API endpoints for the Pagos SPA.

Business rule: payments due Mon–Sun of a given week must be
paid no later than the Friday of that same week.

Recurring logic:
  When a recurring payment is first created, we pre-generate all
  occurrences for the next 12 months (or until recurrence_end_date).
  When one is marked paid, we top-up so the next 12 months always have
  pending occurrences.
"""

import frappe
from frappe.utils import today, getdate, add_days, add_months, nowdate
from datetime import date, timedelta


# ─── helpers ──────────────────────────────────────────────────────────────────

def _week_bounds(ref=None):
    if ref is None:
        ref = getdate(today())
    monday = ref - timedelta(days=ref.weekday())
    sunday = monday + timedelta(days=6)
    friday = monday + timedelta(days=4)
    return monday, sunday, friday


def _status_color(status):
    return {"Pending": "yellow", "Paid": "green", "Overdue": "red", "Cancelled": "gray"}.get(status, "gray")


def _next_date_from(doc_or_dict, from_date):
    """Calculate next due date after from_date using the recurrence settings."""
    interval = int(doc_or_dict.get("recurrence_interval") or 1)
    t = doc_or_dict.get("recurrence_type")
    base = getdate(from_date)

    if t == "Daily":     return add_days(base, interval)
    if t == "Weekly":    return add_days(base, 7 * interval)
    if t == "Monthly":   return add_months(base, interval)
    if t == "Quarterly": return add_months(base, 3 * interval)
    if t == "Yearly":    return add_months(base, 12 * interval)
    return None


def _pre_generate_occurrences(source_name, months_ahead=12):
    """
    Pre-generate all future pending occurrences for a recurring payment.
    Walks every date from source.due_date to the cutoff, filling any gaps.
    This handles cases where far-future records exist but intermediate months are missing.
    """
    source = frappe.get_doc("Payment Schedule", source_name)
    if not source.is_recurring:
        return

    cutoff = getdate(today()) + timedelta(days=months_ahead * 30)
    end_date = getdate(source.recurrence_end_date) if source.recurrence_end_date else None

    # Walk ALL dates from the source's due_date forward to the cutoff.
    # Always advance current_date whether or not we inserted, so gaps get filled.
    current_date = getdate(source.due_date)
    generated = []
    for _ in range(200):  # hard cap
        next_d = _next_date_from(source, current_date)
        if not next_d:
            break
        next_d = getdate(next_d)
        if next_d > cutoff:
            break
        if end_date and next_d > end_date:
            break

        # Only insert if this date+title doesn't exist yet
        already = frappe.db.exists("Payment Schedule", {
            "title": source.title,
            "due_date": next_d.isoformat(),
            "is_recurring": 1,
        })
        current_date = next_d  # always advance to walk through gaps
        if already:
            continue

        new_doc = frappe.get_doc({
            "doctype": "Payment Schedule",
            "title": source.title,
            "related_to": source.related_to,
            "category": source.category,
            "amount": source.amount,
            "currency": source.currency or "MXN",
            "due_date": next_d.isoformat(),
            "status": "Pending",
            "is_recurring": 1,
            "recurrence_type": source.recurrence_type,
            "recurrence_interval": source.recurrence_interval or 1,
            "recurrence_end_date": source.recurrence_end_date,
            "notes": source.notes,
            "owner_user": source.owner_user,
        })
        new_doc.flags.skip_pre_generate = True
        new_doc.insert(ignore_permissions=True)
        generated.append(new_doc.name)

    if generated:
        frappe.db.commit()
    return generated


# ─── dashboard ────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_dashboard():
    today_d = getdate(today())
    monday, sunday, friday = _week_bounds(today_d)

    # This week — Pending/Overdue only
    this_week = frappe.get_all(
        "Payment Schedule",
        filters={
            "due_date": ["between", [monday.isoformat(), sunday.isoformat()]],
            "status": ["in", ["Pending", "Overdue"]],
        },
        fields=["name", "title", "amount", "currency", "due_date", "status",
                "category", "related_to", "is_recurring", "recurrence_type"],
        order_by="due_date asc",
    )
    for p in this_week:
        p["payment_deadline"] = friday.isoformat()
        p["days_until_friday"] = (friday - today_d).days
        p["is_urgent"] = today_d >= friday
        p["color"] = _status_color(p["status"])

    # Next 30 days — Pending only
    next_start = (sunday + timedelta(days=1)).isoformat()
    next_end = (today_d + timedelta(days=30)).isoformat()
    upcoming = frappe.get_all(
        "Payment Schedule",
        filters={
            "due_date": ["between", [next_start, next_end]],
            "status": ["in", ["Pending", "Overdue"]],
        },
        fields=["name", "title", "amount", "currency", "due_date", "status",
                "category", "related_to", "is_recurring", "recurrence_type"],
        order_by="due_date asc",
    )
    for p in upcoming:
        p["color"] = _status_color(p["status"])

    # Overdue before this week
    overdue = frappe.get_all(
        "Payment Schedule",
        filters={"due_date": ["<", monday.isoformat()], "status": "Overdue"},
        fields=["name", "title", "amount", "currency", "due_date", "status",
                "category", "related_to"],
        order_by="due_date asc",
    )
    for p in overdue:
        p["color"] = "red"
        p["days_overdue"] = (today_d - getdate(p["due_date"])).days

    # Paid this month
    month_start = date(today_d.year, today_d.month, 1).isoformat()
    paid_month = frappe.get_all(
        "Payment Schedule",
        filters={
            "due_date": ["between", [month_start, today_d.isoformat()]],
            "status": "Paid",
        },
        fields=["name", "title", "amount", "currency", "due_date", "status",
                "category", "related_to", "is_recurring"],
        order_by="due_date desc",
    )

    counts = {
        "pending": frappe.db.count("Payment Schedule", {"status": "Pending"}),
        "overdue":  frappe.db.count("Payment Schedule", {"status": "Overdue"}),
        "paid_this_month": len(paid_month),
    }

    return {
        "this_week": this_week,
        "upcoming": upcoming,
        "overdue": overdue,
        "paid_this_month": paid_month,
        "counts": counts,
        "week_total": sum(p.get("amount") or 0 for p in this_week),
        "week_bounds": {
            "monday": monday.isoformat(),
            "friday": friday.isoformat(),
            "sunday": sunday.isoformat(),
        },
        "today": today_d.isoformat(),
    }


# ─── calendar ─────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_calendar_events(start, end):
    payments = frappe.get_all(
        "Payment Schedule",
        filters={
            "due_date": ["between", [start, end]],
            "status": ["not in", ["Cancelled"]],
        },
        fields=["name", "title", "amount", "currency", "due_date", "status",
                "category", "related_to", "is_recurring"],
        order_by="due_date asc",
    )

    color_map = {
        "Pending": "#af282f",
        "Paid":    "#059669",
        "Overdue": "#dc2626",
        "Cancelled": "#9ca3af",
    }

    events = []
    for p in payments:
        color = color_map.get(p["status"], "#9ca3af")
        events.append({
            "id": p["name"],
            "title": f"{p['title']}  ${p['amount']:,.0f}",
            "start": p["due_date"],
            "allDay": True,
            "backgroundColor": color,
            "borderColor": color,
            "textColor": "#ffffff",
            "extendedProps": {
                "name": p["name"],
                "title_clean": p["title"],
                "amount": p["amount"],
                "currency": p["currency"],
                "status": p["status"],
                "category": p["category"],
                "related_to": p["related_to"],
                "is_recurring": p["is_recurring"],
            },
        })
    return events


# ─── payments list ────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_payments_by_month(year=None, month=None, status=None, category=None):
    """
    Returns all payments for a given month, grouped into pending and paid.
    Defaults to current month.
    """
    today_d = getdate(today())
    year  = int(year)  if year  else today_d.year
    month = int(month) if month else today_d.month

    month_start = date(year, month, 1)
    # Last day of the month
    if month == 12:
        month_end = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        month_end = date(year, month + 1, 1) - timedelta(days=1)

    filters = {"due_date": ["between", [month_start.isoformat(), month_end.isoformat()]]}
    if status:
        filters["status"] = status
    if category:
        filters["category"] = category

    payments = frappe.get_all(
        "Payment Schedule",
        filters=filters,
        fields=["name", "title", "related_to", "amount", "currency", "due_date",
                "status", "category", "is_recurring", "recurrence_type",
                "recurrence_interval", "notes"],
        order_by="due_date asc",
    )
    for p in payments:
        p["color"] = _status_color(p["status"])

    pending = [p for p in payments if p["status"] in ("Pending", "Overdue")]
    paid    = [p for p in payments if p["status"] == "Paid"]
    cancelled = [p for p in payments if p["status"] == "Cancelled"]

    return {
        "pending": pending,
        "paid": paid,
        "cancelled": cancelled,
        "all": payments,
        "month_start": month_start.isoformat(),
        "month_end": month_end.isoformat(),
        "year": year,
        "month": month,
        "total_pending": sum(p["amount"] or 0 for p in pending),
        "total_paid":    sum(p["amount"] or 0 for p in paid),
    }


@frappe.whitelist()
def get_payment(name):
    doc = frappe.get_doc("Payment Schedule", name)
    frappe.has_permission("Payment Schedule", "read", doc=doc, throw=True)
    result = doc.as_dict()
    result["color"] = _status_color(doc.status)
    result["logs"] = frappe.get_all(
        "Payment Log",
        filters={"payment_schedule": name},
        fields=["name", "paid_date", "amount", "currency", "notes", "creation"],
        order_by="paid_date desc",
    )
    return result


# ─── CRUD ─────────────────────────────────────────────────────────────────────

@frappe.whitelist(methods=["POST"])
def create_payment(data):
    import json
    if isinstance(data, str):
        data = json.loads(data)

    doc = frappe.get_doc({"doctype": "Payment Schedule", **data})
    doc.flags.skip_pre_generate = True
    doc.insert(ignore_permissions=True)
    frappe.db.commit()

    # Pre-generate future occurrences for recurring payments
    if doc.is_recurring:
        _pre_generate_occurrences(doc.name, months_ahead=12)

    return {"name": doc.name, "message": "Pago creado exitosamente."}


@frappe.whitelist(methods=["POST"])
def update_payment(name, data):
    import json
    if isinstance(data, str):
        data = json.loads(data)

    doc = frappe.get_doc("Payment Schedule", name)
    frappe.has_permission("Payment Schedule", "write", doc=doc, throw=True)
    doc.flags.skip_pre_generate = True
    doc.update(data)
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name, "message": "Actualizado."}


@frappe.whitelist(methods=["POST"])
def mark_paid(name, paid_date=None, amount=None, notes=None):
    """
    Mark a Payment Schedule as Paid and log the payment.
    For recurring payments, ensures the next 12 months of occurrences exist.
    """
    from frappe.utils import today as _today

    doc = frappe.get_doc("Payment Schedule", name)
    frappe.has_permission("Payment Schedule", "write", doc=doc, throw=True)

    # 1. Mark as Paid directly — reliable, no hook dependency
    frappe.db.set_value("Payment Schedule", name, "status", "Paid")
    frappe.db.commit()

    # 2. Create payment log
    paid_amount = float(amount) if amount else (doc.amount or 0)
    log = frappe.get_doc({
        "doctype": "Payment Log",
        "payment_schedule": name,
        "paid_date": paid_date or _today(),
        "amount": paid_amount,
        "currency": doc.currency or "MXN",
        "notes": notes or "",
    })
    log.insert(ignore_permissions=True)
    frappe.db.commit()

    # 3. For recurring payments, top-up future occurrences
    if doc.is_recurring:
        _pre_generate_occurrences(name, months_ahead=12)

    return {
        "message": "Pago registrado.",
        "log_name": log.name,
    }


@frappe.whitelist(methods=["POST"])
def delete_payment(name):
    doc = frappe.get_doc("Payment Schedule", name)
    frappe.has_permission("Payment Schedule", "delete", doc=doc, throw=True)
    frappe.delete_doc("Payment Schedule", name)
    frappe.db.commit()
    return {"message": "Pago eliminado."}


# ─── repair ───────────────────────────────────────────────────────────────────

@frappe.whitelist()
def repair_recurring_payments(months_ahead=12):
    """Fill gaps in recurring payment occurrences for all active recurring payments."""
    # Find one representative per recurring group (the earliest record per title+type)
    sources = frappe.get_all(
        "Payment Schedule",
        filters={"is_recurring": 1, "status": ["not in", ["Cancelled"]]},
        fields=["name", "title", "recurrence_type"],
        order_by="due_date asc",
    )
    seen = set()
    total_generated = []
    for s in sources:
        key = (s["title"], s["recurrence_type"])
        if key in seen:
            continue
        seen.add(key)
        result = _pre_generate_occurrences(s["name"], months_ahead=int(months_ahead))
        if result:
            total_generated.extend(result)
    return {"generated": len(total_generated), "names": total_generated}


# ─── categories ───────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_categories():
    return frappe.get_all(
        "Payment Category",
        fields=["name", "category_name", "color", "icon"],
        order_by="category_name asc",
    )


@frappe.whitelist(methods=["POST"])
def create_category(category_name, color=None, icon=None):
    doc = frappe.get_doc({
        "doctype": "Payment Category",
        "category_name": category_name,
        "color": color,
        "icon": icon,
    })
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"name": doc.name}
