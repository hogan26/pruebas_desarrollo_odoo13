# -*- coding: utf-8 -*-

from datetime import timedelta
from odoo import models, fields, api
from odoo.tools import float_compare
from odoo.exceptions import AccessError, UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    x_profundidad_pozo2 = fields.Integer(string="Profundidad2")
    x_profundidad_pozo = fields.Integer(string="Profundidad 1", default=0)
    x_servicios_requeridos = fields.Selection([('s1','S1'),('s2','S2')],string='Servicios requeridos')


class MargenTotal(models.Model):
    _inherit = 'sale.order'

    @api.depends('order_line.margen_total')
    def suma_margen(self):
        for order in self:
            suma_margen = 0
            for line in order.order_line:
                suma_margen += line.margen_total
            order.update({
                'suma_margen': suma_margen,
            })

    suma_margen = fields.Monetary(string="Margen total", readonly=True,
                                  compute=suma_margen)
    x_profundidad_pozo2 = fields.Integer('Profundidad',
                                         related='opportunity_id.x_profundidad_pozo2',
                                         store=True)

    opportunity_id = fields.Many2one(
        'crm.lead', string='Opportunity', check_company=True,
        domain="[('type', '=', 'opportunity'), '|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    x_servicios_requeridos = fields.Selection(
        related='opportunity_id.x_servicios_requeridos', store=True)

    @api.onchange('sale_order_template_id')
    def onchange_sale_order_template_id(self):
        _logger.info('entra exitosamente')
        if not self.sale_order_template_id:
            self.require_signature = self._get_default_require_signature()
            self.require_payment = self._get_default_require_payment()
            return
        template = self.sale_order_template_id.with_context(
            lang=self.partner_id.lang)

        order_lines = [(5, 0, 0)]
        for line in template.sale_order_template_line_ids:
            data = self._compute_line_data_for_template_change(line)
            if line.product_id:
                discount = 0
                if self.pricelist_id:
                    price = self.pricelist_id.with_context(
                        uom=line.product_uom_id.id).get_product_price(
                        line.product_id, 1, False)
                    if self.pricelist_id.discount_policy == 'without_discount' and line.price_unit:
                        discount = (
                                           line.price_unit - price) / line.price_unit * 100
                        # negative discounts (= surcharge) are included in the display price
                        if discount < 0:
                            discount = 0
                        else:
                            price = line.price_unit
                    elif line.price_unit:
                        price = line.price_unit

                else:
                    price = line.price_unit

                # para comprobar que la cotizacion viene de un requerimiento y no es una orden de trabajo
                if self.opportunity_id:
                    if line.name == 'producto de prueba':
                        profundidad = self.opportunity_id.x_profundidad_pozo
                        data.update({
                            'price_unit': price,
                            'discount': 100 - ((100 - discount) * (
                                    100 - line.discount) / 100),
                            'product_uom_qty': profundidad,
                            'product_id': line.product_id.id,
                            'product_uom': line.product_uom_id.id,
                            'customer_lead': self._get_customer_lead(
                                line.product_id.product_tmpl_id),
                        })
                    else:
                        data.update({
                            'price_unit': price,
                            'discount': 100 - ((100 - discount) * (
                                    100 - line.discount) / 100),
                            'product_uom_qty': line.product_uom_qty,
                            'product_id': line.product_id.id,
                            'product_uom': line.product_uom_id.id,
                            'customer_lead': self._get_customer_lead(
                                line.product_id.product_tmpl_id),
                        })
                else:
                    data.update({
                        'price_unit': price,
                        'discount': 100 - ((100 - discount) * (
                                100 - line.discount) / 100),
                        'product_uom_qty': line.product_uom_qty,
                        'product_id': line.product_id.id,
                        'product_uom': line.product_uom_id.id,
                        'customer_lead': self._get_customer_lead(
                            line.product_id.product_tmpl_id),
                    })

                if self.pricelist_id:
                    data.update(
                        self.env['sale.order.line']._get_purchase_price(
                            self.pricelist_id, line.product_id,
                            line.product_uom_id,
                            fields.Date.context_today(self)))
            order_lines.append((0, 0, data))

        self.order_line = order_lines
        self.order_line._compute_tax_id()

        option_lines = [(5, 0, 0)]
        for option in template.sale_order_template_option_ids:
            data = self._compute_option_data_for_template_change(option)
            option_lines.append((0, 0, data))
        self.sale_order_option_ids = option_lines

        if template.number_of_days > 0:
            self.validity_date = fields.Date.context_today(self) + timedelta(
                template.number_of_days)

        self.require_signature = template.require_signature
        self.require_payment = template.require_payment

        if template.note:
            self.note = template.note

        # _logger.info('_action_launch_stock_rule method')

    @api.model
    def create(self, vals):
        _logger.info('create utilidad porcentaje method')
        if vals.get('name', ('New')) == ('New'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if 'company_id' in vals:
                vals['name'] = self.env['ir.sequence'].with_context(force_company=vals['company_id']).next_by_code(
                    'sale.order', sequence_date=seq_date) or ('New')
            else:
                vals['name'] = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or ('New')

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist and partner.property_product_pricelist.id)
        result = super(MargenTotal, self).create(vals)
        return result

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def utilidad_unitaria(self):
        for line in self:
            line.utilidad_unitaria = line.price_unit * (
                    line.utilidad_porcentaje / 100)

    def precio_venta(self):
        for line in self:
            line.precio_venta = line.price_unit + line.utilidad_unitaria

    def monto_final(self):
        for line in self:
            line.monto_final = line.precio_venta * line.product_uom_qty

    def margen_total(self):
        for line in self:
            line.margen_total = line.utilidad_unitaria * line.product_uom_qty

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id',
                 'utilidad_unitaria', 'precio_venta', 'monto_final',
                 'utilidad_porcentaje')
    def _compute_amount(self):
        for line in self:
            price = (line.price_unit + line.utilidad_unitaria) * (
                    1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id,
                                            line.product_uom_qty,
                                            product=line.product_id,
                                            partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(
                    t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
            if self.env.context.get('import_file',
                                    False) and not self.env.user.user_has_groups(
                'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'],
                                             [line.tax_id.id])

    utilidad_porcentaje = fields.Float(string="Utilidad(%)", default=45)
    utilidad_unitaria = fields.Monetary(string="U. unitaria($)",
                                        compute=utilidad_unitaria)
    precio_venta = fields.Monetary(string="Precio de venta",
                                   compute=precio_venta)
    monto_final = fields.Monetary(string="Monto final", compute=monto_final)
    margen_total = fields.Monetary(string="Margen", compute=margen_total)
