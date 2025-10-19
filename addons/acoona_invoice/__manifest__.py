# -*- coding: utf-8 -*-
{
    "name": "Acoona Invoice (Japan)",
    "summary": "日本向けの請求書レイアウトと設定を提供します。",
    "version": "16.0.1.0.0",
    "category": "Accounting/Localizations/Invoice",
    "website": "",
    "author": "",
    "license": "LGPL-3",
    "depends": [
        "account",
        "l10n_jp_invoice_system",
    ],
    "data": [
        "views/res_config_settings_views.xml",
        "views/report_invoice_document.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
}
