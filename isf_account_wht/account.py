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

from openerp.osv import fields, orm
from openerp.tools.translate import _
import decimal_precision as dp

import logging
_logger = logging.getLogger(__name__)
_debug = False

class res_company(orm.Model):
    _inherit = 'res.company'
    _columns = {
        'withholding_payment_term_id': fields.many2one('account.payment.term',
            'Withholding tax Payment Term',
            help="The withholding tax will have to be paid within this term"),
        'withholding_account_id': fields.many2one('account.account','Withholding account',
            help='Payable account used for amount due to tax authority',
            domain=[('type', '=', 'payable')]),
        'withholding_journal_id': fields.many2one('account.journal','Withholding journal',
            help="Journal used for registration of witholding amounts to be paid"),
        'authority_partner_id': fields.many2one('res.partner', 'Tax Authority Partner'),
        }
    
class account_config_settings(orm.TransientModel):
    _inherit = 'account.config.settings'
    _columns = {
        'withholding_payment_term_id': fields.related(
            'company_id', 'withholding_payment_term_id',
            type='many2one',
            relation="account.payment.term",
            string="Withholding tax Payment Term"),
        'withholding_account_id': fields.related(
            'company_id', 'withholding_account_id',
            type='many2one',
            relation="account.account",
            string="Withholding account",
            help='Payable account used for amount due to tax authority',
            domain=[('type', '=', 'payable')]),
        'withholding_journal_id': fields.related(
            'company_id', 'withholding_journal_id',
            type='many2one',
            relation="account.journal",
            string="Withholding journal",
            help='Journal used for registration of witholding amounts to be paid'),
        'authority_partner_id': fields.related(
            'company_id', 'authority_partner_id',
            type='many2one',
            relation="res.partner",
            string="Tax Authority Partner"),
    }
    
    def onchange_company_id(self, cr, uid, ids, company_id, context=None):
        res = super(account_config_settings, self).onchange_company_id(cr, uid, ids, company_id, context=context)
        if company_id:
            company = self.pool.get('res.company').browse(cr, uid, company_id, context=context)
            res['value'].update({
                'withholding_payment_term_id': (company.withholding_payment_term_id
                    and company.withholding_payment_term_id.id or False), 
                'withholding_account_id': (company.withholding_account_id
                    and company.withholding_account_id.id or False),
                'withholding_journal_id': (company.withholding_journal_id
                    and company.withholding_journal_id.id or False),
                'authority_partner_id': (company.authority_partner_id
                    and company.authority_partner_id.id or False),
                })
        else: 
            res['value'].update({
                'withholding_payment_term_id': False, 
                'withholding_account_id': False,
                'withholding_journal_id': False,
                'authority_partner_id': False,
                })
        return res

