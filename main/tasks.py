from celery import shared_task
from django.utils import timezone
from .models import Invoice, WAInfo
from .utils import send_wa_message, format_libyan_number

@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 30})
def send_pending_invoices_reminder(self):
    pending_invoices = Invoice.objects.filter(status="pending")
    wa_infos = WAInfo.objects.filter(is_active=True)

    if not pending_invoices.exists() or not wa_infos.exists():
        return "No pending invoices or no active WA contacts"

    for wa in wa_infos:
        if not wa.contact_number:
            continue

        for invoice in pending_invoices:
            message = wa.reminder_message or (
                f"🔔 تذكير بفاتورة معلقة\n"
                f"رقم الفاتورة: {invoice.id}\n"
                f"العميل: {invoice.name}\n"
                f"الهاتف: {format_libyan_number(invoice.phone)}\n"
                f"الإجمالي: {invoice.total} د.ل\n"
                f"تاريخ الإنشاء: {invoice.created_at.date()}"
            )

            send_wa_message(wa.contact_number, message)

    return f"Sent reminders for {pending_invoices.count()} invoices"
