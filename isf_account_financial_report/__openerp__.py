# -*- coding: utf-8 -*-

{
	'name': 'ISF Account Financial Report',
	'version': '1.0',
	'category': 'Reports',
	'description': """

ISF Account Financial Report 
============================

Modify the OE Financial Report with totals at the end of each section

* the wizard will point to the new rml report 
* the parser will use a recursive function to calculate the lines and totals 
* the parser will use a new function to get children of a parent only
* main column shows selected fiscal year name
* currency symbol removed in order to gain more space

""",
	'author': 'Alessandro Domanico (alessandro.domanico@informaticisenzafrontiere.org)',
	'website': 'www.informaticisenzafrontiere.org',
	'license': 'AGPL-3',
	'depends': ['account_accountant'],
	'data': [],
	'demo': [],
	'installable' : True,
}

