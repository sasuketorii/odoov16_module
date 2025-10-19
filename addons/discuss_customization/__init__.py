# -*- coding: utf-8 -*-
from . import models


def post_init_hook(cr, registry):
    """インストール後にOdooBotをAcoona Botへ名称・画像ともに統一する"""
    from base64 import b64encode
    from odoo import api, SUPERUSER_ID
    from odoo.modules.module import get_module_resource

    env = api.Environment(cr, SUPERUSER_ID, {})

    image_bytes = None
    image_path = get_module_resource('discuss_customization', 'static', 'img', 'acoona_bot.png')
    if image_path:
        with open(image_path, 'rb') as image_file:
            image_bytes = b64encode(image_file.read())

    partner_vals = {'name': 'Acoona Bot'}
    if image_bytes:
        partner_vals['image_1920'] = image_bytes

    partners = env['res.partner'].with_context(active_test=False).search([('name', 'in', ['OdooBot', 'Acoona Bot'])])
    if partners:
        partners.write(partner_vals)

    system_user = env['res.users'].with_context(active_test=False).search([('login', '=', '__system__')], limit=1)
    if system_user and system_user.partner_id:
        system_user.partner_id.write(partner_vals)

    if image_bytes:
        attachments = env['ir.attachment'].sudo().search([
            ('res_model', '=', 'res.partner'),
            ('res_field', '=', 'image_1920'),
            ('res_id', 'in', env['res.partner'].with_context(active_test=False).search([('name', '=', 'Acoona Bot')]).ids),
        ])
        if attachments:
            attachments.write({
                'name': 'acoona_bot.png',
                'mimetype': 'image/png',
            })
