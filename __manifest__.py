# -*- coding: utf-8 -*-
{
    'name': "openacademy",

    'summary': """ Manage training""",

    'description': """ Open Academy module for training management:
                        - training courses
                        - training sessions
                        - participant registration
                   """,

    'author': "Lari Feuzeu",
    'website': "https://www.its.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'board',   'web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/openacademy.xml',
        'views/partner.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/session_board.xml',
        'views/reports.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
