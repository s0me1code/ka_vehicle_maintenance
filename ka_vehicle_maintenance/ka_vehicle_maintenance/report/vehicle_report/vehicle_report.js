// Copyright (c) 2024, ahmed.g.abdin and contributors
// For license information, please see license.txt

frappe.query_reports["Vehicle Report"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.add_days(frappe.datetime.get_today(), -30)  // 30 days before today
		},
		{
			"fieldname": "to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
			"default": frappe.datetime.get_today()  // Today's date
		}
	]
};

