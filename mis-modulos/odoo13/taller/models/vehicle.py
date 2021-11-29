# -*- coding: utf-8 -*-

from odoo import models, fields, api, exceptions


class Vehicle(models.Model):
    _name = 'taller.vehicle'
    # _rec_name = 'name'
    _description = 'vehicle management'

    name = fields.Char(string="Name", help="ayuda de ejemplo", size=20,
                       default="nuevo")
    active = fields.Boolean(string="Active", default=True)
    matricula = fields.Char(string="Placa")

    _sql_constraints = [
        ('vehicle_name_unique', 'unique (name)', 'el nombre debe ser unico')]
    tag_ids = fields.Many2many(
        comodel_name="vehicle.tag"
    )

    @api.constrains('matricula')
    def _check_matricula(self):
        domain = [
            ('id', '!=', self.id),
            ('matricula', '=', self.matricula)
        ]
        vehicles = self.search(domain)
        if vehicles:
            raise exceptions.ValidationError("matricula duplicada")


class VehicleTag(models.Model):
    _name = "vehicle.tag"

    name = fields.Char(string="Name")
