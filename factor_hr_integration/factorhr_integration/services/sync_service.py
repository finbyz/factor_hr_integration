import frappe
from frappe import _
from typing import Dict, List, Optional
from datetime import datetime
from factor_hr_integration.factorhr_integration.api.api_client import FactoHRAPIClient
from factor_hr_integration.factorhr_integration.utils.data_utils import (
	parse_factohr_date,
	extract_category_value,
	map_status,
	validate_employee_data,
	extract_reporting_manager
)


class EmployeeSyncService:
	"""Service for syncing employees from FactoHR to ERPNext"""

	def __init__(self, settings_doc):
		self.settings = settings_doc
		self.api_client = FactoHRAPIClient(
			settings_doc.api_endpoint,
			settings_doc.username,
			settings_doc.get_password('password')
		)
		self.stats = {
			'total': 0,
			'created': 0,
			'updated': 0,
			'failed': 0,
			'errors': []
		}

	def sync_employees(self, manual: bool = False) -> Dict:
		"""
		Main sync function

		Args:
			manual: Whether this is a manual sync

		Returns:
			Dict with sync statistics
		"""
		try:
			frappe.logger().info("Starting FactoHR employee sync")

			# Fetch employees from FactoHR
			# Use raw string from settings; api_client handles formatting
			from_date = self.settings.sync_from_date if self.settings.sync_from_date else None

			response = self.api_client.fetch_employees(from_date=from_date)

			employees_data = response.get('Data', [])
			self.stats['total'] = len(employees_data)

			# Process each employee
			for emp_data in employees_data:
				try:
					self._process_employee(emp_data)
				except Exception as e:
					self.stats['failed'] += 1
					error_msg = f"Failed to process employee: {str(e)}"
					self.stats['errors'].append(error_msg)
					frappe.log_error(error_msg, "Employee Sync Error")

			# Log sync results
			self._log_sync_result(manual)

			# Update last sync date
			self.settings.last_sync_date = frappe.utils.now()
			self.settings.save(ignore_permissions=True)

			frappe.db.commit()

			frappe.logger().info(f"Sync completed: {self.stats}")

			return self.stats

		except Exception as e:
			error_msg = f"Sync failed: {str(e)}"
			frappe.log_error(error_msg, "FactoHR Sync Error")
			self._log_sync_result(manual, failed=True, error=error_msg)
			raise

	def _process_employee(self, factohr_data: Dict):
		"""Process a single employee"""
		emp_data = factohr_data.get('EmployeeData', {})
		categories = factohr_data.get('CurrentCategoryList', [])

		# Extract employee code
		emp_code = emp_data.get('EmpCode')
		if not emp_code:
			raise ValueError("Employee code is missing")

		# Transform data
		employee_dict = self._transform_employee_data(emp_data, categories)

		# Validate data
		if not validate_employee_data(employee_dict):
			raise ValueError("Employee data validation failed")

		# Check if employee exists in mapping
		existing_mapping = frappe.db.get_value(
			'FactoHR Employee Mapping',
			{'factohr_emp_code': emp_code},
			['employee', 'name'],
			as_dict=True
		)

		if existing_mapping:
			# Update existing employee
			self._update_employee(existing_mapping.employee, employee_dict, emp_code)
			self.stats['updated'] += 1
		else:
			# Check if employee_number already exists (without mapping)
			existing_emp_by_number = frappe.db.get_value(
				'Employee',
				{'employee_number': emp_code},
				'name'
			)
			
			if existing_emp_by_number:
				# Employee exists but no mapping - create mapping and update
				frappe.logger().warning(
					f"Employee with number {emp_code} exists without FactoHR mapping. Creating mapping and updating employee."
				)
				self._create_mapping(existing_emp_by_number, emp_code)
				self._update_employee(existing_emp_by_number, employee_dict, emp_code)
				self.stats['updated'] += 1
			else:
				# Create new employee
				self._create_employee(employee_dict, emp_code)
				self.stats['created'] += 1

	def _transform_employee_data(self, emp_data: Dict, categories: List) -> Dict:
		"""Transform FactoHR data to ERPNext format"""

		# Extract department and designation from categories
		department = extract_category_value(categories, 'Department')
		designation = extract_category_value(categories, 'Designation')

		# Map department and designation
		department = self._get_or_create_department(department)
		designation = self._get_or_create_designation(designation)

		# Build employee dict
		employee_dict = {
			'doctype': 'Employee',
			'employee_number': emp_data.get('EmpCode'),
			'first_name': (emp_data.get('FirstName') or '').strip(),
			'middle_name': (emp_data.get('MiddleName') or '').strip() or None,
			'last_name': (emp_data.get('LastName') or '').strip() or None,
			'salutation': emp_data.get('Title'),
			'gender': emp_data.get('Gender'),
			'date_of_birth': parse_factohr_date(emp_data.get('DateOfBirth')),
			'date_of_joining': parse_factohr_date(emp_data.get('JoiningDate')),
			'status': map_status(emp_data.get('Status')),
			'cell_number': emp_data.get('Mobile'),
			'company_email': emp_data.get('Email'),
			'personal_email': emp_data.get('PersonalEmail'),
			'department': department,
			'designation': designation,
			'company': self.settings.default_company,
			'relieving_date': parse_factohr_date(emp_data.get('LeavingDate'))
		}

		# Add reporting manager if available
		reports_to = extract_reporting_manager(emp_data, categories)
		if reports_to:
			employee_dict['reports_to'] = reports_to

		# Remove None values
		employee_dict = {k: v for k, v in employee_dict.items() if v is not None}

		return employee_dict

	def _create_employee(self, employee_dict: Dict, emp_code: str):
		"""Create new employee"""
		try:
			# Build employee full name from name fields
			name_parts = []
			if employee_dict.get('first_name'):
				name_parts.append(employee_dict['first_name'])
			if employee_dict.get('middle_name'):
				name_parts.append(employee_dict['middle_name'])
			if employee_dict.get('last_name'):
				name_parts.append(employee_dict['last_name'])
			
			full_name = ' '.join(name_parts) if name_parts else emp_code
			
			# Remove naming_series if present to prevent auto-naming
			if 'naming_series' in employee_dict:
				del employee_dict['naming_series']
			
			# Set employee_name explicitly
			employee_dict['employee_name'] = full_name
			
			# Create employee document
			employee = frappe.get_doc(employee_dict)
			
			# Set custom naming format: {it should shmber}-{employee_name}
			# This overrides any naming series to use the format you specified
			custom_name = f"{emp_code}-{full_name}"
			employee.name = custom_name
			
			# Insert with ignore_naming to bypass naming series
			employee.flags.ignore_naming_series = True
			employee.insert(ignore_permissions=True)

			# Create mapping
			self._create_mapping(employee.name, emp_code)

			frappe.logger().info(f"Created employee: {employee.name} (Employee Number: {emp_code})")

		except Exception as e:
			raise Exception(f"Failed to create employee {emp_code}: {str(e)}")

	def _update_employee(self, employee_name: str, employee_dict: Dict, emp_code: str):
		"""Update existing employee"""
		try:
			employee = frappe.get_doc('Employee', employee_name)

			# Update fields
			for key, value in employee_dict.items():
				if key != 'doctype' and hasattr(employee, key):
					setattr(employee, key, value)

			employee.save(ignore_permissions=True)

			# Update mapping
			self._update_mapping(employee_name, emp_code)

			frappe.logger().info(f"Updated employee: {employee_name}")

		except Exception as e:
			raise Exception(f"Failed to update employee {emp_code}: {str(e)}")

	def _create_mapping(self, employee_name: str, emp_code: str):
		"""Create employee mapping"""
		mapping = frappe.get_doc({
			'doctype': 'FactoHR Employee Mapping',
			'employee': employee_name,
			'factohr_emp_code': emp_code,
			'last_synced': frappe.utils.now(),
			'sync_status': 'Active'
		})
		mapping.insert(ignore_permissions=True)

	def _update_mapping(self, employee_name: str, emp_code: str):
		"""Update employee mapping"""
		mapping_name = frappe.db.get_value(
			'FactoHR Employee Mapping',
			{'factohr_emp_code': emp_code},
			'name'
		)

		if mapping_name:
			mapping = frappe.get_doc('FactoHR Employee Mapping', mapping_name)
			mapping.last_synced = frappe.utils.now()
			mapping.sync_status = 'Active'
			mapping.error_message = None
			mapping.save(ignore_permissions=True)

	def _get_or_create_department(self, department_name: str) -> Optional[str]:
		"""Get or create department and return its name (ID)"""
		if not department_name:
			return None

		# 1. Search for existing department by department_name and company
		existing = frappe.db.get_value('Department', 
			{'department_name': department_name, 'company': self.settings.default_company}, 
			'name')
		
		if existing:
			return existing

		# 2. If not found and allowed, create it
		if self.settings.create_missing_departments:
			try:
				dept = frappe.get_doc({
					'doctype': 'Department',
					'department_name': department_name,
					'company': self.settings.default_company
				})
				dept.insert(ignore_permissions=True)
				frappe.db.commit() # Commit to avoid losing it if later items fail
				frappe.logger().info(f"Created department: {dept.name}")
				return dept.name
			except frappe.DuplicateEntryError:
				# 3. Final re-check in case of race condition or naming pattern match
				existing = frappe.db.get_value('Department', 
					{'department_name': department_name, 'company': self.settings.default_company}, 
					'name')
				return existing or department_name
			except Exception as e:
				frappe.log_error(f"Error creating department {department_name}: {str(e)}", "FactoHR Sync Error")
				return department_name

		return department_name

	def _get_or_create_designation(self, designation_name: str) -> Optional[str]:
		"""Get or create designation and return its name (ID)"""
		if not designation_name:
			return None

		# 1. Search for existing designation by designation_name
		existing = frappe.db.exists('Designation', designation_name) or \
				   frappe.db.get_value('Designation', {'designation_name': designation_name}, 'name')
		
		if existing:
			return existing

		# 2. If not found and allowed, create it
		if self.settings.create_missing_designations:
			try:
				desig = frappe.get_doc({
					'doctype': 'Designation',
					'designation_name': designation_name
				})
				desig.insert(ignore_permissions=True)
				frappe.db.commit()
				frappe.logger().info(f"Created designation: {desig.name}")
				return desig.name
			except frappe.DuplicateEntryError:
				# 3. Final re-check
				existing = frappe.db.get_value('Designation', {'designation_name': designation_name}, 'name')
				return existing or designation_name
			except Exception as e:
				frappe.log_error(f"Error creating designation {designation_name}: {str(e)}", "FactoHR Sync Error")
				return designation_name

		return designation_name

	def _log_sync_result(self, manual: bool, failed: bool = False, error: str = None):
		"""Log sync results"""
		log = self.settings.append('sync_logs', {})
		log.sync_datetime = frappe.utils.now()
		log.status = 'Failed' if failed else ('Success' if self.stats['failed'] == 0 else 'Partial')
		log.total_records = self.stats['total']
		log.created = self.stats['created']
		log.updated = self.stats['updated']
		log.failed = self.stats['failed']
		log.api_message = error if error else f"Sync completed {'manually' if manual else 'automatically'}"

		if self.stats['errors']:
			log.error_details = '\n'.join(self.stats['errors'][:10])  # Limit to first 10 errors

		self.settings.save(ignore_permissions=True)


@frappe.whitelist()
def scheduled_sync():
	"""Scheduled sync function called by cron"""
	settings = frappe.get_single('FactoHR Settings')

	if settings.deactivate or not settings.enable_auto_sync:
		return

	try:
		sync_service = EmployeeSyncService(settings)
		sync_service.sync_employees(manual=False)
	except Exception as e:
		frappe.log_error(f"Scheduled sync failed: {str(e)}", "FactoHR Scheduled Sync")

# Made with Bob
