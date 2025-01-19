# Copyright (c) 2024, ahmed.g.abdin and contributors
# For license information, please see license.txt
import frappe
from frappe.query_builder import Order
from frappe.query_builder.functions import Count


def execute(filters=None):
    columns, data = [], []

    columns = [
        # {
        #    "fieldname": "name",
        #    "label": "Vehicle ID",
        #    "fieldtype": "Link",
        #    "options": "Vehicle KA",
        #    "width": 250,
        # },
        {
            "fieldname": "license_plate",
            "label": "License Plate",
            "fieldtype": "Int",
        },
        {
            "fieldname": "model",
            "label": "Model",
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "year",
            "label": "Year",
            "fieldtype": "Int",
        },
        {
            "fieldname": "current_km",
            "label": "Current KM",
            "fieldtype": "Int",
        },
        {
            "fieldname": "rider",
            "label": "Rider ID",
            "fieldtype": "Link",
            "options": "Employee",
        },
        {
            "fieldname": "whatsapp_number",
            "label": "WP Number",
            "fieldtype": "Int",
        },
        {
            "fieldname": "last_visit_date",
            "label": "Last Visit Date",
            "fieldtype": "Date",
        },
        {
            "fieldname": "num",
            "label": "Number of Visits",
            "fieldtype": "Int",
        },
    ]

    vehicles = get_vehicle(filters)
    print(f"\n\n\nvehicles:{len(vehicles)}")
    data = [
        {
            "name": row.name,
            "license_plate": row.license_plate,
            "model": row.model,
            "year": row.year,
            "state": row.state,
            "current_km": row.current_km,
            "rider": row.rider,
            "whatsapp_number": row.whatsapp_number,
            "last_visit_date": row.last_visit_date,
            "num": row.num
        }
        for row in vehicles
    ]
    return columns, data


def get_vehicle(filters):
    mv = frappe.qb.DocType("Maintenance Visit KA")
    mv_q = frappe.qb.from_(mv).select(
        mv.vehicle,
        mv.maintenance_date,
        Count('*').as_("num")
    ).where(
        (mv.docstatus == 1) & (
            mv.maintenance_date[filters.from_date: filters.to_date])
    ).groupby(mv.vehicle)

    v = frappe.qb.DocType("Vehicle KA")
    query = (
        frappe.qb.from_(v)
        .left_join(mv_q).on(v.name == mv_q.vehicle)
        .select(v.name,
                v.license_plate,
                v.model,
                v.year,
                v.state,
                v.current_km,
                v.rider,
                v.whatsapp_number,
                v.last_visit_date,
                mv_q.num
                ).orderby(v.last_visit_date, order=Order.asc)
    )
    return query.run(as_dict=True)
