# -*- coding: utf-8 -*-
{
    'name': 'Acoona Default JP',
    'version': '16.0.1.0.0',
    'category': 'Localization/Japan',
    'summary': 'デフォルト言語と通貨を日本向けに設定',
    'description': """
Acoona Default JP
=================
- デフォルト言語を日本語（ja_JP）に設定
- デフォルト通貨を日本円（JPY）に設定
- 新規ユーザーの初期設定を自動化
    """,
    'author': 'SasukeTorii',
    'company': 'REV-C inc.',
    'maintainer': 'REV-C inc.',
    'website': 'https://company.rev-c.com',
    'depends': ['base', 'base_setup', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/default_data.xml',
        'views/res_config_settings_views.xml',
    ],
    'post_init_hook': 'post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
