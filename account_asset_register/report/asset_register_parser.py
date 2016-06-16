# -*- coding: utf-8 -*-
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta

import pprint
pp = pprint.PrettyPrinter(indent=4)

from openerp.osv import fields, orm

from openerp.report import report_sxw
from openerp import tools
import logging
import locale
import platform
from collections import OrderedDict

try:
    locale.setlocale(locale.LC_ALL,'')
except:
    pass

    
_logger = logging.getLogger(__name__)
_debug = True

class asset_register(orm.Model):
    _name = "asset.register.view"
    _description = "Fixed Assets Register View"
    _auto = False
    _columns = {
        'category_id' : fields.char('category_id', size=16, required=False, readonly=True),
        'category' : fields.char('category', size=16, required=False, readonly=True),
        'factor' : fields.char('factor', size=16, required=False, readonly=True),
        'code' : fields.char('code', size=16, required=False, readonly=True),
        'asset' : fields.char('asset', size=16, required=False, readonly=True),
        'date_purchase' : fields.char('date_purchase', size=16, required=False, readonly=True),
        'date_start' : fields.char('date_start', size=16, required=False, readonly=True),
        'purchase_value' : fields.char('purchase_value', size=16, required=False, readonly=True),
        'date_revaluation' : fields.char('date_revaluation', size=16, required=False, readonly=True),
        'opening_cost' : fields.char('opening_cost', size=16, required=False, readonly=True),
        'revaluated_value' : fields.char('revaluated_value', size=16, required=False, readonly=True),
        'date_remove' : fields.char('date_remove', size=16, required=False, readonly=True),
        'profit_loss_disposal' : fields.char('profit_loss_disposal', size=16, required=False, readonly=True),
        'accumulated_depreciation_previous_years' : fields.char('accumulated_depreciation_previous_years', size=16, required=False, readonly=True),
        'depreciation_current_year' : fields.char('depreciation_current_year', size=16, required=False, readonly=True),
    }

