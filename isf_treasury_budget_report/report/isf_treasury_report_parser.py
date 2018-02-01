# -*- coding: utf-8 -*-
import time
import pprint

from openerp.report import report_sxw
from collections import OrderedDict
import logging
import locale
import platform

try:
    locale.setlocale(locale.LC_ALL,'')
except:
    pass

    
_logger = logging.getLogger(__name__)
_debug = True
pp = pprint.PrettyPrinter(indent=4)

class isf_treasury_report_parser(report_sxw.rml_parse):
    _name = 'report.isf.treasury.webkit'
    
    def __init__(self, cr, uid, name, context=None):
        if _debug:
            _logger.debug('==> in init: %s', __name__)
            
        super(isf_treasury_report_parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'pp': pp,
            'lines': self.lines,
            'datelines' : self.datelines,
            'excluded' : self.excluded,
            'duplicated' : self.duplicated,
        })
        self.context = context
        self.result_date = []
        self.result_values = []
        self.result_excluded = []
        self.result_duplicated = []
        
    def duplicated(self, ids=None, done=None):
        return self.result_duplicated
        
    def excluded(self, ids=None, done=None):
        return self.result_excluded
        
    def datelines(self, ids=None, done=None):
        ctx = self.context.copy()
        obj_report = self.pool.get('isf.treasury.report.view')
        report_fiscal_year = obj_report.read(self.cr, self.uid, ctx['active_id'], ['fiscalyear_id'])
        report_divisor = obj_report.read(self.cr, self.uid, ctx['active_id'], ['divisor'])
        report_target_move = obj_report.read(self.cr, self.uid, ctx['active_id'], ['target_move'])
        users = self.pool.get('res.users').browse(self.cr, self.uid, self.uid, context=None)
        company_id = users.company_id.id
        currency = users.company_id.currency_id
        
        fiscal_year = report_fiscal_year['fiscalyear_id']
        divisor = report_divisor['divisor']
        target_move = report_target_move['target_move']
        
        if _debug:
            _logger.debug('fiscal_year: %s', fiscal_year)
            _logger.debug('divisor: %s', divisor)
            _logger.debug('target_move: %s', target_move)
        
        res = {
            'fiscal_year' : fiscal_year[1],
            'divisor' : divisor,
            'currency' : currency.name,
            'warning' : False,
            'target' : target_move,
        }
        
        self.result_date.append(res)
        
        return self.result_date

    def lines(self, ids=None, done=None):
        ctx = self.context.copy()
        obj_move = self.pool.get('account.move')
        obj_move_line = self.pool.get('account.move.line')
        obj_account = self.pool.get('account.account')
        obj_report = self.pool.get('isf.treasury.report.view')
        obj_period = self.pool.get('account.period')
        obj_fiscal_year = self.pool.get('account.fiscalyear')
        report_fiscal_year = obj_report.read(self.cr, self.uid, ctx['active_id'], ['fiscalyear_id'])
        report_divisor = obj_report.read(self.cr, self.uid, ctx['active_id'], ['divisor'])
        report_target_move = obj_report.read(self.cr, self.uid, ctx['active_id'], ['target_move'])
        
        fiscal_year = report_fiscal_year['fiscalyear_id']
        if _debug:
            _logger.debug('fiscal_year : %s', fiscal_year[1])
        
        divisor = report_divisor['divisor']
        target_move = report_target_move['target_move']
        
        #report mapping
        map = {}
        
        #cash and bank accounts
        cash_and_bank_accounts_ids = self.pool.get('account.account').search(self.cr, self.uid, [('type','=','liquidity')], context=None)
        cash_and_bank_accounts = self.pool.get('account.account').browse(self.cr, self.uid, cash_and_bank_accounts_ids, context=None)
        
        #cashin accounts
        cashin_account_ids = []
        cashin_report_ids = self.pool.get('isf.treasury.report').search(self.cr, self.uid, [('type','=','cashin')])
        for report in self.pool.get('isf.treasury.report').browse(self.cr, self.uid, cashin_report_ids, context=None):
            for account in report.account_ids:
                cashin_account_ids.append(account.id)
                #If account.id is already mapped, it will raise a Warning
                if map.has_key(account.id):
                    note = "\"" + map[account.id] + "\" & \"" + report.name_total + "\""
                    self.result_duplicated.append({'account_code' : account.code, 'ref' : account.name, 'note' : note})
                    self.result_date[0].update({ 'warning' : True })
                map[account.id] = report.name_total
                    
        #cashin accounts
        cashout_account_ids = []
        cashout_report_ids = self.pool.get('isf.treasury.report').search(self.cr, self.uid, [('type','=','cashout')])
        for report in self.pool.get('isf.treasury.report').browse(self.cr, self.uid, cashout_report_ids, context=None):
            for account in report.account_ids:
                cashout_account_ids.append(account.id)
                #If account.id is already mapped, it will raise a Warning
                if map.has_key(account.id):
                    note = "\"" + map[account.id] + "\" & \"" + report.name_total + "\""
                    self.result_duplicated.append({'account_code' : account.code, 'ref' : account.name, 'note' : note})
                    self.result_date[0].update({ 'warning' : True })
                map[account.id] = report.name_total
        
        if _debug:    
            _logger.debug('cash_and_bank_accounts_ids : %s', cash_and_bank_accounts_ids)
            _logger.debug('cashin_account_ids : %s', cashin_account_ids)
            _logger.debug('cashout_account_ids : %s', cashout_account_ids)
            
        opening_period_id = obj_period.search(self.cr, self.uid, [('fiscalyear_id','=',fiscal_year[0]),('special','=',True)])
        if _debug:
            _logger.debug('Opening Period id : %s', opening_period_id)
        
        period_ids = obj_period.search(self.cr, self.uid, [('fiscalyear_id','=',fiscal_year[0]),('special','=',False)])
        periods = obj_period.browse(self.cr, self.uid, period_ids)
        if _debug:
            _logger.debug('period_ids : %s', period_ids)
        
        period_fy = obj_fiscal_year.browse(self.cr, self.uid, fiscal_year[0])
        period_fiscal_year = self._get_period_object('13')
        period_opening_balances = self._get_period_object('0')
        opening_period_move_line_ids = obj_move_line.search(self.cr, self.uid, [('period_id','in',opening_period_id)])
        opening_period_move_lines = obj_move_line.browse(self.cr, self.uid, opening_period_move_line_ids)
        
        opening_balance_fiscal_year = self._get_opening_balance_fiscal_year(opening_period_id,cash_and_bank_accounts_ids,target_move)
        #closing_balance_fiscal_year = self._get_closing_balance_fiscal_year(period_fy,cash_and_bank_accounts_ids,target_move)
        for line in opening_period_move_lines:
            account_code = line.account_id.code
            state = line.move_id.state
            debit = line.debit
            credit = line.credit
            
            try: 
                if target_move == 'all' and state == 'draft':
                    period_opening_balances[str(account_code)]['posted'] = False
                
                period_opening_balances[str(account_code)]['value'] += debit
                period_opening_balances[str(account_code)]['value'] += credit
                
            except Exception, e:
                if _debug:
                    #logging.exception(e) # or pass an error message, see comment
                    _logger.debug('Exception : %s', e)
                    _logger.debug('Opening Entries not mapped account: %s', account_code)
                    _logger.debug('reference  : %s', line.ref)
                    _logger.debug('    debit  : %s', debit)
                    _logger.debug('    credit : %s', credit)
                    _logger.debug('    posted : %s', state != 'draft' or False)
        
        result_periods = []
        previous_period = {}
        for p in periods:
            # save previous period, if any
            if len(result_periods) > 0:
                previous_period = result_periods[-1]
            
            # start new period
            period = self._get_period_object(p.id)
            
            # if first period, balances start from opening entries and the same is for the FY column
            if p.id == periods[0].id:
                 
                period['balance_at_beginning_of_period']['value'] = opening_balance_fiscal_year
                period_fiscal_year['balance_at_beginning_of_period']['value'] = opening_balance_fiscal_year
                for account in cash_and_bank_accounts:
                    period[str(account.code)]['value'] = self._get_opening_balance_fiscal_year(opening_period_id,account.code,target_move) # + self._get_opening_balance(p, account_code, target_move)
                    period_fiscal_year[str(account.code)]['value'] = self._get_opening_balance_fiscal_year(opening_period_id,account.code,target_move) # + self._get_opening_balance(p, account_code, target_move)
                period['total_cash_and_bank_balances_reconciliation']['value'] = opening_balance_fiscal_year
                period_fiscal_year['total_cash_and_bank_balances_reconciliation']['value'] = opening_balance_fiscal_year
            
            # other periods start with ending balance of previous period + differences in the previous period
            else:
                period['balance_at_beginning_of_period']['value'] = previous_period['balance_at_ending_of_period']['value'] - previous_period['difference_books_and_cash_balances']['value']
                period['total_cash_and_bank_balances_reconciliation']['value'] = previous_period['balance_at_ending_of_period']['value'] - previous_period['difference_books_and_cash_balances']['value']
                for account in cash_and_bank_accounts:
                    period[str(account.code)]['value'] = previous_period[str(account.code)]['value']
            
            # get only period move lines
            move_lines_ids = obj_move_line.search(self.cr, self.uid, [('period_id','=',p.id),('account_id','in',cash_and_bank_accounts_ids)])
            move_lines = obj_move_line.browse(self.cr, self.uid, move_lines_ids)
            if not isinstance(move_lines, list):
                move_lines = [move_lines]
            move_ids = []
            for move_line in move_lines:
                move_id = move_line.move_id.id
                state = move_line.move_id.state
                if target_move == 'all':
                    if move_id not in move_ids:
                        move_ids.append(move_id)
                else:
                    if state == 'posted' and move_id not in move_ids:
                        move_ids.append(move_id)
            move_lines_ids = obj_move_line.search(self.cr, self.uid, [('move_id','in',move_ids)])
            if _debug:
                _logger.debug('selected move_ids [period %s]: %s', p.id, move_ids)
                _logger.debug('selected move_lines_ids [period %s]: %s', p.id, move_lines_ids)
                
            move_lines = obj_move_line.browse(self.cr, self.uid, move_lines_ids)
            for line in move_lines:
                account_id = line.account_id.id
                account_name = line.account_id.name
                account_code = line.account_id.code
                state = line.move_id.state
                credit_value = line.credit - line.debit
                debit_value = line.debit - line.credit
                period_id = line.period_id.id
                
                try:
                    
                    #Test mapping:
                    #If account_code not mapped, it will raise an Exception
                    period[str(account_code)]
                    
                    #posted or not posted
                    if target_move == 'all' and state == 'draft':
                        period[str(account_code)]['posted'] = False
                    
                    #values and totals calculation
                    # Cash & Banks
                    if account_id in cash_and_bank_accounts_ids:
                        period[str(account_code)]['value'] += debit_value
                        period_fiscal_year[str(account_code)]['value'] += debit_value
                        period['total_cash_and_bank_balances_reconciliation']['value'] += debit_value
                        period_fiscal_year['total_cash_and_bank_balances_reconciliation']['value'] += debit_value
                    
                    # Cash in flows / Receipts
                    elif account_id in cashin_account_ids:
                        period[str(account_code)]['value'] += credit_value
                        period_fiscal_year[str(account_code)]['value'] += credit_value
                        report_name = map[account_id]
                        period['total_' +  report_name]['value'] += credit_value
                        period_fiscal_year['total_' + report_name]['value'] += credit_value
                    
                    # Cash out flows / disbursement
                    elif account_id in cashout_account_ids:
                        period[str(account_code)]['value'] += debit_value
                        period_fiscal_year[str(account_code)]['value'] += debit_value
                        report_name = map[account_id]
                        period['total_' +  report_name]['value'] += debit_value
                        period_fiscal_year['total_' + report_name]['value'] += debit_value
                
                except Exception, e:
                    if _debug:
                        #logging.exception(e) # or pass an error message, see comment
                        _logger.debug('Exception : %s', e)
                        _logger.debug('Not mapped account : %s', account_code)
                        if account_code not in [d['account_code'] for d in self.result_excluded]:
                            self.result_excluded.append({'account_code' : account_code, 'ref' : line.move_id.name, 'note' : line.move_id.ref})
                        self.result_date[0].update({ 'warning' : True })
            
            #Total Cash in flows
            period['total_cash_in_flows']['value'] = 0
            period_fiscal_year['total_cash_in_flows']['value'] = 0
            cashin_flow = self.pool.get('isf.treasury.report').search(self.cr, self.uid, [('type','=','cashin'),('parent_id','=',False)])
            for report in self.pool.get('isf.treasury.report').browse(self.cr, self.uid, cashin_flow, context=None):
                #Since the first sections have been already summarized from related accounts, we recalculate only the sections with subsections (children)
                children = self.pool.get('isf.treasury.report')._get_children_by_order(self.cr, self.uid, [report.id], context=None)
                children = children[1:] #skip the parent itself
                if len(children) > 0:
                    period['total_' + report.name_total]['value'] += self._get_report_total_recursive(p.id, ids, report, period, context=None)
                    period_fiscal_year['total_' + report.name_total]['value'] += self._get_report_total_recursive(p.id, ids, report, period, context=None)
                #Summarized all first sections
                period['total_cash_in_flows']['value'] += period['total_' + report.name_total]['value']
                period_fiscal_year['total_cash_in_flows']['value'] += period_fiscal_year['total_' + report.name_total]['value']
            
            #Total Cash out flows
            period['total_cash_out_flows']['value'] = 0
            period_fiscal_year['total_cash_out_flows']['value'] = 0
            cashout_flow = self.pool.get('isf.treasury.report').search(self.cr, self.uid, [('type','=','cashout'),('parent_id','=',False)])
            for report in self.pool.get('isf.treasury.report').browse(self.cr, self.uid, cashout_flow, context=None):
                #Since the first sections have been already summarized from related accounts, we recalculate only the sections with subsections (children)
                children = self.pool.get('isf.treasury.report')._get_children_by_order(self.cr, self.uid, [report.id], context=None)
                children = children[1:] #skip the parent itself
                if len(children) > 0:
                    period['total_' + report.name_total]['value'] += self._get_report_total_recursive(p.id, ids, report, period, context=None)
                    period_fiscal_year['total_' + report.name_total]['value'] += self._get_report_total_recursive(p.id, ids, report, period, context=None)
                #Summarized all first sections
                period['total_cash_out_flows']['value'] += period['total_' + report.name_total]['value']
                period_fiscal_year['total_cash_out_flows']['value'] += period_fiscal_year['total_' + report.name_total]['value']
                
            period['difference_cashin_cashout']['value'] = period['total_cash_in_flows']['value'] - period['total_cash_out_flows']['value']
            period_fiscal_year['difference_cashin_cashout']['value'] = period_fiscal_year['total_cash_in_flows']['value'] - period_fiscal_year['total_cash_out_flows']['value']
            
            period['balance_at_ending_of_period']['value'] = period['balance_at_beginning_of_period']['value'] + period['difference_cashin_cashout']['value']
            period_fiscal_year['balance_at_ending_of_period']['value'] = period_fiscal_year['balance_at_beginning_of_period']['value'] + period_fiscal_year['difference_cashin_cashout']['value']
            
            period['difference_books_and_cash_balances']['value'] = period['balance_at_ending_of_period']['value'] - period['total_cash_and_bank_balances_reconciliation']['value']
            period_fiscal_year['difference_books_and_cash_balances']['value'] = period_fiscal_year['balance_at_ending_of_period']['value'] - period_fiscal_year['total_cash_and_bank_balances_reconciliation']['value']
            
            result_periods.append(period)

        result_periods.append(period_fiscal_year)
        
        ### percentage calculation
        period_percentage = self._get_period_object('%')
        period_keys = period_percentage.keys()
        reports_ids = self.pool.get('isf.treasury.report').search(self.cr, self.uid, [])
        for report in self.pool.get('isf.treasury.report').browse(self.cr, self.uid, reports_ids):
            period_percentage['total_' + report.name_total]['value'] = 100
            for account in report.account_ids:
                try:
                    period_percentage[account.code]['value'] = abs(period_fiscal_year[account.code]['value'] / period_fiscal_year['total_' + report.name_total]['value'] * 100)
                except Exception, e:
                    if _debug:
                        _logger.debug('Exception : %s', e)
        
        result_periods.append(period_percentage)
        
        #### CONVERT TO REPORT DICTIONARY ####
        for key in period_keys:
            temp = {}
            period_id = 1 #override period id for report
            title = ''
            fiscal_year = 0
            level = 0
            for period in result_periods:
                period_value = str(period_id)
                value_locale = str(period_id) + '_locale'
                value_posted = str(period_id) + '_posted'
                
                temp['position'] = period[key]['position']
                temp['title'] = period[key]['title']
                temp['type'] = period[key]['type']
                temp['level'] = period[key]['level']
                temp[period_value] = 0
                temp[value_locale] = ''
                temp[value_posted] = True 
                
                temp[value_posted] = temp[value_posted] and period[key]['posted']
                
                value = period[key]['value']
                if value:
                    temp[period_value] = value
                        
                if period[key]['period'] == '%':
                    temp[value_locale] = locale.format("%20.0f", temp[period_value], grouping=True)
                else:
                    temp[value_locale] = locale.format("%20.0f", temp[period_value] / divisor, grouping=True)
                    
                period_id += 1
                
            self.result_values.append(temp)
            
        return self.result_values
    
    
    def _get_report_total_recursive(self, pid, ids=None, report=None, period=None, context=None):
        total = 0
        children = self.pool.get('isf.treasury.report')._get_children_by_order(self.cr, self.uid, [report.id], context=context)
        children = children[1:] #skip the parent itself
        if len(children) > 0:
            for child in self.pool.get('isf.treasury.report').browse(self.cr, self.uid, children, context=context):
                total += self._get_report_total_recursive(pid, ids, child, period, context)
        else:
            total = period['total_' + report.name_total]['value']
        return total
    
    def _get_period_object_recursive(self, pid, ids=None, report=None, context=None):
        period = OrderedDict()
        period['title_' + report.name] = {'level' : report.level, 'type' : 'title', 'posted' : True, 'position' : '', 'period' : pid, 'title' : report.name, 'value' : None}
        for account in report.account_ids:
            period[account.code] = {'level' : report.level, 'type' : 'value', 'posted' : True, 'position' : account.code, 'period' : pid, 'title' : '', 'value' : 0.0}
        children = self.pool.get('isf.treasury.report')._get_children_by_order(self.cr, self.uid, [report.id], context=context)
        children = children[1:] #skip the parent itself
        if len(children) > 0:
            for child in self.pool.get('isf.treasury.report').browse(self.cr, self.uid, children, context=context):
                period.update(self._get_period_object_recursive(pid, ids, child, context))
        period['total_' + report.name_total] = {'level' : report.level, 'type' : 'total', 'posted' : True, 'position' : '', 'period' : pid, 'title' : report.name_total, 'value' : 0.0}
        return period
        
    def _get_period_object(self, pid, ids=None, context=None):
        period = OrderedDict()
        
        ## BEGINNING BALANCE
        period['balance_at_beginning_of_period'] = {'level' : 0, 'type' : 'calc', 'posted' : True, 'position' : '', 'period' : pid, 'title' : 'BALANCE AT BEGINNING OF PERIOD', 'value' : 0.0}
        
        ## CASHIN FLOWS
        period['title_cash_in_flows'] = {'level' : 0, 'type' : 'section', 'posted' : True, 'position' : '', 'period' : pid, 'title' : 'CASH IN FLOWS (INCOMES and OTHERS)', 'value' : None}
        cashin_flow = self.pool.get('isf.treasury.report').search(self.cr, self.uid, [('type','=','cashin'),('parent_id','=',False)])
        for report in self.pool.get('isf.treasury.report').browse(self.cr, self.uid, cashin_flow, context=context):
            period.update(self._get_period_object_recursive(pid, ids, report, context))
        period['total_cash_in_flows'] = {'level' : 0, 'type' : 'total', 'posted' : True, 'position' : '', 'period' : pid, 'title' : 'TOTAL CASH IN FLOWS (INCOMES and OTHERS)', 'value' : 0.0}
        
        ## CASHOUT FLOWS
        period['title_cash_out_flows'] = {'level' : 0, 'type' : 'section', 'posted' : True, 'position' : '', 'period' : pid, 'title' : 'CASH OUT FLOWS (DISBURSEMENTS)', 'value' : None}
        cashout_flow = self.pool.get('isf.treasury.report').search(self.cr, self.uid, [('type','=','cashout'),('parent_id','=',False)])
        for report in self.pool.get('isf.treasury.report').browse(self.cr, self.uid, cashout_flow, context=context):
            period.update(self._get_period_object_recursive(pid, ids, report, context))
        period['total_cash_out_flows'] = {'level' : 0, 'type' : 'total', 'posted' : True, 'position' : '', 'period' : pid, 'title' : 'TOTAL CASH OUT FLOWS (DISBURSEMENTS)', 'value' : 0.0}

        ## DIFF CASHIN - CASHOUT
        period['difference_cashin_cashout'] = {'level' : 0, 'type' : 'calc', 'posted' : True, 'position' : '', 'period' : pid, 'title' : 'DIFF. +/-  CASH IN / CASH OUT FLOWS', 'value' : 0.0}
        
        ## ENDING BALANCE
        period['balance_at_ending_of_period'] = {'level' : 0, 'type' : 'calc', 'posted' : True, 'position' : '', 'period' : pid, 'title' : 'BALANCE AT ENDING OF PERIOD', 'value' : 0.0}
        
        ## CASH AND BANK RECONCILIATION
        period['cash_and_bank_balances_reconciliation'] = {'level' : 0, 'type' : 'section', 'posted' : True, 'position' : '', 'period' : pid, 'title' : 'RECONCILIATION', 'value' : None}
        period['title_cash_and_bank_balances_reconciliation'] = {'level' : 0, 'type' : 'title', 'posted' : True, 'position' : '', 'period' : pid, 'title' : 'Cash and Banks Balances Reconciliation', 'value' : None}
        cash_and_bank_accounts_ids = self.pool.get('account.account').search(self.cr, self.uid, [('type','=','liquidity')], context=None)
        for account in self.pool.get('account.account').browse(self.cr, self.uid, cash_and_bank_accounts_ids, context=None):
            period[account.code] = {'level' : 0, 'type' : 'value', 'posted' : True, 'position' : account.code, 'period' : pid, 'title' : '', 'value' : 0.0} 
        period['total_cash_and_bank_balances_reconciliation'] = {'level' : 0, 'type' : 'total', 'posted' : True, 'position' : '', 'period' : pid, 'title' : 'Totals Final Balances in Cash and Cash Equivalent', 'value' : 0.0}
        
        ## DIFF BOOK AND CASH
        period['difference_books_and_cash_balances'] = {'level' : 0, 'type' : 'end', 'posted' : True, 'position' : '', 'period' : pid, 'title' : 'Differ. +/- Books & (Cash) Balances', 'value' : 0.0}
        period_keys = period.keys();
            
        # get accounts names (first 50 characters)
        obj_account = self.pool.get('account.account')
        accounts_ids = obj_account.search(self.cr, self.uid, [('code', 'in', period_keys)])
        accounts = obj_account.browse(self.cr, self.uid, accounts_ids)
        for account in accounts:
            code = account.code
            period[code]['title'] = account.name[:50]
            
#         if _debug:
#             _logger.debug('==> period object:')
#         pp.pprint(period)
            
        return period;
    
    def _get_opening_balance_fiscal_year(self, period_id, cash_and_bank_accounts_ids, target_move):
        obj_move_line = self.pool.get('account.move.line')
        value = 0
        previous_move_lines_ids = obj_move_line.search(self.cr, self.uid, [('period_id','in',period_id),('account_id','in',cash_and_bank_accounts_ids)])
        previous_move_lines = obj_move_line.browse(self.cr, self.uid, previous_move_lines_ids)
        if not isinstance(previous_move_lines, list):
            previous_move_lines = [previous_move_lines]
        previous_move_ids = []
        for line in previous_move_lines:
            state = line.move_id.state
            if target_move == 'all':
                debit = line.debit
                credit = line.credit
                value += debit
                value -= credit
            else:
                if state == 'posted':
                    debit = line.debit
                    credit = line.credit
                    value += debit
                    value -= credit
        
        return value
        
report_sxw.report_sxw('report.isf.treasury.webkit', 'isf.treasury.report.view', 'addons/isf_treasury_budget_report/report/treasury.mako', parser=isf_treasury_report_parser)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
