# -*- coding: utf-8 -*-
#############################################################################
#
#    REV-C inc.
#
#    Copyright (C) 2024-TODAY REV-C inc.(<https://company.rev-c.com>)
#    Author: SasukeTorii(<https://company.rev-c.com>)
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
    "name": "Sasuke Backend Theme V16",
    "description": """Enhanced and optimized backend theme for Odoo 16 with improved CSS alignment and design consistency""",
    "summary": "Sasuke Backend Theme V16 is an enhanced theme with better UI/UX alignment",
    "category": "Themes/Backend",
    "version": "16.0.1.0.0",
    'author': 'SasukeTorii',
    'company': 'REV-C inc.',
    'maintainer': 'REV-C inc.',
    'website': "https://company.rev-c.com",
    "depends": ['base', 'web', 'mail'],
    "data": [
        'views/layout.xml',
        'views/icons.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'sasuke_backend_theme/static/src/xml/styles.xml',
            'sasuke_backend_theme/static/src/xml/top_bar.xml',
            'sasuke_backend_theme/static/src/scss/theme_accent.scss',
            'sasuke_backend_theme/static/src/scss/navigation_bar.scss',
            'sasuke_backend_theme/static/src/scss/datetimepicker.scss',
            'sasuke_backend_theme/static/src/scss/theme.scss',
            'sasuke_backend_theme/static/src/scss/sidebar.scss',
            'sasuke_backend_theme/static/src/js/chrome/sidebar_menu.js',
            'sasuke_backend_theme/static/src/js/fields/colors.js',
        ],
        'web.assets_frontend': [
            'sasuke_backend_theme/static/src/scss/login.scss',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/theme_screenshot.png',
    ],
    'license': 'LGPL-3',
    'pre_init_hook': 'test_pre_init_hook',
    'post_init_hook': 'test_post_init_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
