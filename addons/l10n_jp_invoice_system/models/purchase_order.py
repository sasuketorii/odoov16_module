# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models
from odoo.tools import float_is_zero, format_date, format_datetime


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    @staticmethod
    def _l10n_jp_round_to_minute(value):
        if not value:
            return value
        if isinstance(value, str):
            value_dt = fields.Datetime.from_string(value)
        elif isinstance(value, datetime):
            value_dt = value
        else:
            return value
        value_dt = value_dt.replace(second=0, microsecond=0)
        return fields.Datetime.to_string(value_dt)

    @classmethod
    def _l10n_jp_prepare_datetime_vals(cls, vals):
        if not vals:
            return vals
        result = dict(vals)
        for field_name in ("date_order", "date_planned"):
            if field_name in result and result[field_name]:
                result[field_name] = cls._l10n_jp_round_to_minute(result[field_name])
        return result

    @api.model
    def create(self, vals):
        vals = self._l10n_jp_prepare_datetime_vals(vals)
        return super().create(vals)

    def write(self, vals):
        vals = self._l10n_jp_prepare_datetime_vals(vals)
        return super().write(vals)

    def _l10n_jp_address_lines(self, partner):
        partner = partner.commercial_partner_id or partner
        lines = []
        if partner.zip:
            lines.append(f"〒{partner.zip}")
        region_parts = [partner.state_id.name or "", partner.city or "", partner.street or ""]
        region = "".join(part for part in region_parts if part)
        if region:
            lines.append(region)
        if partner.street2:
            lines.append(partner.street2)
        return lines

    def _l10n_jp_vendor_label(self):
        self.ensure_one()
        partner = self.partner_id or self.env["res.partner"]
        if not partner:
            return ""
        return partner._l10n_jp_display_name_with_suffix()

    def _l10n_jp_format_date(self, date_value):
        if not date_value:
            return ""
        return format_date(self.env, date_value)

    def _l10n_jp_format_datetime(self, datetime_value, dt_format="yyyy年MM月dd日 HH:mm", tz=None):
        self.ensure_one()
        if not datetime_value:
            return ""
        if tz:
            target_tz = tz
        else:
            context_tz = self.env.context.get("tz")
            user_tz = self.env.user.tz
            company_tz = self.company_id.partner_id.tz
            target_tz = context_tz or user_tz or company_tz or "Asia/Tokyo"
        tz = target_tz
        return format_datetime(self.env, datetime_value, tz=tz, dt_format=dt_format)

    def _l10n_jp_line_tax_display(self, line):
        taxes = getattr(line, "taxes_id", False) or getattr(line, "tax_id", False) or getattr(line, "tax_ids", False)
        rates = []
        if taxes:
            for tax in taxes:
                if tax.amount is not None:
                    rates.append(f"{tax.amount:g}%")
        display = ", ".join(sorted(set(rates)))
        if self._l10n_jp_is_reduced_rate(line):
            display = f"{display}※" if display else "※"
        return display

    def _l10n_jp_is_reduced_rate(self, line):
        taxes = getattr(line, "taxes_id", False) or getattr(line, "tax_id", False) or getattr(line, "tax_ids", False)
        if not taxes:
            return False
        for tax in taxes:
            if tax.amount is not None and float_is_zero(tax.amount - 8.0, precision_digits=1):
                return True
        return False

    def _l10n_jp_tax_summary(self):
        self.ensure_one()
        currency = self.currency_id
        summary_map = {}
        for line in self.order_line:
            taxes = line.taxes_id
            if not taxes:
                continue
            res = taxes._origin.compute_all(
                line.price_unit,
                currency,
                line.product_qty,
                product=line.product_id,
                partner=self.partner_id,
            )
            for tax_res in res.get("taxes", []):
                tax_id = tax_res["id"]
                entry = summary_map.setdefault(
                    tax_id,
                    {
                        "name": tax_res["name"],
                        "tax": 0.0,
                        "base": 0.0,
                    },
                )
                entry["tax"] += tax_res["amount"]
                entry["base"] += tax_res["base"]

        summary = []
        for entry in summary_map.values():
            if float_is_zero(entry["base"], precision_rounding=currency.rounding) and float_is_zero(
                entry["tax"], precision_rounding=currency.rounding
            ):
                continue
            summary.append(entry)
        return summary

    def _l10n_jp_company_bank_info(self):
        self.ensure_one()
        company = self.company_id
        partner = company.partner_id
        bank = False
        if partner:
            partner_banks = partner.bank_ids.filtered(lambda b: b.allow_out_payment)
            if not partner_banks:
                partner_banks = partner.bank_ids
            bank = partner_banks[:1]
        if not bank and company.bank_ids:
            bank = company.bank_ids[:1]
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
        holder = bank.acc_holder_name or holder_kana or company.name or ""
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
        note = company.l10n_jp_invoice_bank_note
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
