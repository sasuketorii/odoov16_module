# -*- coding: utf-8 -*-
import json
from lxml import etree

from odoo import api, fields, models


class BaseDocumentLayout(models.TransientModel):
    _inherit = "base.document.layout"

    # PDFプレビュー用レイアウトウィザードからも登録番号・社印を参照できるようにする
    l10n_jp_registration_number = fields.Char(
        related="company_id.l10n_jp_registration_number",
        string="Japan Registration Number",
        readonly=False,
    )
    l10n_jp_company_seal = fields.Binary(
        related="company_id.l10n_jp_company_seal",
        string="Company Seal (JP)",
        readonly=False,
    )

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "form" and res.get("arch"):
            doc = etree.fromstring(res["arch"])
            field_nodes = doc.xpath("//field[@name='report_layout_id']")
            for field in field_nodes:
                options_raw = field.get("options")
                options_dict = {}
                if options_raw:
                    try:
                        options_dict = json.loads(options_raw)
                    except json.JSONDecodeError:
                        pass
                options_dict.setdefault("limit", 0)
                if options_dict["limit"] < 10:
                    options_dict["limit"] = 10
                field.set("options", json.dumps(options_dict))
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
