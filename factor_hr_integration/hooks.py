app_name = "factor_hr_integration"
app_title = "FactorHR Integration"
app_publisher = "Finbyz Tech Pvt Ltd"
app_description = "Integration with Factor Hr to Sync employee and payroll"
app_email = "info@finbyz.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "factor_hr_integration",
# 		"logo": "/assets/factor_hr_integration/logo.png",
# 		"title": "FactorHR Integration",
# 		"route": "/factor_hr_integration",
# 		"has_permission": "factor_hr_integration.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/factor_hr_integration/css/factor_hr_integration.css"
# app_include_js = "/assets/factor_hr_integration/js/factor_hr_integration.js"

# include js, css files in header of web template
# web_include_css = "/assets/factor_hr_integration/css/factor_hr_integration.css"
# web_include_js = "/assets/factor_hr_integration/js/factor_hr_integration.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "factor_hr_integration/public/scss/website"

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
# app_include_icons = "factor_hr_integration/public/icons.svg"

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

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "factor_hr_integration.utils.jinja_methods",
# 	"filters": "factor_hr_integration.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "factor_hr_integration.install.before_install"
# after_install = "factor_hr_integration.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "factor_hr_integration.uninstall.before_uninstall"
# after_uninstall = "factor_hr_integration.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "factor_hr_integration.utils.before_app_install"
# after_app_install = "factor_hr_integration.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "factor_hr_integration.utils.before_app_uninstall"
# after_app_uninstall = "factor_hr_integration.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "factor_hr_integration.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
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

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"factor_hr_integration.tasks.all"
# 	],
# 	"daily": [
# 		"factor_hr_integration.tasks.daily"
# 	],
# 	"hourly": [
# 		"factor_hr_integration.tasks.hourly"
# 	],
# 	"weekly": [
# 		"factor_hr_integration.tasks.weekly"
# 	],
# 	"monthly": [
# 		"factor_hr_integration.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "factor_hr_integration.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "factor_hr_integration.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "factor_hr_integration.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "factor_hr_integration.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["factor_hr_integration.utils.before_request"]
# after_request = ["factor_hr_integration.utils.after_request"]

# Job Events
# ----------
# before_job = ["factor_hr_integration.utils.before_job"]
# after_job = ["factor_hr_integration.utils.after_job"]

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
# 	"factor_hr_integration.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

