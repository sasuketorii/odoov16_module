# -*- coding: utf-8 -*-
from base64 import b64encode
from odoo import models
from odoo.modules.module import get_module_resource


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def init(self):
        """モジュール読み込み時にOdooBotの名称と画像をAcoona Botへ統一する"""
        super().init()
        env = self.env

        # 名称の統一
        partners = env['res.partner'].with_context(active_test=False).search([('name', '=', 'OdooBot')])
        if partners:
            partners.write({'name': 'Acoona Bot'})

        system_user = env['res.users'].with_context(active_test=False).search([('login', '=', '__system__')], limit=1)
        if system_user and system_user.partner_id:
            if system_user.partner_id.name != 'Acoona Bot':
                system_user.partner_id.write({'name': 'Acoona Bot'})

        # 画像および添付ファイルの更新
        image_path = get_module_resource('discuss_customization', 'static', 'img', 'acoona_bot.png')
        if image_path:
            with open(image_path, 'rb') as image_file:
                image_data = b64encode(image_file.read())
            targets = env['res.partner'].with_context(active_test=False).search([('name', '=', 'Acoona Bot')])
            if targets:
                targets.write({'image_1920': image_data})
                attachments = env['ir.attachment'].sudo().search([
                    ('res_model', '=', 'res.partner'),
                    ('res_field', '=', 'image_1920'),
                    ('res_id', 'in', targets.ids),
                ])
                if attachments:
                    attachments.write({
                        'name': 'acoona_bot.png',
                        'mimetype': 'image/png',
                    })
