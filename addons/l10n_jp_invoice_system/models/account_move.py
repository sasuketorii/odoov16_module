# -*- coding: utf-8 -*-
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_jp_invoice_bank_id = fields.Many2one(
        "res.partner.bank",
        string="Invoice Remit-to Bank (JP)",
        domain="[('partner_id', '=', company_partner_id)]",
        help="Bank account to print on the invoice. If not set, the company's default will be used.",
        check_company=True,
        default=lambda self: self._default_l10n_jp_invoice_bank_id(),
    )

    # ドメイン参照用の補助フィールド（ビュー内で不可視配置前提）
    company_partner_id = fields.Many2one(
        related="company_id.partner_id",
        string="Company Partner",
        readonly=True,
    )

    @api.model
    def _default_l10n_jp_invoice_bank_id(self):
        company = self.env.company
        return company.l10n_jp_default_invoice_bank_id.id if company.l10n_jp_default_invoice_bank_id else False

    @api.onchange("company_id")
    def _onchange_company_set_default_bank(self):
        if self.company_id and not self.l10n_jp_invoice_bank_id:
            self.l10n_jp_invoice_bank_id = (
                self.company_id.l10n_jp_default_invoice_bank_id
            )
