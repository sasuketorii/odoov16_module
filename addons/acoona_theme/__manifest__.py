# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2021-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

{
    "name": "Acoona Theme",
    "description": """Acoona backend theme with fixed sidebar - clean implementation""",
    "summary": "Acoona backend theme with fixed sidebar",
    "category": "Themes/Backend",
    "version": "16.0.1.0.0",
    'author': 'REV-C inc.',
    'company': 'REV-C inc.',
    'maintainer': 'REV-C inc.',
    'website': "https://company.rev-c.com",
    "depends": ['base', 'web', 'mail'],
    "data": [
        'data/menu_material_icons.xml',
        'views/head_branding.xml',
        'views/layout.xml',
        'views/icons.xml',
        'views/login.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'acoona_theme/static/src/xml/styles.xml',
            'acoona_theme/static/src/xml/top_bar.xml',
            'acoona_theme/static/src/scss/theme_accent.scss',
            'acoona_theme/static/src/scss/navigation_bar.scss',
            'acoona_theme/static/src/scss/datetimepicker.scss',
            'acoona_theme/static/src/scss/theme.scss',
        'acoona_theme/static/src/scss/sidebar.scss',
        'acoona_theme/static/src/js/dialog_title_patch.js',
        'acoona_theme/static/src/js/chrome/sidebar_menu.js',
            'acoona_theme/static/src/js/fields/colors.js',
            'acoona_theme/static/src/js/webclient_branding.js',
        ],
        'web.assets_frontend': [
            'acoona_theme/static/src/scss/login.scss',
            'acoona_theme/static/src/js/frontend_branding.js',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/theme_screenshot.png',
    ],
    'license': 'LGPL-3',
    'pre_init_hook': 'acoona_pre_init_hook',
    'post_init_hook': 'acoona_post_init_hook',
    'uninstall_hook': 'acoona_uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
