# -*- coding: utf-8 -*-

{
    'name': 'My Sales',
    'version': '1.0',
    'category': 'My Sales',
    'summary': 'My Sales',
    'description': 'My Sales',
    'depends': ['sales_team', 'res_localization_ept'],
    'data': ['data/ir_sequence_data.xml', 'security/sale_order_security.xml', 'security/ir.model.access.csv',
             'report/report_country.xml',
             'views/view_category.xml',
             'views/view_product.xml', 'views/view_uom.xml', 'views/view_partner.xml', 'views/view_sale_order.xml',
             'views/view_product_uom.xml', 'views/view_sales_team.xml', 'views/view_crm_lead.xml',
             'views/view_stock_warehouse.xml', 'views/view_stock_location.xml', 'views/view_purchase_order.xml',
             'views/view_stock_picking.xml', 'views/view_stock_move.xml', 'views/view_stock_inventory.xml',
             'views/view_stock_update.xml', 'views/view_account_tax.xml'
             ],
    'demo': [],
    'installable': True,
    'auto_install': False
}
