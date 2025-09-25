# -*- coding: utf-8 -*-
# 設定ウィザード拡張: デフォルト言語・通貨の日本向け初期値
from odoo import fields, models, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # 設定: 言語（"default_" 接頭辞は使わない → Odooのdefault_*分類を回避）
    acoona_default_lang = fields.Selection(
        selection='_get_languages',
        string='デフォルト言語',
        config_parameter='web.default_lang',
        default='ja_JP',
        help='新規ユーザーのデフォルト言語を設定します',
    )

    # 設定: 通貨（"default_" 接頭辞は使わない）
    acoona_default_currency_id = fields.Many2one(
        'res.currency',
        string='デフォルト通貨',
        config_parameter='base.default_currency_id',
        default=lambda self: self.env.ref('base.JPY', raise_if_not_found=False),
        help='会社のデフォルト通貨を設定します',
    )

    @api.model
    def _get_languages(self):
        """利用可能な言語コード/名称の一覧を取得（全言語）"""
        langs = self.env['res.lang'].search([])
        return [(l.code, l.name) for l in langs]

    @api.model
    def get_values(self):
        """設定値を取得"""
        res = super(ResConfigSettings, self).get_values()

        # デフォルト言語の取得
        default_lang = self.env['ir.config_parameter'].sudo().get_param('web.default_lang', 'ja_JP')
        res.update(acoona_default_lang=default_lang)

        # デフォルト通貨の取得
        default_currency_id = self.env['ir.config_parameter'].sudo().get_param('base.default_currency_id')
        if default_currency_id:
            res.update(acoona_default_currency_id=int(default_currency_id))

        return res

    def set_values(self):
        """設定値を保存"""
        super(ResConfigSettings, self).set_values()

        # デフォルト言語の設定
        if self.acoona_default_lang:
            self.env['ir.config_parameter'].sudo().set_param('web.default_lang', self.acoona_default_lang)

        # デフォルト通貨の設定
        if self.acoona_default_currency_id:
            self.env['ir.config_parameter'].sudo().set_param('base.default_currency_id', self.acoona_default_currency_id.id)

            # 既存会社の通貨は安全に更新（仕訳のない会社のみ）
            aml_model = self.env['account.move.line'] if 'account.move.line' in self.env else None
            for company in self.env['res.company'].search([]):
                can_update = True
                if aml_model is not None:
                    has_moves = bool(aml_model.sudo().search([('company_id', '=', company.id)], limit=1))
                    can_update = not has_moves
                if can_update:
                    company.write({'currency_id': self.acoona_default_currency_id.id})
