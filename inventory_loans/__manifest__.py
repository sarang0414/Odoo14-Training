{
    'name': 'Inventory Loans',
    'version': '18.0.1.0.0',
    'summary': 'Manage Inventory Loans (Loan In/Loan Out)',
    'description': """
    This module creates a mechanism to handle Inventory Loans.
    It adds a loan type to stock transfers, moves, and quants to separate loan stock from regular stock.
    """,
    'category': 'Inventory/Inventory',
    'author': 'Antigravity',
    'depends': ['stock', 'stock_account'],
    'data': [
        'views/stock_picking_view.xml',
        'data/inventory_loans_data.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
