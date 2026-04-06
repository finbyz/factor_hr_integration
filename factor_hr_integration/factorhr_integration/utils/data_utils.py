import frappe
from datetime import datetime
from typing import Dict, List, Optional


def parse_factohr_date(date_string: Optional[str]) -> Optional[str]:
	"""
	Parse FactoHR date format to ERPNext format

	Args:
		date_string: Date in format "1985-08-14T00:00:00"

	Returns:
		Date in format "1985-08-14" or None
	"""
	if not date_string:
		return None

	try:
		# Parse ISO 8601 format
		dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
		return dt.strftime('%Y-%m-%d')
	except (ValueError, AttributeError):
		frappe.log_error(f"Invalid date format: {date_string}", "FactoHR Date Parse Error")
		return None


def extract_category_value(categories: List[Dict], category_type: str) -> Optional[str]:
	"""
	Extract category value from FactoHR categories list

	Args:
		categories: List of category dictionaries
		category_type: Type of category (Department, Designation, Branch, etc.)

	Returns:
		Category description or None
	"""
	if not categories:
		return None

	for category in categories:
		try:
			cat_type = category.get('Category', {}).get('CategoryType', {}).get('Type')
			if cat_type == category_type:
				return category.get('Category', {}).get('Description')
		except (KeyError, AttributeError):
			continue

	return None


def map_status(factohr_status: str) -> str:
	"""
	Map FactoHR status to ERPNext status

	Args:
		factohr_status: FactoHR employee status

	Returns:
		ERPNext employee status
	"""
	status_mapping = {
		'Active': 'Active',
		'Inactive': 'Left',
		'Left': 'Left',
		'Suspended': 'Suspended'
	}

	return status_mapping.get(factohr_status, 'Active')


def validate_employee_data(employee_dict: Dict) -> bool:
	"""
	Validate employee data before creating/updating

	Args:
		employee_dict: Employee data dictionary

	Returns:
		True if valid, False otherwise
	"""
	required_fields = ['first_name', 'company']

	for field in required_fields:
		if not employee_dict.get(field):
			frappe.log_error(f"Missing required field: {field}", "Employee Data Validation Error")
			return False

	# Validate email format if provided
	if employee_dict.get('company_email'):
		if not frappe.utils.validate_email_address(employee_dict['company_email']):
			frappe.log_error(f"Invalid email: {employee_dict['company_email']}", "Employee Data Validation Error")
			return False

	return True


def format_phone_number(phone: Optional[str]) -> Optional[str]:
	"""
	Format phone number

	Args:
		phone: Phone number string

	Returns:
		Formatted phone number or None
	"""
	if not phone:
		return None

	# Remove any non-digit characters
	phone = ''.join(filter(str.isdigit, phone))

	return phone if phone else None


def extract_reporting_manager(emp_data: Dict, categories: List[Dict]) -> Optional[str]:
	"""
	Extract and map reporting manager from FactoHR data

	Args:
		emp_data: Employee data from FactoHR
		categories: Category list from FactoHR

	Returns:
		ERPNext employee name of reporting manager or None
	"""
	manager_code = emp_data.get('Manager')

	if not manager_code:
		return None

	# Find ERPNext employee by employee_number
	manager_name = frappe.db.get_value('Employee', {'employee_number': manager_code}, 'name')

	return manager_name

# Made with Bob
