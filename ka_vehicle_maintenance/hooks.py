app_name = "ka_vehicle_maintenance"
app_title = "KA Vehicle Maintenance"
app_publisher = "ahmed.g.abdin"
app_description = "Vehicle Maintenance"
app_email = "ahmed.g.abdien@gmail.com"
app_license = "mit"
# required_apps = []

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ka_vehicle_maintenance/css/ka_vehicle_maintenance.css"
# app_include_js = "/assets/ka_vehicle_maintenance/js/ka_vehicle_maintenance.js"

# include js, css files in header of web template
# web_include_css = "/assets/ka_vehicle_maintenance/css/ka_vehicle_maintenance.css"
# web_include_js = "/assets/ka_vehicle_maintenance/js/ka_vehicle_maintenance.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ka_vehicle_maintenance/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "ka_vehicle_maintenance/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "ka_vehicle_maintenance.utils.jinja_methods",
# 	"filters": "ka_vehicle_maintenance.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ka_vehicle_maintenance.install.before_install"
# after_install = "ka_vehicle_maintenance.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ka_vehicle_maintenance.uninstall.before_uninstall"
# after_uninstall = "ka_vehicle_maintenance.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ka_vehicle_maintenance.utils.before_app_install"
# after_app_install = "ka_vehicle_maintenance.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ka_vehicle_maintenance.utils.before_app_uninstall"
# after_app_uninstall = "ka_vehicle_maintenance.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ka_vehicle_maintenance.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

permission_query_conditions = {
    # 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
    "Vehicle KA": "ka_vehicle_maintenance.permissions.company_wise_v",
    "Maintenance Visit KA": "ka_vehicle_maintenance.permissions.company_wise_mv",
    "Vehicle Visit KA": "ka_vehicle_maintenance.permissions.company_wise_vv",
}

# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }
doc_events = {
    "Vehicle KA": {},
    "Vehicle Visit KA": {},
    "Employee": {
        "on_update": "ka_vehicle_maintenance.eventss.employee.on_update",
    },
    "Maintenance Visit KA": {
        #"on_update": "ka_vehicle_maintenance.events.on_maintenance_update",
        #"on_trash": "ka_vehicle_maintenance.events.on_maintenance_delete",
        #"on_cancel": "ka_vehicle_maintenance.events.on_maintenance_delete",
    },
    "Quotation": {
        "on_update": "ka_vehicle_maintenance.events.on_quotation_update",
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ka_vehicle_maintenance.tasks.all"
# 	],
# 	"daily": [
# 		"ka_vehicle_maintenance.tasks.daily"
# 	],
# 	"hourly": [
# 		"ka_vehicle_maintenance.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ka_vehicle_maintenance.tasks.weekly"
# 	],
# 	"monthly": [
# 		"ka_vehicle_maintenance.tasks.monthly"
# 	],
# }
scheduler_events = {"daily": ["ka_vehicle_maintenance.schedules.update_state"]}


# Testing
# -------

# before_tests = "ka_vehicle_maintenance.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ka_vehicle_maintenance.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ka_vehicle_maintenance.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ka_vehicle_maintenance.utils.before_request"]
# after_request = ["ka_vehicle_maintenance.utils.after_request"]

# Job Events
# ----------
# before_job = ["ka_vehicle_maintenance.utils.before_job"]
# after_job = ["ka_vehicle_maintenance.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"ka_vehicle_maintenance.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }
