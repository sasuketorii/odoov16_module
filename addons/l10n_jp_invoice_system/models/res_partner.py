# -*- coding: utf-8 -*-
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _l10n_jp_display_name_with_suffix(self, prefer_commercial=True):
        """Return display name with a Japanese honorific suffix.

        For business partners (companies), append "御中". For individuals, append
        "様". When ``prefer_commercial`` is ``True`` (default), we evaluate the
        commercial entity to decide whether the partner is treated as a company.
        """

        self.ensure_one()
        partner = self
        if prefer_commercial and self.commercial_partner_id:
            partner = self.commercial_partner_id

        name = partner.display_name or partner.name or ""
        suffix = "御中" if partner.is_company else "様"
        return f"{name}{suffix}" if name else suffix