class account_invoice(orm.Model):
    _inherit = "account.invoice"
    
    def _net_pay(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for invoice in self.browse(cr, uid, ids, context):
            res[invoice.id] = invoice.amount_total - invoice.withholding_amount
        return res

    _columns = {
        'withholding_amount': fields.float('Withholding amount', digits_compute=dp.get_precision('Account'), readonly=True, states={'draft':[('readonly',False)]}),
        'has_withholding': fields.boolean('With withholding tax', readonly=True, states={'draft':[('readonly',False)]}),
        'net_pay': fields.function(_net_pay, string="Net Pay"),
        'withholding_move_id': fields.many2one('account.move', 'Withholding Tax Entries', readonly=True, select=1, ondelete='restrict', help="Link to the With-Holding Journal Entry."),
        }
    
    #This method complete overrides the original one
    def finalize_invoice_move_lines(self, cr, uid, invoice_browse, move_lines):
        """finalize_invoice_move_lines(cr, uid, invoice, move_lines) -> move_lines
        Hook method to be overridden in additional modules to verify and possibly alter the
        move lines to be created by an invoice, for special cases.
        :param invoice_browse: browsable record of the invoice that is generating the move lines
        :param move_lines: list of dictionaries with the account.move.lines (as for create())
        :return: the (possibly updated) final move_lines to create for this invoice
        """
        if _debug:
            _logger.debug('==> invoice_browse : %s', invoice_browse)
            _logger.debug('==> move_lines : %s', move_lines)
        
        if invoice_browse.has_withholding:
            # check if invoice has only one element, otherwise cannot be split in two different invoices
            if len(invoice_browse.invoice_line) > 1:
                raise orm.except_orm(_('Error'), _('A With-Holding Tax invoice must have only one debit account') )
            # check config
            if not invoice_browse.company_id.withholding_account_id:
                raise orm.except_orm(_('Error'), _('The company does not have an associated Withholding account') )
            if not invoice_browse.company_id.withholding_payment_term_id:
                raise orm.except_orm(_('Error'), _('The company does not have an associated Withholding Payment Term') )
            #compute the new amount
            new_amount = invoice_browse.net_pay #invoice_browse.amount_untaxed - invoice_browse.withholding_amount
            #update move lines   
            for move_line in move_lines:
                if move_line[2]['debit'] > 0:
                    move_line[2]['debit'] = new_amount
                if move_line[2]['credit'] > 0:
                    move_line[2]['credit'] = new_amount
            
            if _debug:
                _logger.debug('==> new_move_lines : %s', move_lines)
            
        return move_lines
    
    def invoice_validate(self, cr, uid, ids, context=None):
        super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        invoice_obj = self.pool.get('account.invoice')
        invoice_browse = invoice_obj.browse(cr, uid, ids)[0]
        
        if invoice_browse.has_withholding:
            move_obj = self.pool.get('account.move')
            move_line_obj = self.pool.get('account.move.line')
            period_obj = self.pool.get('account.period')
            
            invoice_move_line_ids = move_line_obj.search(cr, uid, [('move_id','=',invoice_browse.move_id.id)])
            invoice_move_line_browse = move_line_obj.browse(cr, uid, invoice_move_line_ids)
            
            for invoice_move_line in invoice_move_line_browse:
                if invoice_move_line.debit > 0:
                    debit_account_id = invoice_move_line.account_id.id
                    debit_account_name = invoice_move_line.name
                    break
            
            # check config
            if not invoice_browse.company_id.withholding_account_id:
                raise orm.except_orm(_('Error'), _('The company does not have an associated Withholding account') )
            if not invoice_browse.company_id.withholding_payment_term_id:
                raise orm.except_orm(_('Error'), _('The company does not have an associated Withholding Payment Term') )
            #compute the new amount
            new_amount = invoice_browse.amount_untaxed - invoice_browse.withholding_amount
            # compute the due date
            term_pool = self.pool.get('account.payment.term')
            due_list = term_pool.compute(
                cr, uid, invoice_browse.company_id.withholding_payment_term_id.id, new_amount,
                date_ref=invoice_browse.date_invoice, context=None)
            if len(due_list) > 1:
                raise orm.except_orm(_('Error'),
                    _('The payment term %s has too many due dates')
                    % invoice_browse.company_id.withholding_payment_term_id.name)
            if len(due_list) == 0:
                raise orm.except_orm(_('Error'),
                    _('The payment term %s does not have due dates')
                    % invoice_browse.company_id.withholding_payment_term_id.name)
                
            new_move_vals = {
                'date': invoice_browse.date_invoice,
                'ref': invoice_browse.number,
                'period_id': period_obj.find(cr, uid, invoice_browse.date_invoice, context=None)[0],
                'journal_id': invoice_browse.company_id.withholding_journal_id.id,
                'narration': invoice_browse.comment,
                'company_id': invoice_browse.company_id.id,
            }
            
            new_move_id = move_obj.create(cr, uid, new_move_vals, context=None)
            new_move_lines = []
            
            move_line_vals = {
                    'name': debit_account_name,
                    'account_id': debit_account_id,
                    'debit': invoice_browse.withholding_amount,
                    'credit': 0.0,
                    'partner_id': False,
                }
            new_move_lines.append((0, 0, move_line_vals))
            move_line_vals = {
                'name': 'With-Holding Tax',
                'account_id': invoice_browse.company_id.withholding_account_id.id,
                'credit': invoice_browse.withholding_amount,
                'date_maturity': due_list[0][0],
                'debit': 0.0,
                'partner_id': invoice_browse.company_id.authority_partner_id.id,
            }
            new_move_lines.append((0, 0, move_line_vals))   
                    
            move_obj.write(cr, uid, [new_move_id], {'line_id': new_move_lines},context=None)
            #move_obj.post(cr, uid, [new_move_id], context=None)
            
            invoice_obj.write(cr, uid, [invoice_browse.id], {'withholding_move_id': new_move_id})
            
        return True
    
    def action_cancel(self, cr, uid, ids, context=None):
        super(account_invoice, self).action_cancel(cr, uid, ids, context=context)
        
        invoice_obj = self.pool.get('account.invoice')
        invoice_browse = invoice_obj.browse(cr, uid, ids)[0]
        
        if invoice_browse.withholding_move_id.id:
            invoice_obj.write(cr, uid, ids, {'withholding_move_id':False})
            move_obj = self.pool.get('account.move')
            move_obj.button_cancel(cr, uid, [invoice_browse.withholding_move_id.id], context=context)
            move_obj.unlink(cr, uid, [invoice_browse.withholding_move_id.id], context=context)
        
        return True