# Copyright (c) 2026, Finbyz Tech Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class FactoHREmployeeMapping(Document):
	def validate(self):
		"""Validate mapping before save"""
		self.validate_unique_employee_number()
		self.validate_unique_factohr_code()
	
	def validate_unique_employee_number(self):
		"""Ensure the linked employee has a unique employee_number"""
		if not self.employee:
			return
		
		# Get employee_number from linked employee
		employee_number = frappe.db.get_value('Employee', self.employee, 'employee_number')
		
		if not employee_number:
			frappe.throw(_("Employee {0} does not have an employee number").format(self.employee))
		
		# Check if another employee has the same employee_number
		duplicate = frappe.db.sql("""
			SELECT name, employee_name
			FROM `tabEmployee`
			WHERE employee_number = %s
			AND name != %s
			LIMIT 1
		""", (employee_number, self.employee), as_dict=True)
		
		if duplicate:
			frappe.throw(_(
				"Employee Number {0} is already assigned to {1} ({2}). "
				"Employee numbers must be unique."
			).format(employee_number, duplicate[0].name, duplicate[0].employee_name))
	
	def validate_unique_factohr_code(self):
		"""Ensure FactoHR employee code is unique across mappings"""
		if not self.factohr_emp_code:
			return
		
		# Check if another mapping exists with the same FactoHR code
		duplicate = frappe.db.get_value(
			'FactoHR Employee Mapping',
			{
				'factohr_emp_code': self.factohr_emp_code,
				'name': ['!=', self.name]
			},
			['employee', 'employee_name'],
			as_dict=True
		)
		
		if duplicate:
			frappe.throw(_(
				"FactoHR Employee Code {0} is already mapped to {1} ({2}). "
				"Each FactoHR code can only be mapped once."
			).format(self.factohr_emp_code, duplicate.employee, duplicate.employee_name))

# Made with Bob
