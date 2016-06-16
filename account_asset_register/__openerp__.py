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
- ID
- Code
- Name
- Purchase Date
- Depreciation Start Date 
- Opening Value at the begin of the FY
- Revaluation (delta)
- Devaluation (delta)
- Disposal (asset remove) = Opening Value + Revaluation - Devaluation
- Gross Book Value = Opening Value + Revaluation - Devaluation - Disposal
- Profit / (Loss) from Disposal = Sale Value - Net Book Value at the date of the disposal
- Accumulated Depreciation Previous Years
- Depreciation Current Year
- Write off Accumulated Depreciation = Accumulated Depreciation Previous Years + Depreciation Current Year (in case of disposal)
- Total Depreciation = Accumulated Depreciation Previous Years + Depreciation Current Year - Write off Accumulated Depreciation
- Net Book Value = Gross Book Value - Total Depreciation

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

