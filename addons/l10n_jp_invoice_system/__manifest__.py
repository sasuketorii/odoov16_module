# -*- coding: utf-8 -*-
{
    "name": "Japan - Document Layout (Invoice)",
    "summary": "Add 'Japan' option to Document Layout for Japanese-style invoices.",
    "version": "16.0.1.0.0",
    "category": "Accounting/Localizations/Invoice",
    "website": "",
    "author": "",
    "license": "LGPL-3",
    # 既存のドキュメントレイアウト(QWeb)に依存
    "depends": [
        "web",
        "base",
        "base_setup",
        "account",
        # OCAの登録番号モジュールがあれば依存を追加するのが望ましいが、
        # 本リポジトリ単体で動作するよう optional に扱う。実運用では依存に加えることを推奨。
        # "l10n_jp_account_report_registration_number",
    ],
    "data": [
        "views/report_layouts.xml",
        "data/report_layout_data.xml",
        "views/res_config_settings_views.xml",
        "views/base_document_layout_views.xml",
        "views/report_invoice_document_jp.xml",
        "views/account_move_views.xml",
    ],
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
