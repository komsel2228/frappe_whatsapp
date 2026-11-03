# Copyright (c) 2025, Shridhar Patil and contributors
# For license information, please see license.txt

import frappe
from frappe import _
# from frappe.integrations.utils import make_post_request
from frappe_whatsapp.utils.http import make_post_request, make_request
from frappe.model.document import Document
from frappe_whatsapp.utils.token_crypto import decrypt_secret, encrypt_secret, is_encrypted


class WhatsAppAccount(Document):
	def validate(self):
		self.encrypt_token()

	def encrypt_token(self):
		"""Keep the access token encrypted at rest (v12 Password limit is 127 chars)."""
		token = self.get("token")
		if not token or self.is_dummy_password(token) or is_encrypted(token):
			return
		self.token = encrypt_secret(token)

	def get_password(self, fieldname="password", raise_exception=True):
		"""Return the decrypted token; other fields use Frappe's default behaviour."""
		if fieldname == "token":
			token = self.get("token")
			if token and not self.is_dummy_password(token):
				return decrypt_secret(token)
			# old records saved when token was a Password field live in __Auth
		return super(WhatsAppAccount, self).get_password(fieldname, raise_exception=raise_exception)

	def on_update(self):
		"""Check there is only one default of each type."""
		self.there_must_be_only_one_default()

	def there_must_be_only_one_default(self):
		"""If current WhatsApp Account is default, un-default all other accounts."""
		for field in ("is_default_incoming", "is_default_outgoing"):
			if not self.get(field):
				continue

			for whatsapp_account in frappe.get_all("WhatsApp Account", filters={field: 1}):
				if whatsapp_account.name == self.name:
					continue

				whatsapp_account = frappe.get_doc("WhatsApp Account", whatsapp_account.name)
				whatsapp_account.set(field, 0)
				whatsapp_account.save()

	@frappe.whitelist()
	def subscribe_app(self):
		"""Subscribe this app to webhooks for the WhatsApp Business Account.

		Required after phone number registration to receive incoming messages.
		Calls POST /{version}/{business_id}/subscribed_apps on the Graph API.
		"""
		for field in ("url", "version", "business_id"):
			if not self.get(field):
				frappe.throw(_("{0} is required to subscribe the app").format(
					frappe.bold(self.meta.get_label(field))
				))

		token = self.get_password("token")
		if not token:
			frappe.throw(_("Access token is required to subscribe the app"))

		# endpoint = f"{self.url}/{self.version}/{self.business_id}/subscribed_apps"
		endpoint = "{}/{}/{}/subscribed_apps".format(self.url, self.version, self.business_id)
		headers = {
			"authorization": "Bearer {}".format(token),
			"content-type": "application/json",
		}

		try:
			response = make_post_request(endpoint, headers=headers)
		except Exception as e:
			error_message = str(e)
			if frappe.flags.integration_request:
				err = frappe.flags.integration_request.json().get("error", {})
				if err:
					error_message = err.get("message") or err.get("Error") or error_message
			frappe.throw(_("Failed to subscribe app to webhooks: {0}").format(error_message))

		if not response.get("success"):
			frappe.throw(_("Subscription was not successful: {0}").format(frappe.as_json(response)))

		frappe.logger().info(
			"WhatsApp app subscribed to webhooks for business_id={}".format(self.business_id)
		)
		return response
