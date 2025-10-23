{
    "name": "Acoona Branding",
    "summary": "General Settings: Acoona branding + toggle for Developer Tools.",
    "version": "16.0.2.0.0",
    "category": "Tools",
    "website": "https://company.rev-c.com",
    "author": "Acoona",
    "license": "LGPL-3",
    "depends": ["base_setup", "portal", "mail"],
    "data": [
        "views/res_config_settings_views.xml",
        "views/backend_debranding.xml",
        "views/portal_debranding.xml",
        "views/upgrade_debranding.xml",
        "views/about_debranding.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "assets": {
        "web.assets_backend": [
            "acoona_branding/static/src/scss/debranding.scss",
            "acoona_branding/static/src/js/menu_hide_apps.js",
        ]
    }
}
