from odoo import models
from odoo.tools import format_date


class AccountMove(models.Model):
    """請求書レポートで利用する日本向けユーティリティを提供する。"""

    _inherit = "account.move"

    def _acoona_invoice_recipient_label(self):
        """取引先名称の末尾に適切な敬称を付与して返す。"""
        self.ensure_one()
        partner = self.partner_id.commercial_partner_id or self.partner_id
        name = partner.display_name or partner.name or ""
        suffix = "御中" if partner.is_company else "様"
        return f"{name}{suffix}" if name else suffix

    def _acoona_invoice_format_date(self, date_value):
        """請求書上で利用する日付表記をロケールに合わせて整形する。"""
        if not date_value:
            return ""
        lang_code = self.env.context.get("lang") or self.env.user.lang or "ja_JP"
        return format_date(self.env, date_value, lang=lang_code)

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
