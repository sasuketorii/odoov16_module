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

    company_l10n_jp_default_invoice_bank_id = fields.Many2one(
        related="company_id.l10n_jp_default_invoice_bank_id",
        comodel_name="res.partner.bank",
        string="Default Invoice Remit-to Bank (JP)",
        readonly=False,
        domain="[('partner_id', '=', company_partner_id)]",
    )
    company_l10n_jp_show_bank_block = fields.Boolean(
        related="company_id.l10n_jp_show_bank_block",
        string="Show Bank Block on Invoices (JP)",
        readonly=False,
    )

    # res.config.settings のビュー内でドメインに使用するための補助フィールド
    company_partner_id = fields.Many2one(
        related="company_id.partner_id",
        string="Company Partner",
        readonly=True,
    )
