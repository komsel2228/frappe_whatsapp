# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import re, ast

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in frappe_whatsapp/__init__.py
_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('frappe_whatsapp/__init__.py', 'rb') as f:
	version = str(ast.literal_eval(_version_re.search(
		f.read().decode('utf-8')).group(1)))

setup(
    name="frappe_whatsapp",
    version=version,
    description="WhatsApp integration for frappe",
    author="Shridhar Patil",
    author_email="shrip.dev@gmail.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)
