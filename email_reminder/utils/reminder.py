import frappe
import json
from frappe import _
import re

@frappe.whitelist()
def send_email(message, recipients, reminder_schedule_date, doctype, docname, site):
    
    error_message = []
    hasError = False
    if not message:
        error_message.append(f'<li>{_("Message")}</li>')
        hasError = True

    if not reminder_schedule_date:
        error_message.append(f'<li>{_("Reminder Date and Time")}</li>')
        hasError = True
    try:
        if isinstance(recipients, str):
            emails = json.loads(recipients)
        elif isinstance(recipients, list):
            emails = recipients
        else:
            json.loads(recipients)
        
        if not emails:
            error_message.append(f'<li>{_("Recipients Email")}</li>')
            hasError = True

        if hasError:
            frappe.msgprint(f'{_("Mandatory fields required for Email Reminder")}<ul>{"".join(error_message)}</ul>')
            return "Error No Log"
        
        doctype_fr = doctype.lower().replace(' ', '-')
        document_link = f"<a href='{site}/app/{doctype_fr}/{docname}'>Open Document</a>"
        message = f"""{doctype}<br>" Reminder on Document {docname}<br><br>"{message}<br><br>"
                {document_link}"""
        
        create_reminder(message, emails, doctype, docname,reminder_schedule_date)

        frappe.sendmail(
            recipients=emails,
            subject=_("Details"),
            message=_(message),
            send_after=reminder_schedule_date,
        )

        return "Success"
    
    except json.JSONDecodeError:
        frappe.log_error(f"JSON decoding error: {frappe.get_traceback()}")
    
    except frappe.exceptions.ValidationError as ve:
        frappe.log_error(f"Validation Error: {ve}\n{frappe.get_traceback()}")

    except frappe.exceptions.LinkValidationError as lve:
        frappe.log_error(f"Link Validation Error: {lve}\n{frappe.get_traceback()}")

    except frappe.exceptions.PermissionError as pe:
        frappe.log_error(f"Permission Error: {pe}\n{frappe.get_traceback()}")


@frappe.whitelist()
def create_reminder(message, emails, doctype, docname,reminder_schedule_date):
    reminder = frappe.get_doc(
        {
            "doctype": "Reminder",
            "reminder": message,
            "document_type": doctype,
            "document_no": docname,
            "reminder_schedule_date":reminder_schedule_date,
            "emails": get_emails(emails)
        }
    )
    reminder.flags.ignore_permissions = True
    reminder.insert()
    reminder.submit()


def get_emails(emails):
    emails_list = []
    invalid_emails = []
    for email in emails:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            invalid_emails.append(email)
        else:
            emails_list.append({"email": email})

    if invalid_emails:
        error_message = f"Invalid Emails: {', '.join(invalid_emails)}"
        frappe.throw(_(error_message))

    return emails_list

