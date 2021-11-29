# -*- coding: utf-8 -*-
{
    'name': "Utility sale order lines",

    'summary': """
        prueba de requerimientos hidrosondajes
        """,

    'author': "Nelson",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'pruebas de desarrollo',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale','purchase','product','crm'],

    # always loaded
    'data': [
        'views/utility_lines_view.xml',
        'views/fijar_proveedor_form_view.xml',
        'views/fijar_proveedor_tree_view.xml',
        'views/line_discount_view.xml',
        'views/sheet_width_increase.xml',
    ],
}
