# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    acoona_hide_devtools_2 = fields.Boolean(
        string="Hide Developer Tools",
        default=True,
        config_parameter="acoona_branding2.hide_devtools",
    )

    acoona_mail_debrand = fields.Boolean(
        string="Remove Odoo branding from emails",
        default=True,
        config_parameter="acoona_branding2.mail_debrand",
        help="Remove Odoo links/branding from outgoing emails.",
    )
