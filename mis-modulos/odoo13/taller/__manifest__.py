# -*- coding: utf-8 -*-
{
    'name': "taller",

    'summary': """
        Gestion de taller
        """,

    'description': """
        Taller de reparaciones
    """,

    'author': "Nelson",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'pruebas de desarrollo',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'data/sequence.xml',
        'security/ir.model.access.csv',
        'views/vehicle_view.xml',
        'views/order_reparation_view.xml',
    ],
}
