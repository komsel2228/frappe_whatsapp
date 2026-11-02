# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import frappe
import requests
from six.moves.urllib.parse import parse_qs

def make_request(method, url, auth=None, headers=None, data=None, timeout=30):
	auth = auth or ""
	headers = headers or {}
	data = data or {}

	try:
		response = requests.request(
			method.upper(), url,
			data=data, auth=auth, headers=headers, timeout=timeout
		)
		frappe.flags.integration_request = response
		response.raise_for_status()

		if response.headers.get("content-type") == "text/plain; charset=utf-8":
			return parse_qs(response.text)

		return response.json()

	except Exception:
		try:
			frappe.log_error(response.text, "WhatsApp API Error")
		except Exception:
			frappe.log_error(frappe.get_traceback(), "WhatsApp API Error")
		raise

def make_post_request(url, auth=None, headers=None, data=None, timeout=30):
	return make_request("POST", url, auth=auth, headers=headers, data=data, timeout=timeout)

def make_get_request(url, auth=None, headers=None, data=None, timeout=30):
	return make_request("GET", url, auth=auth, headers=headers, data=data, timeout=timeout)