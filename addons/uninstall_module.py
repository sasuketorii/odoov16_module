#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper script for uninstalling Odoo modules inside Docker stack."""
import logging
import sys

import odoo
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_DB = 'odoo'

def main():
    module_name = sys.argv[1] if len(sys.argv) > 1 else None
    if not module_name:
        logger.error('Usage: uninstall_module.py <module_name> [db_name]')
        sys.exit(1)

    db_name = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DB

    odoo.tools.config.parse_config([
        f'--database={db_name}',
        '--db_user=odoo',
        '--db_password=odoo',
        '--db_host=db',
        '--addons-path=/mnt/extra-addons'
    ])

    try:
        registry = Registry.new(db_name, update_module=False)
        with registry.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            module = env['ir.module.module'].search([('name', '=', module_name)])
            if not module:
                logger.error('Module not found: %s', module_name)
                sys.exit(1)
            if module.state != 'installed':
                logger.info('Module %s is not installed (state=%s)', module_name, module.state)
                return
            logger.info('Uninstalling module: %s', module_name)
            module.button_immediate_uninstall()
            cr.commit()
            logger.info('Module uninstalled successfully')
    except Exception as exc:
        logger.error('Error uninstalling module: %s', exc)
        sys.exit(1)

if __name__ == '__main__':
    main()
