import frappe
from frappe.model.document import Document


class PaymentLog(Document):
    # Status update is handled directly in the API (mark_paid).
    # This class intentionally left minimal.
    pass
