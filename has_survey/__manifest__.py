# -*- coding: utf-8 -*-
{
    'name': 'HAS - Survey',
    #'version': '1.0.0',
    'description': """ Agregar vista de evaluaciones """,
    'summary': """ Agregar vista de evaluaciones """,
    'author': 'HAS',
    'website': '',
    'category': '',
    'depends': ['base','survey'],
    "data": [
        "views/evaluaciones_views.xml",
        "security/ir.model.access.csv",
        "views/presenciales_views.xml",
        "views/webinars_views.xml",
        "views/survey_templates.xml",
        #"views/survey_user_input_views.xml",
    ],
    'application': True,
    #'installable': True,
    #'auto_install': False,
    'license': 'LGPL-3',
}
