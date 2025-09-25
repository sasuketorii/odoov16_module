#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import odoo
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

odoo.tools.config.parse_config([
    '--database=odoo',
    '--db_user=odoo',
    '--db_password=odoo',
    '--db_host=db',
    '--addons-path=/mnt/extra-addons'
])

from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

try:
    reg = Registry.new('odoo', update_module=True)
    with reg.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        # コマンドライン引数からモジュール名を取得
        module_name = sys.argv[1] if len(sys.argv) > 1 else 'acoona_jp_prefecture_localization'
        
        module = env['ir.module.module'].search([('name', '=', module_name)])
        
        if module:
            if module.state != 'installed':
                logger.info(f'Installing module: {module.name} (current state: {module.state})')
                module.button_immediate_install()
                cr.commit()
                logger.info('Module installed successfully')
            else:
                logger.info(f'Module already installed: {module.name}')
        else:
            logger.error(f'Module not found: {module_name}')
            sys.exit(1)
            
except Exception as e:
    logger.error(f'Error installing module: {e}')
    sys.exit(1)