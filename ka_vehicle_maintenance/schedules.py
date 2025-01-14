import frappe
from frappe.utils import nowdate, getdate
from frappe.query_builder import DocType
from ka_vehicle_maintenance.enums import VehicleStatus, VehicleOwnershipType


def update_state_and_send_notifications():
    today = nowdate()
    current_day = getdate(today).weekday()  # 0 is Monday, 6 is Sunday

    # Check if today is Sunday (6), Monday (0), Tuesday (1), Wednesday (2), or Thursday (3)
    if current_day not in {6, 0, 1, 2, 3}:
        return

    # Define your DocType for Query Builder
    MaintenanceVisitKA = DocType("Maintenance Visit KA")

    # Fetch all documents that are not submitted and have the state "Upcoming" and reminding_date < today
    docs = (
        frappe.qb.from_(MaintenanceVisitKA)
        .select(MaintenanceVisitKA.name, MaintenanceVisitKA.Vehicle)
        .where(
            (MaintenanceVisitKA.docstatus == 0)
            & (
                (MaintenanceVisitKA.state == VehicleStatus.UPCOMING.value)
                | (MaintenanceVisitKA.state == VehicleStatus.UNCHECKED.value)
            )
            & (MaintenanceVisitKA.reminding_date <= today)
        )
    ).run(as_dict=True)

    # Update the state of each document and send notification
    docs_len = len(docs)
    if docs_len == 0:
        return

    for index, doc in enumerate(docs, start=1):
        # Update the state
        frappe.db.set_value(
            "Maintenance Visit KA", doc.name, "state", VehicleStatus.UNCHECKED.value
        )
        frappe.db.set_value(
            "Vehicle KA", doc.vehicle, "state", VehicleStatus.UNCHECKED.value
        )
        vv_list = frappe.get_all(
            "Vehicle Visit KA",
            filters={"maintenance_visit": doc.name},
        )
        for vv in vv_list:
            frappe.db.set_value(
                "Vehicle Visit KA", vv.name, "state", VehicleStatus.UNCHECKED.value
            )

    frappe.db.commit()


def delete_LTO_maintenance_visits():
    """
    This method intended to run every day to make sure that all Vehicle with
    LTO ownership_type, does not have any un submitted Maintenance Visits

    Step 1: Get all Vehicles with LTO Status
    Step 2: Get Un-submitted Maintenance Visits for each Vehicle
    Step 3: Delete all un submitted Maintenance Visits
    """
    # Step 1: Get all Vehicles with LTO Status
    VehicleKA = DocType("Vehicle KA")
    vs = (
        frappe.qb.from_(VehicleKA)
        .select(VehicleKA.name)
        .where(
            VehicleKA.ownership_type == VehicleOwnershipType.LTO.value
        )
    ).run(as_dict=True)
    if vs is None or len(vs) == 0:
        return
    for _, v in enumerate(vs, start=1):
        # Step 2: Get Un-submitted Maintenance Visits for each Vehicle
        maintenance_visits = frappe.get_all(
            "Maintenance Visit KA",
            filters={"vehicle": v.name, "docstatus": 0},
        )
        if maintenance_visits is None or len(maintenance_visits) == 0:
            continue
        # Step 3: Delete all un submitted Maintenance Visits
        for mv in maintenance_visits:
            frappe.delete_doc("Maintenance Visit KA", mv.name)


def sync_vehicle_with_maintenance():
    """
    This function intended to sync the RENTED Vehicle in sync with
    the number of Maintenance Visits

    Step 1: Get all Vehicles with ownership_type RENTED Status
    Step 2: Get Un-submitted Maintenance Visits for each Vehicle
    Case A: none
        Step 1: Create a new Maintenance Visit for each Vehicle
    Case B: one
        Step 1: verify that the state is UPCOMING OR UNCHECKED
    Case C: more than one
        Step 1: verify that the latest state is UPCOMING OR UNCHECKED
        step 2: delete the rest
    """
    # Step 1: Get all Vehicles with RENTED Status
    VehicleKA = DocType("Vehicle KA")
    vs = (
        frappe.qb.from_(VehicleKA)
        .select(
            VehicleKA.name,
            VehicleKA.company,
            VehicleKA.current_km,
            VehicleKA.state,
            VehicleKA.rider,
            VehicleKA.rider_name,
            VehicleKA.phone_number,
            VehicleKA.whatsapp_number,
        )
        .where(
            VehicleKA.ownership_type == VehicleOwnershipType.RENTED.value
        )
    ).run(as_dict=True)
    if vs is None or len(vs) == 0:
        return
    for _, v in enumerate(vs, start=1):
        # Step 2: Get Un-submitted Maintenance Visits for each Vehicle
        maintenance_visits = frappe.get_all(
            "Maintenance Visit KA",
            filters={"vehicle": v.name, "docstatus": 0},
            order_by="maintenance_date desc",
            fields=["name", "state"],
        )
        if maintenance_visits is None or len(maintenance_visits) == 0:
            # Step A1: Create a new Maintenance Visit for each Vehicle
            create_maintenance_visit(v)
        elif len(maintenance_visits) == 1:
            # Step B1: verify that the state is UPCOMING OR UNCHECKED
            verify_vehicle_with_maintenance(v, maintenance_visits[0])
        elif len(maintenance_visits) > 1:
            # Step C1: verify that the state is UPCOMING OR UNCHECKED
            verify_vehicle_with_maintenance(v, maintenance_visits[0])
            # Step C2: keep the latest Un-submitted Maintenance Visit
            for visit in maintenance_visits[1:]:
                frappe.delete_doc("Maintenance Visit KA", visit.name)


def verify_vehicle_with_maintenance(v, mv):
    """
    Verify the Vehicle is up to date with the visit otherwise create a new one
    Steps:
    1. Get the Vehicle data and get the Maintenance Data
    Case A: as expected
    Case B: create a new one with UNCHECKED state
    """
    if mv is None:
        print("\n\n\n No Maintenance Visit for this vehicle")
        create_maintenance_visit(v)
        return
    if mv.state != VehicleStatus.UPCOMING.value and mv.state != VehicleStatus.UNCHECKED.value:
        print("\n\n\n Maintenance Visit is not in UPCOMING or UNCHECKED state")
        frappe.delete_doc("Maintenance Visit KA", mv.name)
        create_maintenance_visit(v)
        return
    if mv.rider != v.rider:
        print("\n\n\n Rider is not the same")
        mv = frappe.get_doc("Maintenance Visit KA", mv.name)
        mv.rider = v.rider
        mv.rider_name = v.rider_name
        mv.rider_phone_number = v.phone_number
        mv.rider_whatsapp_number = v.whatsapp_number
        mv.save()
        return



def create_maintenance_visit(v):
    today = nowdate()
    mv = frappe.new_doc("Maintenance Visit KA")
    mv.vehicle = v.name
    mv.company = v.company
    mv.last_km = v.current_km
    mv.new_km = v.current_km
    mv.rider = v.rider
    mv.rider_name = v.rider_name
    mv.rider_phone_number = v.phone_number
    mv.rider_whatsapp_number = v.whatsapp_number
    mv.maintenance_date = today
    mv.state = VehicleStatus.UNCHECKED.value
    mv.insert()


def update_state():
    update_state_and_send_notifications()
    delete_LTO_maintenance_visits()
    # Make sure all vehicle have a draft MaintenanceVisitKA
    sync_vehicle_with_maintenance()


#  bench execute ka_vehicle_maintenance.schedules.update_state
