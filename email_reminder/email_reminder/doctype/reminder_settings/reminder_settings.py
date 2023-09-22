# Copyright (c) 2023, Hamza Abuabada and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from packaging import version

custom_js_script = """
frappe.ui.form.on('%s', {
    send_email(frm) {
        frappe.call({
            method: "email_reminder.utils.reminder.send_email",
            args: {
                message: frm.doc._message || null,
                recipients: frm.doc.rmn_emails && frm.doc.rmn_emails.length > 0 ? frm.doc.rmn_emails.map(field => field.email).filter(Boolean) : [],
                reminder_schedule_date: frm.doc.rmn_date_and_time || null,
                doctype: frm.doc.doctype || null,
                docname: frm.doc.name || null,
                site: window.origin,
            },
            async: false,
            callback: function(r) {
                var message = r.message === 'Success' ?
                    {
                        message: __('Email added to Email Queue'),
                        indicator: 'green'
                    } :
                    {
                        message: __('Error in sending email, Check Error Log or contact technical team'),
                        indicator: 'red'
                    };

                r.message === 'Error No Log' ? '' : frappe.show_alert(message, 5);
            }
        })
    }
})
"""

class ReminderSettings(Document):
    @frappe.whitelist()
    def generate_fields(self, docs):
        if not isinstance(docs,list) or len(docs) == 0:
            return
        self.disable_fields(docs)
        self.disable_scripts(docs)
        for doc in docs:
            if not doc or frappe.db.exists("Doctype", doc):
                continue
            fields = self.get_fields(doc)
            create_custom_fields(fields)
            self.enable_scripts(doc)

        self.save(Document)

    def disable_fields(self, docs):
        for doc in docs:
            custom_fields = frappe.get_all("Custom Field", filters={
                "fieldtype": "Tab Break",
                "fieldname": f"{doc.lower()}_messages"
            })
            if not custom_fields:
                return
            for field in custom_fields:
                custom_field = frappe.get_doc("Custom Field", field.name)
                custom_field.hidden = 1
                custom_field.save()

    def disable_scripts(self, docs):
        for doc in docs:
            script_doc = frappe.db.exists("Client Script", f'{doc} Email Reminder')
            if script_doc:
                script_doc = frappe.get_doc("Client Script", script_doc)
                script_doc.enabled = 0
                script_doc.save()

    def enable_scripts(self, doc):
        script_doc = frappe.db.exists("Client Script", f'{doc} Email Reminder')
        if script_doc:
            script_doc = frappe.get_doc("Client Script", script_doc)
            script_doc.update({
                "dt": doc,
                "view": "Form",
                "enabled": 1,
                "script": custom_js_script %doc,
            })
            script_doc.save(ignore_permissions = True)
        else:
            script_doc = frappe.new_doc("Client Script")
            script_doc.update({
                "__newname": f'{doc} Email Reminder',
                "dt": doc,
                "view": "Form",
                "enabled": 1,
                "script": custom_js_script %doc,
            })
            script_doc.insert(ignore_permissions = True)

    def get_fields(self, doc):
        frappe_version = frappe.__version__
        if version.parse(frappe_version) >= version.parse("13.0.0") and version.parse(frappe_version) < version.parse("14.0.0") :
            Type_Break = frappe._dict(dt=f"{doc}", fieldname=f"{doc.lower()}_messages", label="Messages", fieldtype="Section Break", hidden=0)
        else:
            Type_Break = frappe._dict(dt=f"{doc}", fieldname=f"{doc.lower()}_messages", label="Messages", fieldtype="Tab Break", hidden=0)
        Message  = frappe._dict(dt= f"{doc}" ,fieldname = "_message",label = "Message",fieldtype = "Small Text" , insert_after = f"{doc.lower()}_messages",allow_on_submit = 1)
        DateFiled = frappe._dict(dt= f"{doc}" ,fieldname = "rmn_date_and_time",label = "Date and Time",fieldtype = "Datetime", insert_after ="_message",allow_on_submit = 1)
        Column_Break = frappe._dict(dt= f"{doc}" ,fieldname = "rmn_column_break",fieldtype = "Column Break" ,insert_after = "rmn_date_and_time") 
        EmailsField = frappe._dict(dt= f"{doc}" ,fieldname = "rmn_emails",label = "Emails",fieldtype = "Table", options= "Reminder Recipients",allow_on_submit = 1,insert_after ="rmn_column_break")
        SendEmailButton = frappe._dict(dt= f"{doc}" ,fieldname = "send_email",label = "Send Email",fieldtype = "Button",insert_after = "rmn_emails")
        dfs = {doc:[
            Type_Break,Message,DateFiled,Column_Break,EmailsField,SendEmailButton
        ]}
        return dfs
