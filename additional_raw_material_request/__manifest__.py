{
    'name': 'Additional Raw Material Request',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing/Manufacturing',
    'summary': 'Request additional raw materials for manufacturing orders',
    'description': """
        This module allows users to request additional raw materials for manufacturing orders.
    """,
    'depends': ['mrp', 'product', 'uom', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/ir_sequence_data.xml',
        'views/additional_raw_material_request_views.xml',
        'views/mrp_production_views.xml',
        'reports/additional_raw_material_request_report.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
