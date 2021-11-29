# -*- coding: utf-8 -*-

from odoo import models, fields, api


class OrderReparation(models.Model):
    _name = 'taller.order.reparation'
    _description = 'order reparation management'

    state = fields.Selection([
        ('nuevo', 'Nuevo'),
        ('confirmado', 'Confirmado'),
        ('realizado', 'Realizado'),
        ('cancelado', 'Cancelado')
    ], string='Estado', readonly=True, index=True, copy=False,
        default='nuevo', tracking=True)
    name = fields.Char(string="Name", default="nuevo")
    partner_id = fields.Many2one(comodel_name="res.partner", string="Cliente")
    order_reparation_line_ids = fields.One2many(
        comodel_name="taller.order.reparation.line",
        inverse_name="reparation_id", string="lineas de orden de reparacion")
    notas = fields.Html(string="Notas")
    READONLY_STATES = {
        'nuevo': [('readonly', False)],
        'confirmado': [('readonly', True)],
        'cancelado': [('readonly', False)],
    }
    company_id = fields.Many2one('res.company', 'Company', required=True,
                                 index=True, states=READONLY_STATES,
                                 default=lambda self: self.env.company.id)

    @api.model
    def create(self, vals):
        new_seq_name = self.env['ir.sequence'].next_by_code(
            'order.reparation') or 'New'
        vals.update(name=new_seq_name)
        res = super(OrderReparation, self).create(vals)
        return res

    def confirm(self):
        #el self.write actualiza un campo del objeto en curso,
        # en este caso el registro del modelo
        self.write({'state': "confirmado"})

class OrderReparationLine(models.Model):
    _name = 'taller.order.reparation.line'

    name = fields.Char(string="Name")
    reparation_id = fields.Many2one(comodel_name="taller.order.reparation")
    vehicle_id = fields.Many2one(comodel_name="taller.vehicle",
                                 string="vehiculo")
