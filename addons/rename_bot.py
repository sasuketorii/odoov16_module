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
    reg = Registry.new('odoo', update_module=False)
    with reg.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})
        
        # OdooBotユーザーを検索して名前変更
        odoobot_partners = env['res.partner'].search([('name', '=', 'OdooBot')])
        for partner in odoobot_partners:
            logger.info(f'Renaming partner: {partner.name} (ID: {partner.id})')
            partner.write({'name': 'Acoona Bot'})
        
        # システムユーザーのパートナーも確認
        system_user = env['res.users'].search([('login', '=', '__system__')], limit=1)
        if system_user and system_user.partner_id:
            if system_user.partner_id.name == 'OdooBot':
                logger.info(f'Renaming system user partner: {system_user.partner_id.name}')
                system_user.partner_id.write({'name': 'Acoona Bot'})
        
        cr.commit()
        logger.info('Bot renamed successfully')
        
except Exception as e:
    logger.error(f'Error renaming bot: {e}')
    sys.exit(1)