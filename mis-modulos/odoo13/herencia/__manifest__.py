# -*- coding: utf-8 -*-
{
    'name': "Herencia",

    'summary': """
        prueba de herencias
        """,

    'author': "Nelson",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'pruebas de desarrollo',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['purchase'],

    # always loaded
    'data': [
        'views/herencia_lines_view.xml',
    ],
}
