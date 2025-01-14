import frappe
from frappe.model.docstatus import DocStatus


def on_update(doc, event):
    # Prevent infinite loop on update
    update_rider_contacts_on_vehicle_doc(doc)


def update_rider_contacts_on_vehicle_doc(doc):
    """
    Update 'Vehicle KA' DocType on updating the employee contacts,
    Steps:
    1. Check 'Employee' DocType, if cell_number and custom_whatsapp_number
    2. Check if there is a 'Vehicle KA' DocType for the employee
    3. Update 'Vehicle KA' DocType, 'cell_number' and 'whatsapp_number'
    3. Update 'Maintenance Visit KA' DocType, 'rider_cell_number' and
    'rider_whatsapp_number'
    """
    if doc.cell_number and doc.custom_whatsapp_number:
        vehicles = frappe.db.get_all(
            "Vehicle KA",
            filters={
                "rider": doc.name,
                "company": doc.company,
            },
        )
        if len(vehicles) > 0:
            for v in vehicles:
                v = frappe.get_doc("Vehicle KA", v.name)
                v.rider_name = doc.employee_name
                v.phone_number = doc.cell_number
                v.whatsapp_number = doc.custom_whatsapp_number
                v.save()
                mvs = frappe.db.get_all(
                    "Maintenance Visit KA",
                    filters={
                        "vehicle": v.name,
                        "company": doc.company,
                        "docstatus": DocStatus.draft(),
                    },
                )
                for mv in mvs:
                    mv = frappe.get_doc("Maintenance Visit KA", mv.name)
                    mv.rider = doc.name
                    mv.rider_name = doc.employee_name
                    mv.rider_phone_number = doc.cell_number
                    mv.rider_whatsapp_number = doc.custom_whatsapp_number
                    mv.save()
