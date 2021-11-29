# -*- coding: utf-8 -*-
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class ActualizarPrecio(models.Model):
    _inherit = 'purchase.order'

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id',
                              self.default_get(['company_id'])['company_id'])
        if vals.get('name', 'New') == 'New':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self,
                                                             fields.Datetime.to_datetime(
                                                                 vals[
                                                                     'date_order']))
            vals['name'] = self.env['ir.sequence'].with_context(
                force_company=company_id).next_by_code('purchase.order',
                                                       sequence_date=seq_date) or '/'

        res = super(ActualizarPrecio,
                    self.with_context(company_id=company_id)).create(vals)

        for line in res.order_line:
            for proveedor in line.product_id.seller_ids:
                if proveedor.display_name in res.partner_id.display_name:
                    if proveedor.fijar_proveedor:
                        nuevo_precio = line.price_unit
                        line.product_id.product_tmpl_id.write(
                            {'list_price': nuevo_precio})
                        _logger.info(
                            'line_id= {}, verdadero'.format(
                                line.id))
                        continue
                    else:
                        _logger.info(
                            'line_id= {}, falso'.format(
                                line.id))
                        continue
                else:
                    _logger.info(
                        'line_id= {}, falso'.format(
                            line.id))
                    continue

        return res

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent']:
                continue
            for line in order.order_line:
                for proveedor in line.product_id.seller_ids:
                    if proveedor.display_name in order.partner_id.display_name:
                        if proveedor.fijar_proveedor:
                            nuevo_precio = line.price_unit
                            line.product_id.product_tmpl_id.write(
                                {'list_price': nuevo_precio})
                            _logger.info(
                                'line_id= {}, verdadero'.format(
                                    line.id))
                            continue
                        else:
                            _logger.info(
                                'line_id= {}, falso'.format(
                                    line.id))
                            continue
                    else:
                        _logger.info(
                            'line_id= {}, falso'.format(
                                line.id))
                        continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order.company_id.po_double_validation == 'one_step' \
                    or (order.company_id.po_double_validation == 'two_step' \
                        and order.amount_total < self.env.company.currency_id._convert(
                        order.company_id.po_double_validation_amount,
                        order.currency_id, order.company_id,
                        order.date_order or fields.Date.today())) \
                    or order.user_has_groups(
                'purchase.group_purchase_manager'):
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
        return True

    class DescuentoLineaCompra(models.Model):
        _inherit = 'purchase.order.line'

        @api.depends('product_qty', 'price_unit', 'taxes_id',
                     'descuento_porcentaje', 'descuento_monto')
        def _compute_amount(self):
            for line in self:
                vals = line._prepare_compute_all_values()
                taxes = line.taxes_id.compute_all(
                    vals['price_unit'],
                    vals['currency_id'],
                    vals['product_qty'],
                    vals['product'],
                    vals['partner'])

                if line.descuento_porcentaje:
                    line.update({
                        'price_tax': sum(
                            t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded']-(taxes['total_excluded']*(line.descuento_porcentaje/100)),
                    })
                elif line.descuento_monto:
                    line.update({
                        'price_tax': sum(
                            t.get('amount', 0.0) for t in
                            taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'] - line.descuento_monto,
                    })
                else:
                    line.update({
                        'price_tax': sum(t.get('amount', 0.0) for t in
                                         taxes.get('taxes', [])),
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })

        descuento_porcentaje = fields.Float(string="Descuento(%)", default=0.0)
        descuento_monto = fields.Float(string="Descuento($)", default=0.0)
