# -*- coding: utf-8 -*-

def post_init_hook(cr, registry):
    """インストール時にOdooBotをAcoona Botに名前変更"""
    from odoo import api, SUPERUSER_ID
    
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # OdooBotのパートナーレコードを検索して名前変更
    odoobot_partners = env['res.partner'].search([('name', '=', 'OdooBot')])
    for partner in odoobot_partners:
        partner.write({'name': 'Acoona Bot'})
    
    # システムユーザーのパートナーも確認
    system_user = env['res.users'].search([('login', '=', '__system__')], limit=1)
    if system_user and system_user.partner_id:
        if system_user.partner_id.name == 'OdooBot':
            system_user.partner_id.write({'name': 'Acoona Bot'})