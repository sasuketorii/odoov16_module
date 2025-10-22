# -*- coding: utf-8 -*-
from lxml import etree

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    acoona_hide_devtools_2 = fields.Boolean(
        string="Hide Developer Tools",
        default=True,
        config_parameter="acoona_branding.hide_devtools",
    )

    acoona_mail_debrand = fields.Boolean(
        string="Remove Odoo branding from emails",
        default=True,
        config_parameter="acoona_branding.mail_debrand",
        help="Remove Odoo links/branding from outgoing emails.",
    )

    @api.model
    def get_views(self, views, options=None):
        """アップグレード誘導を含むコンテナを強制的に非表示にする。"""
        result = super().get_views(views, options=options)

        form_view_info = result.get("views", {}).get("form")
        if not form_view_info:
            return result

        form_view = self.env["ir.ui.view"].browse(form_view_info["id"])
        if form_view.xml_id != "base.res_config_settings_view_form":
            return result

        doc = etree.XML(form_view_info["arch"])

        for node in doc.xpath("//div[div[field[@widget='upgrade_boolean']]]"):
            node.attrib["class"] = "d-none"

        form_view_info["arch"] = etree.tostring(doc, encoding="unicode")
        return result
