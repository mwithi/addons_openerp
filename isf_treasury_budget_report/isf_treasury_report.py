# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

try:
    locale.setlocale(locale.LC_ALL,'')
except:
    pass

class isf_treasury_report(osv.osv):
    _name = "isf.treasury.report"
    _description = "Treasury Report Model"
    
    def _get_level(self, cr, uid, ids, field_name, arg, context=None):
        '''Returns a dictionary with key=the ID of a record and value = the level of this  
            record in the tree structure.'''
        res = {}
        for report in self.browse(cr, uid, ids, context=context):
            level = 0
            if report.parent_id:
                level = report.parent_id.level + 1
            res[report.id] = level
        return res
    
    def _get_children_by_order(self, cr, uid, ids, context=None):
        '''returns a dictionary with the key= the ID of a record and value = all its children,
           computed recursively, and sorted by sequence. Ready for the printing'''
        res = []
        for id in ids:
            res.append(id)
            ids2 = self.search(cr, uid, [('parent_id', '=', id)], order='sequence ASC', context=context)
            res += self._get_children_by_order(cr, uid, ids2, context=context)
        return res
    
    def _get_type_from_parent(self, cr, uid, context=None):
        for report in self.browse(cr, uid, context.get('id'), context=context):
            type = 'cashin'
            if report and report.parent_id:
                type = report.parent_id.type
        return type
        

    _columns = {
        'sequence': fields.integer('Sequence'),
        'type': fields.selection([
            ('cashin','Cash In Flow'),
            ('cashout','Cash Out Flow'),
            ],'Type',required=True),
        'name': fields.char('Section Name', size=128, required=True, translate=True),
        'name_total': fields.char('Section Total Name', size=128, required=True, translate=True),
        'parent_id': fields.many2one('isf.treasury.report', 'Parent'),
        'children_ids':  fields.one2many('isf.treasury.report', 'parent_id', 'Account Report'),
        'account_ids': fields.many2many('account.account', 'account_account_treasury_report', 'report_line_id', 'account_id', 'Accounts'),
        'level': fields.function(_get_level, string='Level', store=True, type='integer'),
        'sign': fields.selection([(-1, 'Reverse balance sign'), (1, 'Preserve balance sign')], 'Sign on Reports', required=True, help='For accounts that are typically more debited than credited and that you would like to print as negative amounts in your reports, you should reverse the sign of the balance; e.g.: Expense account. The same applies for accounts that are typically more credited than debited and that you would like to print as positive amounts in your reports; e.g.: Income account.'),
        'style_overwrite': fields.selection([
            (0, 'Automatic formatting'),
            (1,'Main Title 1 (bold, underlined)'),
            (2,'Title 2 (bold)'),
            (3,'Title 3 (bold, smaller)'),
            (4,'Normal Text'),
            (5,'Italic Text (smaller)'),
            (6,'Smallest Text'),
            ],'Financial Report Style', help="You can set up here the format you want this record to be displayed. If you leave the automatic formatting, it will be computed based on the financial reports hierarchy (auto-computed field 'level')."),
    }

    _defaults = {
        'sign' : 1,
        'type' : 'cashin', #_get_type_from_parent,
        'style_overwrite' : 0,
    }
    
isf_treasury_report()