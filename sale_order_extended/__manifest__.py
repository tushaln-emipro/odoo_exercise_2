# -*- coding: utf-8 -*-

{
    'name': 'Sale Order Extended',
    'version': '1.0',
    'category': 'Sale Order Extended',
    'summary': 'Sale Order Extended',
    'description': 'Sale Order Extended',
    'depends': ['sale_crm'],
    'data': ['data/tag_data.xml', 'views/view_sale_order.xml', 'views/view_product.xml',
             'views/view_stock_picking.xml', 'views/view_purchase_order.xml', 'report/report_salesby_salesperson.xml',
             'views/view_project_tags.xml'],
    'demo': [],
    'installable': True,
    'auto_install': False
}
