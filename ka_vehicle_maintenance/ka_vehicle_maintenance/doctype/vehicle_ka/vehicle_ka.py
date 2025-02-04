# Copyright (c) 2024, ahmed.g.abdin and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from ka_vehicle_maintenance.enums import AvailabilityStatus


class VehicleKA(Document):
    def before_save(self):
        if self.rider:
            emp = frappe.get_doc("Employee", self.rider)
            self.rider_name = emp.employee_name
            self.whatsapp_number = emp.custom_whatsapp_number
            self.phone_number = emp.cell_number
            self.availability_status = AvailabilityStatus.ON_ROAD.value
        else:  # if no rider is assigned
            self.rider_name = None
            self.whatsapp_number = None
            self.phone_number = None
