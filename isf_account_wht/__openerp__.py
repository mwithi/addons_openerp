# -*- coding: utf-8 -*-
##############################################################################
#    
#    Copyright (C) 2012 Agile Business Group sagl (<http://www.agilebg.com>)
#    Copyright (C) 2012 Domsense srl (<http://www.domsense.com>)
#    Copyright (C) 2012-2013 Associazione OpenERP Italia
#    (<http://www.openerp-italia.org>). 
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'ISF With-Holding Tax',
    'version': '0.1',
    'category': 'Accounting',
    'description': """
ISF With-Holding Tax on Supplier Invoices
=========================================

Inspired by ''l10n_it_withholding_tax'' for OpenERP 7.0, developed by:

- Lorenzo Battistini <lorenzo.battistini@agilebg.com> 
- Paolo Chiara <p.chiara@isa.it>

Instructions:
-------------
In order to use the module, you need to configure the following fields in the company settings (Accounting part):

- Withholding tax Payment Term
- Withholding account
- Withholding journal
- Tax Authority partner
 
In this very first version (0.1), while filling-in the Supplier Invoice, the user must specify the with-holding tax's amount manually and only one debit account can be used

1. On the single Invoice enable the flag 'With withholding tax'
2. The Invoice must have at most one debit account
3. Insert the Withholding amount in the related field that will appear
4. Save and Validate
5. On Validation you will find two Journal Entries, one for the Supplier (posted) and one for the Tax Authority partner (unposted)
6. Pay the two Journal Entries separately
7. If using the 'Pay' button on the invoice, speficy the exact amount due to the Supplier (the Difference Amount goes to Zero)


""",
    'author': 'Alessandro Domanico <alessandro.domanico@informaticisenzafrontiere.org>',
    'website': 'www.informaticisenzafrontiere.org',
    'license': 'AGPL-3',
    'depends' : ['account'],
    'data' : ['account_view.xml',],
    'demo' : [],
    'images': [
        'static/description/wht_screenshot.PNG',
    ],
    'installable': True,
}
