# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import re


class ResCompany(models.Model):
    _inherit = "res.company"

    # OCAの l10n_jp_account_report_registration_number が無い環境でも動くように、
    # 本モジュール側で登録番号フィールドを提供する（既存に同名があれば再定義されない）。
    l10n_jp_registration_number = fields.Char(
        string="Japan Registration Number",
        help="Qualified Invoice Registration No. (e.g., T1234567890123)",
    )

    # 日本の商習慣に合わせた会社印（任意）。PDF上で透かし的に重ねる用途。
    l10n_jp_company_seal = fields.Binary(
        string="Company Seal (JP)",
        attachment=True,
        help="Company seal image used in Japanese invoices.",
    )

    l10n_jp_default_invoice_bank_id = fields.Many2one(
        "res.partner.bank",
        string="Default Invoice Remit-to Bank (JP)",
        domain="[('partner_id', '=', partner_id)]",
        help="Default bank account to print on invoices.",
        check_company=True,
    )

    l10n_jp_show_bank_block = fields.Boolean(
        string="Show Bank Block on Invoices (JP)",
        default=True,
        help="If enabled, the invoice prints a bank account section.",
    )

    @api.constrains("l10n_jp_registration_number")
    def _check_jp_registration_number(self):
        pattern = re.compile(r"^T\d{13}$")
        for rec in self:
            if rec.l10n_jp_registration_number and not pattern.match(rec.l10n_jp_registration_number):
                raise ValidationError(
                    "Japan Registration Number must be 'T' followed by 13 digits."
                )

    @api.model
    def _ensure_japan_report_layout(self):
        view = self.env.ref("l10n_jp_invoice_system.external_layout_jp", raise_if_not_found=False)
        if not view:
            return

        layout_model = self.env["report.layout"].sudo()
        layout_model._ensure_japan_layout()

    @api.model
    def _register_hook(self):
        res = super()._register_hook()
        self._ensure_japan_report_layout()
        return res
