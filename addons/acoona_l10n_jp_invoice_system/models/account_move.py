# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.tools import float_is_zero, format_date

from .pdf_filename import build_pdf_filename


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

    l10n_jp_transaction_date = fields.Date(
        string="取引日",
        help="取引が発生した日付。未入力の場合、請求書には表示されません。",
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
        partner = company.partner_id
        if not partner:
            return False
        banks = partner.bank_ids.filtered(lambda b: b.allow_out_payment)
        if not banks:
            banks = partner.bank_ids
        if not banks:
            banks = company.bank_ids
        return banks[:1].id if banks else False

    @api.onchange("company_id")
    def _onchange_company_set_default_bank(self):
        if self.company_id and not self.l10n_jp_invoice_bank_id:
            partner = self.company_id.partner_id
            banks = partner.bank_ids.filtered(lambda b: b.allow_out_payment) if partner else self.env["res.partner.bank"]
            if partner and not banks:
                banks = partner.bank_ids
            if not banks:
                banks = self.company_id.bank_ids
            self.l10n_jp_invoice_bank_id = banks[:1]

    # Acoona Invoice の機能を統合
    def _acoona_invoice_recipient_label(self):
        """取引先名称の末尾に適切な敬称を付与して返す。"""
        self.ensure_one()
        partner = self.partner_id or self.env["res.partner"]
        if not partner:
            return ""
        return partner._l10n_jp_display_name_with_suffix()

    def _acoona_invoice_format_date(self, date_value):
        """請求書上で利用する日付表記をロケールに合わせて整形する。"""
        if not date_value:
            return ""
        return format_date(self.env, date_value)

    def _acoona_invoice_responsible_lines(self):
        """発行元の部署・担当者情報を行ごとに返す。"""
        self.ensure_one()
        company = self.company_id
        lines = []
        if company.acoona_invoice_department:
            lines.append(company.acoona_invoice_department)
        responsible_name = company.acoona_invoice_responsible_name
        if responsible_name:
            if company.acoona_invoice_responsible_title:
                lines.append(f"{company.acoona_invoice_responsible_title} {responsible_name}")
            else:
                lines.append(responsible_name)
        return lines

    def _get_jp_tax_summary(self):
        """Return tax totals grouped for the Japanese summary table."""
        self.ensure_one()
        currency = self.currency_id

        def _add_summary_line(summary_map, key, name, base, tax):
            if float_is_zero(base, precision_rounding=currency.rounding) and float_is_zero(
                tax, precision_rounding=currency.rounding
            ):
                return
            entry = summary_map.setdefault(
                key,
                {
                    "name": name or "",
                    "base": 0.0,
                    "tax": 0.0,
                },
            )
            entry["base"] += base
            entry["tax"] += tax

        totals = self.tax_totals or {}
        summary_map = {}

        for group in totals.get("groups_by_tax_group", []) or []:
            _add_summary_line(
                summary_map,
                group.get("group_key") or group.get("tax_group_id") or group.get("tax_group_name"),
                group.get("tax_group_name"),
                group.get("tax_group_base_amount", 0.0),
                group.get("tax_group_amount", 0.0),
            )

        if not summary_map and totals.get("groups_by_subtotal"):
            for entries in totals.get("groups_by_subtotal", {}).values():
                for group in entries:
                    _add_summary_line(
                        summary_map,
                        group.get("group_key") or group.get("tax_group_id") or group.get("tax_group_name"),
                        group.get("tax_group_name"),
                        group.get("tax_group_base_amount", 0.0),
                        group.get("tax_group_amount", 0.0),
                    )

        if summary_map:
            return list(summary_map.values())

        # Fallback for cases where tax_totals is empty or lacks group info (e.g., draft invoices)
        for line in self.invoice_line_ids.filtered(lambda l: l.display_type not in ("line_section", "line_note")):
            taxes = line.tax_ids
            if not taxes:
                continue

            price = line.price_unit
            if line.discount:
                price *= 1 - (line.discount / 100.0)

            line_currency = line.currency_id or currency
            res = taxes._origin.compute_all(
                price,
                line_currency,
                line.quantity,
                product=line.product_id,
                partner=line.partner_id,
            )
            for tax_res in res.get("taxes", []):
                base = tax_res.get("base", 0.0)
                tax = tax_res.get("amount", 0.0)
                if line_currency != currency:
                    company = self.company_id
                    date = self.invoice_date or fields.Date.context_today(self)
                    base = line_currency._convert(base, currency, company, date)
                    tax = line_currency._convert(tax, currency, company, date)
                _add_summary_line(summary_map, tax_res.get("id"), tax_res.get("name"), base, tax)

        return list(summary_map.values())

    def _get_jp_bank_info(self):
        """Prepare bank information lines for the invoice template."""
        self.ensure_one()
        partner = self.company_id.partner_id
        bank = self.l10n_jp_invoice_bank_id
        if not bank and partner:
            partner_banks = partner.bank_ids.filtered(lambda b: b.allow_out_payment)
            if not partner_banks:
                partner_banks = partner.bank_ids
            bank = partner_banks[:1]
        if not bank:
            bank = self.company_id.bank_ids[:1]
        if not bank:
            return {}

        name = (bank.bank_id and bank.bank_id.name) or getattr(bank, "bank_name", False) or ""
        branch_code = (
            getattr(bank, "jpBranchCode", False)
            or getattr(bank, "l10n_jp_branch_code", False)
            or getattr(bank, "branch_code", False)
        )
        branch_name = (
            getattr(bank, "jpBranchName", False)
            or getattr(bank, "l10n_jp_branch_name", False)
            or getattr(bank, "bank_branch_name", False)
        )
        if not branch_name and getattr(bank, "bank_name", False) and bank.bank_name != name:
            branch_name = bank.bank_name

        acc_type_label = self._l10n_jp_map_account_type(
            getattr(bank, "jpAccountType", False)
        ) or self._l10n_jp_map_account_type(bank.acc_type)

        branch_part = ""
        branch_code = branch_code.strip() if isinstance(branch_code, str) else branch_code
        branch_name = branch_name.strip() if isinstance(branch_name, str) else branch_name
        if branch_name and branch_code:
            branch_part = f"{branch_name}(支店番号: {branch_code})"
        elif branch_name:
            branch_part = branch_name
        elif branch_code:
            branch_part = f"支店番号: {branch_code}"

        holder_kana = (
            getattr(bank, "jpAccountHolderKana", False)
            or getattr(bank, "acc_holder_name_kana", False)
        )
        holder = bank.acc_holder_name or holder_kana or self.company_id.name or ""
        lines = []
        bank_line = " ".join(part for part in [name, branch_part] if part).strip()
        if bank_line:
            lines.append(bank_line)
        account_line = " ".join(part for part in [acc_type_label, bank.acc_number] if part).strip()
        if account_line:
            lines.append(account_line)
        if holder_kana:
            lines.append(holder_kana)
        elif holder:
            lines.append(holder)
        note = self.company_id.l10n_jp_invoice_bank_note
        return {
            "lines": [line for line in lines if line],
            "note": note,
        }

    @staticmethod
    def _l10n_jp_map_account_type(value):
        if not value:
            return ""
        mapping = {
            "bank": "普通",
            "banks": "普通",
            "ordinary": "普通",
            "ordinary account": "普通",
            "savings": "普通",
            "savings account": "普通",
            "deposit": "普通預金",
            "futsu": "普通",
            "futsuu": "普通",
            "普通": "普通",
            "普通預金": "普通預金",
            "普通預金口座": "普通預金",
            "普通口座": "普通",
            "checking": "当座",
            "checking account": "当座",
            "current": "当座",
            "current account": "当座",
            "当座": "当座",
            "当座預金": "当座預金",
            "当座預金口座": "当座預金",
            "当座口座": "当座",
            "general": "総合",
            "general account": "総合",
            "sogo": "総合",
            "総合": "総合",
            "総合口座": "総合",
        }
        text = str(value).strip()
        if not text:
            return ""
        lowered = text.lower()
        mapped = mapping.get(lowered)
        if mapped:
            return mapped
        return text

    def _get_jp_address_lines(self, partner):
        """Return address lines in JP format: zip, prefecture+city+street, building."""
        partner = partner.commercial_partner_id or partner
        lines = []
        if partner.zip:
            lines.append(f"〒{partner.zip}")
        region_parts = [partner.state_id.name or '', partner.city or '', partner.street or '']
        region_line = ''.join(part for part in region_parts if part)
        if region_line:
            lines.append(region_line)
        building = getattr(partner, "street2", False)
        if building:
            lines.append(building)
        return lines

    def _get_jp_line_tax_display(self, line):
        self.ensure_one()
        rates = []
        for tax in line.tax_ids:
            if tax.amount is None:
                continue
            rates.append(f"{tax.amount:g}%")
        display = ", ".join(sorted(set(rates)))
        if self._is_jp_reduced_rate(line):
            display = f"{display}※" if display else "※"
        return display

    def _is_jp_reduced_rate(self, line):
        self.ensure_one()
        for tax in line.tax_ids:
            if tax.amount is None:
                continue
            if float_is_zero(tax.amount - 8.0, precision_digits=1):
                return True
        return False

    def _l10n_jp_report_title(self):
        """Return the most relevant title string shown on JP documents."""
        self.ensure_one()
        candidates = [
            getattr(self, "payment_reference", False),
            getattr(self, "invoice_payment_ref", False),
            getattr(self, "invoice_origin", False),
            self.name,
        ]
        for candidate in candidates:
            if candidate:
                return candidate
        return ""

    def _get_report_base_filename(self):
        self.ensure_one()
        base_filename = super()._get_report_base_filename()
        partner_label = self._acoona_invoice_recipient_label()
        title = self._l10n_jp_report_title()
        filename = build_pdf_filename("請求書", partner_label, title)
        return filename or base_filename
