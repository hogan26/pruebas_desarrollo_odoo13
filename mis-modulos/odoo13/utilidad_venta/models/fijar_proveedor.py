# -*- coding: utf-8 -*-

from odoo import models, fields


class FijarProveedor(models.Model):
    _inherit = 'product.supplierinfo'

    fijar_proveedor = fields.Boolean(string="Fijar proveedor", required=False)
