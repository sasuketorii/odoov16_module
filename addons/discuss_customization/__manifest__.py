# -*- coding: utf-8 -*-
{
    'name': 'Acoona Bot名前変更',
    'version': '16.0.1.0.1',
    'category': 'Discuss',
    'summary': 'OdooBotをAcoona Botに名前変更',
    'description': """
OdooBotの名前変更
=================
- OdooBotをAcoona Botに名前変更
    """,
    'author': 'SasukeTorii',
    'company': 'REV-C inc.',
    'maintainer': 'REV-C inc.',
    'website': 'https://company.rev-c.com',
    'depends': ['mail'],
    'data': [
        'data/rename_odoobot.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}
