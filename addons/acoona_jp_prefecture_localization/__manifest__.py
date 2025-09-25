# -*- coding: utf-8 -*-
{
    'name': '日本都道府県ローカライズ',
    'version': '16.0.1.0.0',
    'category': 'Localization/Japan',
    'summary': '日本の都道府県名を日本語で表示',
    'description': """
日本都道府県ローカライズモジュール
=====================================

このモジュールは日本の都道府県名を英語から日本語に自動変換します。

主な機能:
---------
* 47都道府県の日本語名称設定
* 都道府県コードの統一化（01〜47）
* 既存データの自動更新

対応内容:
---------
* 北海道 (Hokkaido) → 北海道 [01]
* 青森県 (Aomori) → 青森県 [02]
* 岩手県 (Iwate) → 岩手県 [03]
* その他44都道府県

注意事項:
---------
* インストール時に既存の都道府県データを更新します
* アンインストール時でも日本語名は保持されます
    """,
    'author': 'SasukeTorii',
    'company': 'REV-C inc.',
    'maintainer': 'REV-C inc.',
    'website': 'https://company.rev-c.com',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/res_country_state_data.xml',  # hooks.pyで処理するため無効化
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
}