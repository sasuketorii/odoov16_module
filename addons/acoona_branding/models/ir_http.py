# -*- coding: utf-8 -*-
"""Expose Acoona-specific toggles in the web client session info."""

from odoo import api, models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @api.model
    def session_info(self):
        info = super().session_info()

        hide_devtools = (
            self.env["ir.config_parameter"].sudo().get_param(
                "acoona_branding.hide_devtools"
            )
            or "True"
        )

        info["acoona_hide_devtools"] = hide_devtools.lower() in {"true", "1"}
        return info
