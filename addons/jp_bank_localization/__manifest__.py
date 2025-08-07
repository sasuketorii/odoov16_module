# -*- coding: utf-8 -*-
{
    'name': '銀行口座日本ローカライズ',
    'version': '16.0.1.0.1',
    'category': 'Localization/Japan',
    'summary': '日本の銀行システムに対応した銀行口座管理',
    'description': """
日本の銀行口座管理モジュール
============================
日本の銀行システムに完全対応した銀行口座管理機能を提供します。

主な機能:
---------
* 銀行コード・支店コードの管理
* 口座種別（普通・当座・貯蓄）の選択
* カナ名義・漢字名義の管理
* 主要銀行マスタデータの提供
* 銀行振込用フォーマットの出力
* 全銀協フォーマット対応

特徴:
-----
* 4桁銀行コード・3桁支店コードの自動検証
* 7桁口座番号の形式チェック
* 半角カナ自動変換機能
* ゆうちょ銀行の記号番号変換対応
    """,
    'author': 'SasukeTorii',
    'company': 'REV-C inc.',
    'maintainer': 'REV-C inc.',
    'website': 'https://company.rev-c.com',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        'data/jp_bank_data.xml',
        'views/jp_bank_views.xml',
        'views/res_bank_views.xml',
        'views/res_partner_bank_views.xml',
        'views/menu_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}