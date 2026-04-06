# Copyright (c) 2026, Finbyz Tech Pvt Ltd and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from factor_hr_integration.factorhr_integration.services.sync_service import EmployeeSyncService


class FactoHRSettings(Document):
	def validate(self):
		"""Validate settings before save"""
		if self.enable_auto_sync and not self.sync_frequency:
			frappe.throw("Please select Sync Frequency when Auto Sync is enabled")

		if not self.api_endpoint:
			frappe.throw("API Endpoint is required")

		if not self.username:
			frappe.throw("User Name is required")

		if not self.password:
			frappe.throw("Password is required")

		if not self.default_company:
			frappe.throw("Default Company is required")

	@frappe.whitelist()
	def sync_employees(self):
		"""Manual sync trigger"""
		if self.deactivate:
			frappe.throw("FactoHR Integration is deactivated")

		sync_service = EmployeeSyncService(self)
		result = sync_service.sync_employees(manual=True)

		return result

	@frappe.whitelist()
	def test_connection(self):
		"""Test API connection"""
		from factor_hr_integration.factorhr_integration.api.api_client import FactoHRAPIClient

		try:
			client = FactoHRAPIClient(self.api_endpoint, self.username, self.get_password('password'))
			token = client.authenticate()
			
			if token:
				self.user_token = token
				self.save(ignore_permissions=True)
				return {
					'success': True,
					'message': 'Connection successful! Token retrieved and saved.'
				}
			else:
				return {
					'success': False,
					'message': 'Authentication failed: No token retrieved'
				}
		except Exception as e:
			return {
				'success': False,
				'message': str(e)
			}
