# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # 会社関連（Settingsから編集できるようにrelatedで解放）
    company_l10n_jp_registration_number = fields.Char(
        related="company_id.l10n_jp_registration_number",
        string="Japan Registration Number",
        readonly=False,
    )
    company_l10n_jp_company_seal = fields.Binary(
        related="company_id.l10n_jp_company_seal",
        string="Company Seal (JP)",
        readonly=False,
    )

    # res.config.settings のビュー内でドメインに使用するための補助フィールド
    company_partner_id = fields.Many2one(
        related="company_id.partner_id",
        string="Company Partner",
        readonly=True,
    )

    # Acoona Invoice の機能を統合
    company_acoona_invoice_use_jp_layout = fields.Boolean(
        related="company_id.acoona_invoice_use_jp_layout",
        string="日本向け請求書レイアウトを使用",
        readonly=False,
    )
    company_acoona_invoice_department = fields.Char(
        related="company_id.acoona_invoice_department",
        string="請求部署名",
        readonly=False,
    )
    company_acoona_invoice_responsible_title = fields.Char(
        related="company_id.acoona_invoice_responsible_title",
        string="担当者肩書",
        readonly=False,
    )
    company_acoona_invoice_responsible_name = fields.Char(
        related="company_id.acoona_invoice_responsible_name",
        string="担当者氏名",
        readonly=False,
    )
    company_acoona_invoice_payment_note = fields.Text(
        related="company_id.acoona_invoice_payment_note",
        string="支払案内メッセージ",
        readonly=False,
    )
    company_acoona_invoice_footer_note = fields.Text(
        related="company_id.acoona_invoice_footer_note",
        string="請求書備考デフォルト",
        readonly=False,
    )
    company_l10n_jp_invoice_opening_text = fields.Char(
        related="company_id.l10n_jp_invoice_opening_text",
        string="請求書リード文 (JP)",
        readonly=False,
    )
    company_l10n_jp_invoice_bank_note = fields.Char(
        related="company_id.l10n_jp_invoice_bank_note",
        string="振込手数料注記 (JP)",
        readonly=False,
    )
