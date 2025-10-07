# -*- encoding: utf-8 -*-

{
    'name': 'Colombian Cities & States',
    'description': 'Cities and States for Colombia',
    'category': 'Localization',
    'license': 'AGPL-3',
    'author': 'Pragmatic Ingeniería S.A.S',
    'website': 'https.//www.pragmaticingenieria.com',
    'version': '1.0',
    'depends': [
        'base',        
    ],
    'data': [
        'data/res.country.state.csv',
        'data/res.country.state.city.csv',
        'data/res.partner.title.csv',
        'res_partner_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
