import frappe
from frappe.model.docstatus import DocStatus
from ka_vehicle_maintenance.enums import AvailabilityStatus


#  bench execute ka_vehicle_maintenance.one_time_run.one_time_run
def one_time_run():
    vehicels = frappe.get_all("Vehicle KA", filters={
                              "state": ["=", "In Garage"]})
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


def update_rider():
    """
    get all vs
    if v has a rider, fill its data
    get all mvs for this v
    fill mv with the rider data
    """
    vs = frappe.get_all(
        "Vehicle KA",
    )
    for v in vs:
        v = frappe.get_doc("Vehicle KA", v.name)
        if v.rider:
            e = frappe.get_doc("Employee", v.rider)
            v.rider_name = e.employee_name
            v.phone_number = e.cell_number
            v.whatsapp_number = e.custom_whatsapp_number
            v.save()
            mvs = frappe.get_all(
                "Maintenance Visit KA",
                filters={
                    "vehicle": v.name,
                    "docstatus": DocStatus.draft(),
                },
            )
            for mv in mvs:
                mv = frappe.get_doc("Maintenance Visit KA", mv.name)
                if not mv.rider:
                    mv.rider = v.rider
                    mv.rider_name = v.rider_name
                    mv.rider_phone_number = v.phone_number
                    mv.rider_whatsapp_number = v.whatsapp_number
                    mv.save()


def update_vehicle():
    vs = frappe.get_all(
        "Vehicle KA",
    )
    for v in vs:
        v = frappe.get_doc("Vehicle KA", v.name)
        if v.rider:
            e = frappe.get_doc("Employee", v.rider)
            v.rider_name = e.employee_name
            v.phone_number = e.cell_number
            v.whatsapp_number = e.custom_whatsapp_number
            v.aviailability_status = AvailabilityStatus.ON_ROAD.value
            v.save()
