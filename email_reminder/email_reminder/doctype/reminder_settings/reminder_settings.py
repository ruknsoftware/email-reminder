# Copyright (c) 2023, Hamza Abuabada and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from packaging import version
class ReminderSettings(Document):
    @frappe.whitelist()
    def generate_fields(self, docs):
        if not isinstance(docs,list) or len(docs) == 0:
            return
        self.disable_fields(docs)
        for doc in docs:
            if not doc or frappe.db.exists("Doctype", doc):
                continue
            fields = self.get_fields(doc)
            create_custom_fields(fields)

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
