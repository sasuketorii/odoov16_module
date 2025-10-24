{
    "name": "Acoona Base Translations",
    "summary": "Bundle Japanese translations for base and Acoona theme",
    "version": "16.0.1.0.0",
    "category": "Localization",
    "author": "Acoona",
    "website": False,
    "license": "LGPL-3",
    "depends": [
        "base",
        "acoona_theme",
        "purchase",
    ],
    "data": [
        "data/ir_ui_menu_translation.xml",
    ],
    "post_init_hook": "post_init_hook",
    "post_load": "post_load",
    "application": False,
    "auto_install": False,
    "installable": True
}
