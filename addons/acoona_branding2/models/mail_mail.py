# -*- coding: utf-8 -*-
"""メール送信時のOdooブランド除去ロジック。"""

from odoo import api, models

from .mail_branding_utils import clean_odoo_branding, is_mail_debranding_enabled


class MailMail(models.Model):
    _inherit = "mail.mail"

    def _clean_payload(self, html_payload):
        if html_payload and is_mail_debranding_enabled(self.env):
            return clean_odoo_branding(html_payload)
        return html_payload

    @api.model
    def create(self, vals):
        if vals.get("body_html"):
            vals["body_html"] = self._clean_payload(vals["body_html"])
        return super().create(vals)

    def write(self, vals):
        if vals.get("body_html"):
            vals["body_html"] = self._clean_payload(vals["body_html"])
        return super().write(vals)

    def _send_prepare_body(self):
        body = super()._send_prepare_body()
        return self._clean_payload(body)
