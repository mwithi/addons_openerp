from openerp.osv import orm, fields, osv
from openerp import netsvc

import datetime
import time

class isf_treasury_report_view(osv.TransientModel):
    _name = "isf.treasury.report.view"
    _description = "St.Luke Hospital Treasury Budget Report Wizard"
    
    def _get_fiscal_year(self, cr, uid, context=None):
        obj_period = self.pool.get('account.period')
        date = datetime.datetime.now()
        period_ids = obj_period.find(cr, uid, date, context=context)
        period = obj_period.browse(cr, uid, period_ids)[0]
        return period.fiscalyear_id.id
    

    _columns = {
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscalyear'),
        'divisor' : fields.float('Divisor', required=True),
        'target_move': fields.selection([('posted', 'All Posted Entries'),
                                         ('all', 'All Entries'),
                                        ], 'Target Moves', required=True),
    }
    
    _defaults = {
        'fiscalyear_id' : _get_fiscal_year,
        'divisor' : 1000.0,
        'target_move': 'posted',
    }
    
    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {}
        data['ids'] = context.get('active_ids', [])
        data['model'] = context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(cr, uid, ids, ['date_from',  'date_to',  'fiscalyear_id', 'journal_ids', 'period_from', 'period_to',  'filter',  'chart_account_id', 'target_move'], context=context)[0]
        for field in ['fiscalyear_id', 'chart_account_id', 'period_from', 'period_to']:
            if isinstance(data['form'][field], tuple):
                data['form'][field] = data['form'][field][0]
        used_context = self._build_contexts(cr, uid, ids, data, context=context)
        data['form']['periods'] = used_context.get('periods', False) and used_context['periods'] or []
        data['form']['used_context'] = dict(used_context, lang=context.get('lang', 'en_US'))
        return self._print_report(cr, uid, ids, data, context=context)
    
isf_treasury_report_view()
