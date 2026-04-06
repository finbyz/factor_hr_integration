import frappe
import requests
from typing import Dict, List, Optional
import json
import datetime


class FactoHRAPIClient:
	"""Client for FactoHR API interactions"""

	def __init__(self, api_endpoint: str, username: str, password: str):
		self.api_endpoint = api_endpoint.rstrip('/')
		self.username = username
		self.password = password
		self.user_token = None

	def authenticate(self) -> str:
		"""Authenticate and get UserToken"""
		url = f"{self.api_endpoint}/api/ACL/AuthenticateUserEmployeeAndGetUserToken"
		
		# Although the Postman says GET, it uses urlencoded body. 
		# Some APIs behave like this. requests.get(url, data=...) might work, 
		# but usually GET params should be in params=. 
		# Let's try to match the Postman's urlencoded body precisely.
		
		payload = {
			'UserName': self.username,
			'Password': self.password
		}
		
		try:
			# Changed from GET with params to POST with data to avoid 500 error 
			# and comply with standard authentication patterns.
			response = requests.post(
				url,
				data=payload, 
				timeout=30
			)
			response.raise_for_status()
			
			# The token might be in the response body directly or as a JSON key
			# Looking at typical FactoHR responses, it's often a string or a JSON
			try:
				data = response.json()
				# If it's a JSON, it might be in a field. 
				# I'll check for common fields or return the whole thing if it's just a string.
				if isinstance(data, str):
					self.user_token = data
				elif isinstance(data, dict):
					# Based on FactoHR response structure, look for 'Token'
					self.user_token = data.get('Token') or data.get('UserToken') or data.get('Data') or str(data)
			except:
				self.user_token = response.text.strip('"')

			if not self.user_token:
				raise Exception("Failed to retrieve UserToken from authentication response")

			return self.user_token

		except Exception as e:
			frappe.log_error(f"FactoHR Authentication Failed: {str(e)}", "FactoHR API Error")
			raise

	def test_connection(self) -> Dict:
		"""Test API connection"""
		try:
			# Try to fetch a small dataset to test connection
			response = self.fetch_employees(limit=1)
			return response
		except Exception as e:
			frappe.log_error(f"FactoHR Connection Test Failed: {str(e)}", "FactoHR API Error")
			raise

	def fetch_employees(self, from_date: Optional[str] = None,
					   to_date: Optional[str] = None) -> Dict:
		"""
		Fetch employees from FactoHR API

		Args:
			from_date: Start date in format DD-MM-YYYY or YYYY-MM-DD
			to_date: End date in format DD-MM-YYYY or YYYY-MM-DD

		Returns:
			Dict containing API response
		"""
		try:
			# Ensure we are authenticated
			if not self.user_token:
				self.authenticate()

			# FactoHR expects dates in format DD-MMM-YYYY (e.g., 01-Feb-2026)
			# Convert from Frappe (YYYY-MM-DD) or current (DD-MM-YYYY)
			def format_factohr_date(d_str):
				if not d_str: return ""
				try:
					# Try YYYY-MM-DD first
					dt = datetime.datetime.strptime(d_str, '%Y-%m-%d')
				except ValueError:
					try:
						# then try DD-MM-YYYY
						dt = datetime.datetime.strptime(d_str, '%d-%m-%Y')
					except ValueError:
						return d_str # Give up and return as-is
				return dt.strftime('%d-%b-%Y')

			formatted_from = format_factohr_date(from_date) if from_date else "01-Jan-1900"
			formatted_to = format_factohr_date(to_date) if to_date else "31-Dec-9999"

			# Endpoint from Postman
			url = f"{self.api_endpoint}/API/Employee/getEmployeeDetailsByModifiedOnDate"

			headers = {
				'UserToken': self.user_token,
				'FROM_DATE': formatted_from,
				'TILL_DATE': formatted_to,
				'RETURN_EMPLOYEEDATA': 'true',
				'RETURN_CURRENT_CATEGORY_LIST': 'true',
				'RETURN_QUALIFICATION_LIST': 'true',
				'RETURN_PAST_EMPLOYMENT_HISTORY_LIST': 'true',
				'RETURN_SALARY_MASTER_COMPONENT_LIST': 'true',
				'RETURN_EMPLOYEE_FURTHER_DETAILS': 'true',
				'RETURN_IDENTITY_LIST': 'true',
				'RETURN_CATEGORIES_HISTORY': 'true',
				'RETURN_RESIGNATION_DETAILS': 'true'
			}

			frappe.logger().info(f"Fetching employees from FactoHR: {url} (From: {formatted_from} To: {formatted_to})")

			response = requests.get(
				url,
				headers=headers,
				timeout=60 # Larger timeout for bulk employee fetch
			)

			response.raise_for_status()
			data = response.json()

			# Validate response structure
			if not self._validate_response(data):
				# If authentication failed (maybe token expired?), try once more
				if data.get('Status') == 'Error' and 'token' in str(data.get('Message', '')).lower():
					self.authenticate()
					headers['UserToken'] = self.user_token
					response = requests.get(url, headers=headers, timeout=60)
					response.raise_for_status()
					data = response.json()
					if not self._validate_response(data):
						raise ValueError("Invalid API response structure after token refresh")
				else:
					raise ValueError(f"Invalid API response: {data.get('Message', 'No message')}")

			return data

		except requests.exceptions.RequestException as e:
			error_msg = f"API Request Failed: {str(e)}"
			frappe.log_error(error_msg, "FactoHR API Error")
			raise Exception(error_msg)
		except json.JSONDecodeError as e:
			error_msg = f"Invalid JSON response: {str(e)}"
			frappe.log_error(error_msg, "FactoHR API Error")
			raise Exception(error_msg)
		except Exception as e:
			error_msg = f"Unexpected error: {str(e)}"
			frappe.log_error(error_msg, "FactoHR API Error")
			raise

	def _validate_response(self, response: Dict) -> bool:
		"""Validate API response structure"""
		required_keys = ['Status', 'Message', 'Data']

		if not all(key in response for key in required_keys):
			return False

		if response['Status'] != 'Success':
			frappe.log_error(f"API returned non-success status: {response.get('Message')}", "FactoHR API Error")
			return False

		if not isinstance(response['Data'], list):
			return False

		return True

# Made with Bob
