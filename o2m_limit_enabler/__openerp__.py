{
    'name': 'One2Many Limit Enabler',
    'category': 'Extra Tools',
    'version': '0.1',
    'license': 'AGPL-3',
    'description': """

One2Many limit enabler
======================

This module enables 'limit' attribute on one2many fields in order to set the pagination limit.

Example:
--------
<field name="MyOne2ManyField" limit="123">
    <tree string="MyField">
        ...
    </tree>

""",
    'author': 'Alessandro Domanico (alessandro.domanico@informaticisenzafrontiere.org)',
    'website': 'www.informaticisenzafrontiere.org',
    'license': 'AGPL-3',
    'depends': ['web'],
    'js' : [
        'static/src/js/view_form.js',
    ],
    'images': [
        'static/description/o2m_screenshot.jpg',
    ],
    'installable' : True,
}
