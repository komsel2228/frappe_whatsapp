"""Encrypt long secrets (WhatsApp access tokens) without using __Auth.

Frappe v12 stores Password fields in __Auth.password (VARCHAR(255)), so
encrypt() refuses anything over 127 characters. Meta tokens are longer, so the
token is kept Fernet-encrypted in a normal long-text column instead.
"""
from __future__ import unicode_literals

import frappe
from frappe import _
from frappe.utils import cstr, encode
from frappe.utils.password import get_encryption_key
from cryptography.fernet import Fernet, InvalidToken

FERNET_PREFIX = "gAAAA"

def _fernet():
	return Fernet(encode(get_encryption_key()))

def is_encrypted(value):
	value = cstr(value or "").strip()
	if not value.startswith(FERNET_PREFIX):
		return False
	try:
		_fernet().decrypt(encode(value))
		return True
	except (InvalidToken, ValueError, TypeError):
		return False

def encrypt_secret(plain_text):
	return cstr(_fernet().encrypt(encode(cstr(plain_text).strip())))

def decrypt_secret(value):
	value = cstr(value or "").strip()
	if not value:
		return value
	if not value.startswith(FERNET_PREFIX):
		return value
	try:
		return cstr(_fernet().decrypt(encode(value)))
	except (InvalidToken, ValueError, TypeError):
		frappe.throw(_("Encryption key is invalid, Please check site_config.json"))