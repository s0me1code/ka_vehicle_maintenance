import frappe
from frappe.utils import add_to_date
from ka_vehicle_maintenance.utils.AttrDict import AttrDict
import json
from frappe.model.docstatus import DocStatus
from ka_vehicle_maintenance.enums import VehicleStatus, VehicleOwnershipType

"""Maintenance Visit
Vehicle
visit_year
state
last_km
new_km
reminding_date
maintaning_date
attachment
next_reminding_date
next_maintaning_date
checked_at
submited_at
"""

"""Vehicle Visit
maintenance_visit       [Maintenance Visit]
vehicle                 [Vehicle]
visit_year
state
last_km
new_km
reminding_date
maintaning_date
attachment
next_reminding_date
next_maintaning_date
checked_at
submited_at
document_status
"""

"""Vehicle
lincense_plate
model
year
vehicle_type
state
ownership_type
current_km
last_visit_date
visits
insurance
end_date
ownership
vehicle_owner
"""


@frappe.whitelist()
def send_notification():
    # send notification
    n = frappe.new_doc("Notification Log")
    n.subject = "Test Notification"
    n.email_content = "This is a test notification"
    n.document_type = "Vehicle KA"
    n.document_name = "Test-2000-123124"

    n.insert()
    print("\n\n\n Notification sent")


# Maintenance Visit Events
def on_maintenance_delete(doc, event):
    doc.visits = []
    vv_list = frappe.get_all(
        "Vehicle Visit KA",
        filters={"maintenance_visit": doc.name},
        fields=["name", "parenttype"],
    )
    for vv in vv_list:
        frappe.delete_doc("Vehicle Visit KA", vv.name)


def on_maintenance_update(doc, event):
    # update/create viehicle visit
    vv_from_maintenance = update_vehicle_visit_for_maintenance(doc)
    doc.visits = [vv_from_maintenance]

    # update vehicle, fill visits table, state, current_km, last_visit_date
    update_vehicle(doc)


def update_vehicle(doc):
    # 0. get vehicle
    vehicle = frappe.get_doc("Vehicle KA", doc.vehicle)
    if vehicle is None:
        frappe.throw("Vehicle not found")
        return

    # 1. update/create vehicle visit for vehicle
    update_vehicle_visit_for_vehicle(doc)

    # 2. get latest submited vehicle visit state and update vehicle field (state)
    latest_visit = get_latest_visit(vehicle.name)
    if latest_visit:
        frappe.db.set_value("Vehicle KA", vehicle.name,
                            "state", latest_visit.state)

    # 3. get latest submitted vehicle visit with and update filed (current_km and last_visit_date)
    latest_serviced_visit = get_latest_submited_visit(vehicle.name)
    if latest_serviced_visit:
        frappe.db.set_value(
            "Vehicle KA",
            vehicle.name,
            "current_km",
            latest_serviced_visit.new_km,
        )
        frappe.db.set_value(
            "Vehicle KA",
            vehicle.name,
            "last_visit_date",
            latest_serviced_visit.maintenance_date,
        )
    else:
        frappe.db.set_value("Vehicle KA", vehicle.name, "current_km", 0)


def get_latest_visit(vehicle):
    # Upcoming is excluded, because it is a safe state but it is not a final state
    latest_visit = frappe.get_all(
        "Vehicle Visit KA",
        filters={"vehicle": vehicle, "state": [
            "!=", VehicleStatus.UPCOMING.value]},
        order_by="maintenance_date desc",
        fields=["state"],
        limit=1,
    )
    if len(latest_visit) > 0:
        return latest_visit[0]
    return None


def get_latest_submited_visit(vehicle):
    latest_visit = frappe.get_all(
        "Vehicle Visit KA",
        filters={"vehicle": vehicle, "docstatus": DocStatus.submitted()},
        order_by="maintenance_date desc",
        fields=["state", "new_km", "maintenance_date"],
        limit=1,
    )
    if len(latest_visit) > 0:
        return latest_visit[0]
    return None


def get_latest_serviced_visit(vehicle):
    latest_serviced_visit = frappe.get_all(
        "Vehicle Visit KA",
        filters={"vehicle": vehicle, "state": VehicleStatus.SERVICED.value},
        order_by="maintenance_date desc",
        fields=["new_km", "maintenance_date"],
        limit=1,
    )
    if len(latest_serviced_visit) > 0:
        return latest_serviced_visit[0]
    return None


def update_vehicle_visit_for_vehicle(doc):
    vv_list = frappe.get_all(
        "Vehicle Visit KA",
        filters={
            "vehicle": doc.vehicle,
            "maintenance_visit": doc.name,
            "parenttype": "Vehicle KA",
        },
        order_by="maintenance_date",
        fields=["*"],
    )
    if len(vv_list) > 1:
        frappe.throw(
            "Multiple vehicle visits found for the same vehicle and maintenance visit."
        )
        return None
    elif len(vv_list) == 0:
        vv = frappe.new_doc("Vehicle Visit KA")
    else:
        vv = vv_list[0]
        vv = frappe.get_doc("Vehicle Visit KA", vv.name)
    mv = frappe.get_doc(
        "Maintenance Visit KA",
        doc.name,
        fields=["total"]
    )
    vv.parent = doc.vehicle
    vv.company = doc.company
    vv.parentfield = "visits"
    vv.parenttype = "Vehicle KA"
    vv.vehicle = doc.vehicle
    vv.maintenance_visit = doc.name
    vv.vehicle_year = doc.vehicle_year
    vv.state = doc.state
    vv.last_km = doc.last_km
    vv.new_km = doc.new_km
    vv.reminding_date = doc.reminding_date
    vv.maintenance_date = doc.maintenance_date
    vv.attachment = doc.attachment
    vv.next_reminding_date = doc.next_reminding_date
    vv.checked_at = doc.checked_at
    vv.submitted_at = doc.submitted_at
    vv.document_status = doc.docstatus
    vv.total = mv.total
    vv.save()


