# Copyright (c) 2024, ahmed.g.abdin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import add_days
from ka_vehicle_maintenance.enums import VehicleStatus

# NOTE:
"""
that the schedule script will keep only one unsubmitted maintenance visit
for each vehicle, so you can be sure that always the latest maintenance visit
will overwrite the older
"""


class MaintenanceVisitKA(Document):
    def validate(self):
        if not self.reminding_date and self.maintenance_date:
            self.reminding_date = add_days(self.maintenance_date, -3)

    def on_update(self):
        self.update_vehicle_visit()
        if self.state != VehicleStatus.UPCOMING.value:
            self.update_vehicle_state()

    def on_submit(self):
        frappe.db.set_value("Vehicle KA", self.vehicle,
                            "current_km", self.new_km,)
        frappe.db.set_value("Vehicle KA", self.vehicle,
                            "last_visit_date", self.maintenance_date,)

    def on_cancel(self):
        self.remove_from_vehicle()

    def on_trash(self):
        self.remove_from_vehicle()

    def remove_from_vehicle(self):
        self.visits = []
        vv_list = frappe.get_all(
            "Vehicle Visit KA",
            filters={"maintenance_visit": self.name},
            fields=["name", "parenttype"],
        )
        for vv in vv_list:
            frappe.delete_doc("Vehicle Visit KA", vv.name)

    def update_vehicle_state(self):
        vehicle = frappe.get_doc("Vehicle KA", self.vehicle)
        vehicle.state = self.state
        vehicle.save()

    def update_vehicle_visit(self):
        vehicle = frappe.get_doc("Vehicle KA", self.vehicle)
        vv = frappe.new_doc("Vehicle Visit KA")
        for vv in vehicle.visits:
            if vv.maintenance_visit == self.name:
                vv = frappe.get_doc("Vehicle Visit KA", vv.name)
        vv.parent = self.vehicle
        vv.parentfield = "visits"
        vv.parenttype = "Vehicle KA"
        vv.company = self.company
        vv.vehicle = self.vehicle
        vv.maintenance_visit = self.name
        vv.vehicle_year = self.vehicle_year
        vv.state = self.state
        vv.last_km = self.last_km
        vv.new_km = self.new_km
        vv.reminding_date = self.reminding_date
        vv.maintenance_date = self.maintenance_date
        vv.attachment = self.attachment
        vv.next_reminding_date = self.next_reminding_date
        vv.checked_at = self.checked_at
        vv.submitted_at = self.submitted_at
        vv.document_status = self.docstatus
        vv.total = self.total
        vv.save()