class asset_register_parser(report_sxw.rml_parse):
    _name = 'report.asset.register.webkit'
    
    def _update_view(self, cr, uid, params):
        
        tools.drop_view_if_exists(cr, 'asset_register_view')
        cr.execute("""
            create or replace view asset_register_view as (
                select
                    a.category_id,
                    count(a.id) as asset_numer,
                    a.id,
                    c.name as category,
                    case when c.method = 'linear' then 1::float / c.method_number else c.method_progress_factor end as factor, 
                    a.code, 
                    a.name as asset, 
                    a.date_purchase,
                    a.date_start,
                    a.purchase_value,
                    a.date_revaluation,
                    (select r.previous_value from account_asset_revaluation r where r.asset_id = a.id and date_revaluation between '""" + params['fy_date_start'] + """' and '""" + params['fy_date_stop'] + """' order by r.id asc limit 1) as opening_cost,
                    (select r.revaluated_value from account_asset_revaluation r where r.asset_id = a.id and date_revaluation between '""" + params['fy_date_start'] + """' and '""" + params['fy_date_stop'] + """' order by r.id desc limit 1) as revaluated_value,
                    -- delta CALCULATED AFTER (select r.revaluated_value - r.previous_value from account_asset_revaluation r where r.asset_id = a.id and date_revaluation between """ + params['fy_date_start'] + """' and '""" + params['fy_date_stop'] + """' order by r.id desc limit 1) as delta,
                    a.date_remove,
                    a.profit_loss_disposal,
                    -- accumulated_depreciation CALCULATED AFTER (accumulated_depreciation_previous_years + depreciation_current_year) as accumulated_depreciation,
                    (select d.depreciated_value from account_asset_depreciation_line d where d.asset_id = a.id and d.line_date <= '""" + params['previous_fy_date_end'] + """' and type = 'depreciate' and move_check IS TRUE order by id desc limit 1) as accumulated_depreciation_previous_years,
                    (select sum(d.amount) from account_asset_depreciation_line d where d.asset_id = a.id and d.line_date between '""" + params['fy_date_start'] + """' and '""" + params['fy_date_stop'] + """' and type = 'depreciate') as depreciation_current_year
                    -- depreciation_monthly_period CALCULATED AFTER (depreciation_current_year / 12) as depreciation_monthly_period,
                    -- net_value CALCULATED AFTER (select d.remaining_value from account_asset_depreciation_line d where d.asset_id = a.id and d.line_date <= '""" + params['fy_date_stop'] + """' and type = 'depreciate' and move_check IS TRUE order by id desc limit 1) as net_value
                    -- percentage REMOVED (depreciation_current_year / revaluated_value) as percentage
                
                from    
                    account_asset_asset a left join 
                    account_asset_category c on a.category_id = c.id right join
                    account_asset_depreciation_line d on d.asset_id = a.id
                    
                where
                    a.type <> 'view' and
                    d.line_date between '""" + params['fy_date_start'] + """' and '""" + params['fy_date_stop'] + """'
                
                group by
                    c.name, a.id, factor
                
                order by
                    c.name, a.id
        )""")
    
    def __init__(self, cr, uid, name, context=None):
        super(asset_register_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'pp': pp,
            'lines': self.lines,
            'datelines' : self.datelines,
        })
        self.context = context
        self.result_date = []
        self.result_values = []
        
    def _get_fy_duration(self, cr, uid, fy_id, option='days', context=None):
        """
        Returns fiscal year duration.
        @param option:
        - days: duration in days
        - months: duration in months,
                  a started month is counted as a full month
        - years: duration in calendar years, considering also leap years
        """
        cr.execute(
            "SELECT date_start, date_stop, "
            "date_stop-date_start+1 AS total_days "
            "FROM account_fiscalyear WHERE id=%s" % fy_id)
        fy_vals = cr.dictfetchall()[0]
        days = fy_vals['total_days']
        months = (int(fy_vals['date_stop'][:4]) -
                  int(fy_vals['date_start'][:4])) * 12 + \
                 (int(fy_vals['date_stop'][5:7]) -
                  int(fy_vals['date_start'][5:7])) + 1
        if option == 'days':
            return days
        elif option == 'months':
            return months
        
    def _get_company_currency(self, cr, uid, context=None):
        users = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        company_id = users.company_id.id
        currency_id = users.company_id.currency_id
        
        return currency_id
        
    def datelines(self, ids=None, done=None):
        ctx = self.context.copy()
        obj_report = self.pool.get('asset.register')
        report_fiscal_year = obj_report.read(self.cr, self.uid, ctx['active_id'], ['fiscalyear_id'])
        report_asset_category_ids = obj_report.read(self.cr, self.uid, ctx['active_id'], ['asset_category_ids'])
        currency = self._get_company_currency(self.cr, self.uid)
        
        fiscal_year = report_fiscal_year['fiscalyear_id']
        asset_category_ids = report_asset_category_ids['asset_category_ids']
        
        if _debug:
            _logger.debug('fiscal_year: %s', fiscal_year)
            _logger.debug('asset_category_ids: %s', asset_category_ids)
        
        res = {
            'fiscal_year' : fiscal_year[1],
            'asset_category_ids' : asset_category_ids,
            'currency' : currency.name,
        }
        
        self.result_date.append(res)
        
        return self.result_date
    
    def _format_fields(self, res):
        res['opening_cost'] = locale.format("%0.2f", res['opening_cost'], grouping=True)
        res['revaluation'] = locale.format("%0.2f", res['revaluation'], grouping=True)
        res['devaluation'] = locale.format("%0.2f", res['devaluation'], grouping=True)
        res['disposal_value'] = locale.format("%0.2f", res['disposal_value'], grouping=True)
        res['profit_loss_disposal'] = locale.format("%0.2f", res['profit_loss_disposal'], grouping=True)
        res['write_off_accumulated_depreciation'] = locale.format("%0.2f", res['write_off_accumulated_depreciation'], grouping=True)
        res['accumulated_depreciation'] = locale.format("%0.2f", res['accumulated_depreciation'], grouping=True)
        res['accumulated_depreciation_previous_years'] = locale.format("%0.2f", res['accumulated_depreciation_previous_years'], grouping=True)
        res['depreciation_current_year'] = locale.format("%0.2f", res['depreciation_current_year'], grouping=True)
        res['gross_book_value'] = locale.format("%0.2f", res['gross_book_value'], grouping=True)
        res['net_value'] = locale.format("%0.2f", res['net_value'], grouping=True)
        
    def _get_totals(self):
        res = {}    
        res['opening_cost'] = 0
        res['revaluated_value'] = 0
        res['revaluation'] = 0
        res['devaluation'] = 0
        res['disposal_value'] = 0
        res['profit_loss_disposal'] = 0
        res['write_off_accumulated_depreciation'] = 0
        res['accumulated_depreciation_previous_years'] = 0
        res['depreciation_current_year'] = 0
        res['accumulated_depreciation'] = 0
        res['gross_book_value'] = 0
        res['net_value'] = 0
        return res

    def lines(self, ids=None, done=None):
        ctx = self.context.copy()
        fy_obj = self.pool.get('account.fiscalyear')
        obj_report = self.pool.get('asset.register')
        report_fiscal_year = obj_report.read(self.cr, self.uid, ctx['active_id'], ['fiscalyear_id'])
        report_asset_category_ids = obj_report.read(self.cr, self.uid, ctx['active_id'], ['asset_category_ids'])
        
        fy_id = report_fiscal_year['fiscalyear_id'][0]
        asset_category_ids = report_asset_category_ids['asset_category_ids']
        
        if _debug:
            _logger.debug('==> fy_id : %s', fy_id)
            _logger.debug('==> asset_category_ids : %s', asset_category_ids)
        
        fy = fy_obj.browse(self.cr, self.uid, fy_id)
        fy_date_start = datetime.strptime(fy.date_start, '%Y-%m-%d')
        fy_date_stop = datetime.strptime(fy.date_stop, '%Y-%m-%d')
        fy_duration_months = self._get_fy_duration(self.cr, self.uid, fy_id, option='months')
        previous_fy_date_end = fy_date_start + relativedelta(days=-1)
        
        if _debug:
            _logger.debug('==> fy_date_start : %s', fy.date_start)
            _logger.debug('==> fy_date_stop : %s', fy.date_stop)
            _logger.debug('==> previous_fy_date_end : %s', datetime.strftime(previous_fy_date_end, '%Y-%m-%d'))
        
        params = {}
        params['fy_date_start'] = fy.date_start
        params['fy_date_stop'] = fy.date_stop
        params['previous_fy_date_end'] = datetime.strftime(previous_fy_date_end, '%Y-%m-%d')
        self._update_view(self.cr, self.uid, params)
        
        obj_depreciation_line = self.pool.get('asset.register.view')
        depreciation_lines_ids = obj_depreciation_line.search(self.cr, self.uid, [], order="category_id asc, id asc")
        depreciation_lines = obj_depreciation_line.browse(self.cr, self.uid, depreciation_lines_ids)
        
        category = ''
        total = False
        cat_totals = self._get_totals()
        totals = self._get_totals() 
        
        for line in depreciation_lines:
            if line.category_id not in asset_category_ids:
                continue
            if line.category <> category:
                #totals for previous category
                if total:
                    res = {}
                    res['type'] = 'subtotal'
                    res['category'] = category
                    res['opening_cost'] = cat_totals['opening_cost']
                    res['revaluated_value'] = cat_totals['revaluated_value']
                    res['revaluation'] = cat_totals['revaluation']
                    res['devaluation'] = cat_totals['devaluation']
                    res['disposal_value'] = cat_totals['disposal_value']
                    res['profit_loss_disposal'] = cat_totals['profit_loss_disposal']
                    res['write_off_accumulated_depreciation'] = cat_totals['write_off_accumulated_depreciation']
                    res['accumulated_depreciation_previous_years'] = cat_totals['accumulated_depreciation_previous_years']
                    res['depreciation_current_year'] = cat_totals['depreciation_current_year']
                    res['accumulated_depreciation'] = cat_totals['accumulated_depreciation']
                    res['gross_book_value'] = cat_totals['gross_book_value']
                    res['net_value'] = cat_totals['net_value']
                    self._format_fields(res)
                    self.result_values.append(res)
                    cat_totals = self._get_totals()
                
                #new category
                res = {}
                res['type'] = 'category'
                category = line.category
                res['category'] = line.category + ' - ' + locale.format("%0.2f", line.factor * 100) +'%'
                self.result_values.append(res)
                total = True
            
            #asset line (from view)
            res = {}
            res['type'] = 'asset'
            res['id'] = line.id
            res['category'] = line.category
            res['code'] = line.code
            res['asset'] = line.asset
            res['date_purchase'] = line.date_purchase
            res['date_start'] = line.date_start
            res['purchase_value'] = line.purchase_value
            res['opening_cost'] = line.opening_cost
            res['revaluated_value'] = line.revaluated_value
            res['date_remove'] = line.date_remove
            res['profit_loss_disposal'] = line.profit_loss_disposal or 0.0
            res['accumulated_depreciation_previous_years'] = line.accumulated_depreciation_previous_years or 0
            res['depreciation_current_year'] = line.depreciation_current_year
             
            #calculated fields
            if res['opening_cost'] is False:
                res['opening_cost'] = res['purchase_value']
            if res['revaluated_value'] is False:
                res['revaluated_value'] = res['opening_cost']
                res['devaluation'] = 0.0
                res['revaluation'] = 0.0
            else:
                delta = res['revaluated_value'] - res['opening_cost']
                if delta > 0:
                    res['revaluation'] = delta
                    res['devaluation'] = 0.0
                else:
                    res['revaluation'] = 0.0
                    res['devaluation'] = -delta
            if res['date_remove']:
                res['disposal_value'] = res['opening_cost'] + res['revaluation'] - res['devaluation']
                res['write_off_accumulated_depreciation'] = -(res['accumulated_depreciation_previous_years'] + res['depreciation_current_year'])
            else:
                res['disposal_value'] = 0.0
                res['write_off_accumulated_depreciation'] = 0.0
            res['gross_book_value'] = res['opening_cost'] + res['revaluation'] - res['devaluation'] - res['disposal_value']
            res['accumulated_depreciation'] = res['accumulated_depreciation_previous_years'] + res['depreciation_current_year'] + res['write_off_accumulated_depreciation']
            res['net_value'] = res['gross_book_value'] - res['accumulated_depreciation']
            if res['net_value'] < 0.0:
                res['net_value'] = 0.0
            
            #totals for current category
            cat_totals['opening_cost'] += res['opening_cost']
            cat_totals['revaluated_value'] += res['revaluated_value']
            cat_totals['revaluation'] += res['revaluation']
            cat_totals['devaluation'] += res['devaluation']
            cat_totals['disposal_value'] += res['disposal_value']
            cat_totals['profit_loss_disposal'] += res['profit_loss_disposal']
            cat_totals['write_off_accumulated_depreciation'] += res['write_off_accumulated_depreciation']
            cat_totals['accumulated_depreciation_previous_years'] += res['accumulated_depreciation_previous_years']
            cat_totals['depreciation_current_year'] += res['depreciation_current_year']
            cat_totals['accumulated_depreciation'] += res['accumulated_depreciation']
            cat_totals['gross_book_value'] += res['gross_book_value']
            cat_totals['net_value'] += res['net_value']
                        
            #overall totals
            totals['opening_cost'] += res['opening_cost']
            totals['revaluated_value'] += res['revaluated_value']
            totals['revaluation'] += res['revaluation']
            totals['devaluation'] += res['devaluation']
            totals['disposal_value'] += res['disposal_value']
            totals['profit_loss_disposal'] += res['profit_loss_disposal']
            totals['write_off_accumulated_depreciation'] += res['write_off_accumulated_depreciation']
            totals['accumulated_depreciation_previous_years'] += res['accumulated_depreciation_previous_years']
            totals['depreciation_current_year'] += res['depreciation_current_year']
            totals['accumulated_depreciation'] += res['accumulated_depreciation']
            totals['gross_book_value'] += res['gross_book_value']
            totals['net_value'] += res['net_value']
                        
            #formatting
            self._format_fields(res)
            self.result_values.append(res)
            
        #last category total
        res = {}
        res['category'] = category
        res['type'] = 'subtotal'
        res['opening_cost'] = cat_totals['opening_cost']
        res['revaluated_value'] = cat_totals['revaluated_value']
        res['revaluation'] = cat_totals['revaluation']
        res['devaluation'] = cat_totals['devaluation']
        res['disposal_value'] = cat_totals['disposal_value']
        res['profit_loss_disposal'] = cat_totals['profit_loss_disposal']
        res['write_off_accumulated_depreciation'] = cat_totals['write_off_accumulated_depreciation']
        res['accumulated_depreciation_previous_years'] = cat_totals['accumulated_depreciation_previous_years']
        res['depreciation_current_year'] = cat_totals['depreciation_current_year']
        res['accumulated_depreciation'] = cat_totals['accumulated_depreciation']
        res['gross_book_value'] = cat_totals['gross_book_value']
        res['net_value'] = cat_totals['net_value']
                
        #formatting
        self._format_fields(res)
        self.result_values.append(res)
        
        #overall total
        res = {}
        res['type'] = 'total'
        res['opening_cost'] = totals['opening_cost']
        res['revaluated_value'] = totals['revaluated_value']
        res['revaluation'] = totals['revaluation']
        res['devaluation'] = totals['devaluation']
        res['disposal_value'] = totals['disposal_value']
        res['profit_loss_disposal'] = totals['profit_loss_disposal']
        res['write_off_accumulated_depreciation'] = totals['write_off_accumulated_depreciation']
        res['accumulated_depreciation_previous_years'] = totals['accumulated_depreciation_previous_years']
        res['depreciation_current_year'] = totals['depreciation_current_year']
        res['accumulated_depreciation'] = totals['accumulated_depreciation']
        res['gross_book_value'] = totals['gross_book_value']
        res['net_value'] = totals['net_value']
        
        #formatting
        self._format_fields(res)
        self.result_values.append(res)
        
        return self.result_values
    
report_sxw.report_sxw('report.asset.register.webkit', 'asset.register', 'addons/asset_register/report/asset_register.mako', parser=asset_register_parser)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