def update_vehicle_visit_for_maintenance(doc):
    # Check if the document exists
    vv_list = frappe.get_all(
        "Vehicle Visit KA",
        filters={"parent": doc.name, "vehicle": doc.vehicle},
        fields=["name"],
    )
    if len(vv_list) > 1:
        frappe.throw(
            "Multiple vehicle visits found for the same vehicle and maintenance visit."
        )
        return None
    elif len(vv_list) == 0:
        vv = frappe.new_doc("Vehicle Visit KA")
    else:
        vv = vv_list[0]
        vv = frappe.get_doc("Vehicle Visit KA", vv.name)

    vv.vehicle = doc.vehicle
    vv.maintenance_visit = doc.name
    vv.company = doc.company
    vv.vehicle_year = doc.vehicle_year
    vv.state = doc.state
    vv.last_km = doc.last_km
    vv.new_km = doc.new_km
    vv.reminding_date = doc.reminding_date
    vv.maintenance_date = doc.maintenance_date
    vv.attachment = doc.attachment
    vv.next_reminding_date = doc.next_reminding_date
    vv.checked_at = doc.checked_at
    vv.submitted_at = doc.submitted_at
    vv.document_status = doc.docstatus
    vv.total = doc.total
    return vv


# State Change Events
@frappe.whitelist()
def create_new_maintenance_visit(doc, reminding_date=None):
    if isinstance(doc, str):
        doc = AttrDict(json.loads(doc))
    elif isinstance(doc, dict):
        doc = AttrDict(doc)
    # get vahicle
    vehicle = frappe.get_doc("Vehicle KA", doc.vehicle)
    if vehicle is None:
        frappe.throw("Vehicle not found")
        return
    # create a maintenace visit only if rented
    if vehicle.ownership_type != VehicleOwnershipType.RENTED.value:
        frappe.throw("Vehicle not rental")
        return

    mv = frappe.new_doc("Maintenance Visit KA")
    mv.vehicle = doc.vehicle
    mv.company = doc.company
    mv.vehicle_year = doc.vehicle_year
    mv.state = VehicleStatus.UPCOMING.value
    mv.availability_status = doc.availability_status
    mv.ownership_type = VehicleOwnershipType.RENTED.value
    mv.last_km = doc.new_km
    mv.new_km = doc.new_km
    mv.reminding_date = reminding_date
    mv.maintenance_date = add_to_date(reminding_date, days=1)
    mv.save()
    # show success message
    # frappe.msgprint("New Maintenance Visit created successfully."

    # case if vehicle in garage
    if doc.state == VehicleStatus.IN_GARAGE.value:
        frappe.db.set_value(
            "Vehicle KA",
            doc.vehicle,
            "closest_reminding_date",
            reminding_date,
        )
    return mv


@frappe.whitelist()
def prepare_rent_application_to_close(doc, values):
    new_vehicle = None
    if isinstance(doc, str):
        doc = json.loads(doc)
        values = json.loads(values)

        try:
            rider = doc["rider"]
        except KeyError:
            frappe.msgprint("There is no rider assigned to this vehicle")
            return True

        try:
            new_vehicle = values["vehicle"]
        except KeyError:
            new_vehicle = None

        doc = AttrDict(doc)
    elif isinstance(doc, dict):
        doc = AttrDict(doc)

    try:
        vehicle = frappe.get_doc("Vehicle KA", doc.vehicle)
        try:
            rider = frappe.get_doc("Employee", doc.rider)
            rent_applications = frappe.get_all(
                "Rent Application KA",
                filters={
                    "vehicle": vehicle.name,
                    "emp": rider.name,
                    "docstatus": DocStatus.submitted(),
                    "is_active": 1,
                },
            )
            # # NOTE: those being commented since they does not show message after submmition
            # if len(rent_applications) == 0:
            #     frappe.msgprint(
            #         "Rider {0} have no Active Rental Application \
            #         for vehicle {1}".format(
            #             rider.name, vehicle.name)
            #     )
            # if len(rent_applications) > 1:
            #     frappe.msgprint(
            #         "Rider {0} have Multiple Active Rental Applications \
            #         for vehicle {1}".format(
            #             rider.name, vehicle.name)
            #     )
            for ra in rent_applications:
                rent_app = frappe.get_doc("Rent Application KA", ra.name)
                rent_app.prepare_to_close()
                if new_vehicle:
                    rent_app.create_new_rent_application_with_different_vehicle(
                        new_vehicle, None)
            return True
        except frappe.DoesNotExistError:
            frappe.msgprint("Rider not found")
    except frappe.DoesNotExistError:
        frappe.throw("Vehicle not found")


def on_quotation_update(doc, event):
    vehicle_name = doc.custom_vehicle
    workflow_state = doc.workflow_state
    frappe.set_value("Vehicle KA", vehicle_name,
                     "last_quotation_status", workflow_state)
