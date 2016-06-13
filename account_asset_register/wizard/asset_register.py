from openerp.osv import orm, fields, osv
from openerp import netsvc

import datetime
import time

class asset_register(osv.osv_memory):
    _name = "asset.register"
    _description = "Fixed Asset Register Wizard"
    
    def _get_fiscalyear(self, cr, uid, context=None):
        if context is None:
            context = {}
        now = time.strftime('%Y-%m-%d')
        company_id = False
        ids = context.get('active_ids', [])
        if ids and context.get('active_model') == 'account.account':
            company_id = self.pool.get('account.account').browse(cr, uid, ids[0], context=context).company_id.id
        else:  # use current company id
            company_id = self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id
        domain = [('company_id', '=', company_id), ('date_start', '<', now), ('date_stop', '>', now)]
        fiscalyears = self.pool.get('account.fiscalyear').search(cr, uid, domain, limit=1)
        return fiscalyears and fiscalyears[0] or False

    _columns = {
        'fiscalyear_id': fields.many2one('account.fiscalyear', 'Fiscal Year', required=True),
        'asset_category_ids' : fields.many2many('account.asset.category',string="Asset Categories", required=True),
    }
    
    _defaults = {
        'fiscalyear_id': _get_fiscalyear,
    }
    
asset_register()
