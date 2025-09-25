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
    "name": "Sasuke Backend Theme V2",
    "description": """Code Backend Theme with fixed sidebar - Clean implementation""",
    "summary": "Code Backend Theme with always visible sidebar",
    "category": "Themes/Backend",
    "version": "16.0.1.0.0",
    'author': 'SasukeTorii (based on Cybrosys)',
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
            'sasuke_backend_theme2/static/src/xml/styles.xml',
            'sasuke_backend_theme2/static/src/xml/top_bar.xml',
            'sasuke_backend_theme2/static/src/scss/theme_accent.scss',
            'sasuke_backend_theme2/static/src/scss/navigation_bar.scss',
            'sasuke_backend_theme2/static/src/scss/datetimepicker.scss',
            'sasuke_backend_theme2/static/src/scss/theme.scss',
            'sasuke_backend_theme2/static/src/scss/sidebar.scss',
            'sasuke_backend_theme2/static/src/js/chrome/sidebar_menu.js',
            'sasuke_backend_theme2/static/src/js/fields/colors.js',
        ],
        'web.assets_frontend': [
            'sasuke_backend_theme2/static/src/scss/login.scss',
        ],
    },
    'images': [
        'static/description/banner.png',
        'static/description/theme_screenshot.png',
    ],
    'license': 'LGPL-3',
    'pre_init_hook': 'test_pre_init_hook',
    'post_init_hook': 'test_post_init_hook',
    'uninstall_hook': 'test_uninstall_hook',
    'installable': True,
    'application': False,
    'auto_install': False,
}
