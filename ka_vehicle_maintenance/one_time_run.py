import frappe
from frappe.model.docstatus import DocStatus


#  bench execute ka_vehicle_maintenance.one_time_run.one_time_run
def one_time_run():
    vehicels = frappe.get_all("Vehicle KA", filters={"state": ["=", "In Garage"]})
    for vehicle in vehicels:
        visit = get_latest_draft_visit(vehicle.name)
        print(visit)
        if visit:
            frappe.db.set_value(
                "Vehicle KA",
                vehicle.name,
                "closest_reminding_date",
                visit.reminding_date,
            )


def get_latest_draft_visit(vehicle):
    latest_visit = frappe.get_all(
        "Vehicle Visit KA",
        filters={"vehicle": vehicle, "docstatus": DocStatus.draft()},
        order_by="maintenance_date desc",
        fields=["state", "reminding_date"],
        limit=1,
    )
    if len(latest_visit) > 0:
        return latest_visit[0]
    return None


#  bench execute ka_vehicle_maintenance.one_time_run.update_company
def update_company():
    company = "Key Arabia"

    doctype = "Vehicle KA"
    docs = frappe.get_all(
        doctype, filters={"company": ["is", "not set"]}, fields=["name"]
    )
    for doc in docs:
        frappe.db.set_value(
            doctype, doc.name, "company", company, update_modified=False
        )
    frappe.db.commit()
    print(f"Updated {doctype} {len(docs)} records with company '{company}'")
    ###

    doctype = "Vehicle Visit KA"
    docs = frappe.get_all(
        doctype, filters={"company": ["is", "not set"]}, fields=["name"]
    )
    for doc in docs:
        frappe.db.set_value(
            doctype, doc.name, "company", company, update_modified=False
        )
    frappe.db.commit()
    print(f"Updated {doctype} {len(docs)} records with company '{company}'")
    ###

    doctype = "Maintenance Visit KA"
    docs = frappe.get_all(
        doctype, filters={"company": ["is", "not set"]}, fields=["name"]
    )
    for doc in docs:
        frappe.db.set_value(
            doctype, doc.name, "company", company, update_modified=False
        )
    frappe.db.commit()
    print(f"Updated {doctype} {len(docs)} records with company '{company}'")
