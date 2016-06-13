# -*- coding: utf-8 -*-

{
	'name': 'Fixed Asset Register',
	'version': '0.1',
	'category': 'Tools',
	'description': 
"""
Fixed Asset Register 
====================

It shows (by category):
- ID Code Name
- Purchase Date
- Depreciation Start Date 
- Purchase Price
- Revaluated/ Devaluated Value
- Accumulated Depreciation
- Accumulated Depreciation Previous Years
- Depreciation Current Year
- Depreciation Monthly Period 
- Net Book Value
- Totals (by category)
- Total

""",
	'author': 'Alessandro Domanico <alessandro.domanico@informaticisenzafrontiere.org>',
	'website': 'www.informaticisenzafrontiere.org',
	'license': 'AGPL-3',
	'depends': ['account_asset_management'],
	'data': [
        'wizard/asset_register_view.xml',
    ],
	'demo': [],
	'installable' : True,
}

