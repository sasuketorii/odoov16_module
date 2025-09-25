# -*- coding: utf-8 -*-
import base64
from functools import lru_cache

from odoo import api, models
from odoo.modules.module import get_resource_path


class ReportLayout(models.Model):
    _inherit = "report.layout"

    def _l10n_jp_layout_vals(self, view):
        return {
            "name": "Japan",
            "sequence": 6,
            "view_id": view.id,
            "image": "/web/static/img/placeholder.png",
            "pdf": self._l10n_jp_layout_binary("pdf/preview_japan.pdf"),
        }

    def _l10n_jp_layout_xmlid(self):
        return ("l10n_jp_invoice_system", "report_layout_japan")

    @staticmethod
    @lru_cache()
    def _l10n_jp_layout_binary(relative_path):
        resource_path = get_resource_path(
            "l10n_jp_invoice_system", "static", *relative_path.split("/")
        )
        if not resource_path:
            return False
        with open(resource_path, "rb") as resource_file:
            return base64.b64encode(resource_file.read())

    @api.model
    def _ensure_japan_layout(self):
        if self.env.context.get("l10n_jp_skip_layout_autocreate"):
            return

        view = self.env.ref(
            "l10n_jp_invoice_system.external_layout_jp", raise_if_not_found=False
        )
        if not view:
            return

        layout = self.with_context(l10n_jp_skip_layout_autocreate=True).search(
            [("view_id", "=", view.id)], limit=1
        )
        vals = self._l10n_jp_layout_vals(view)
        if layout:
            layout.write({k: v for k, v in vals.items() if k != "view_id"})
        else:
            layout = self.with_context(l10n_jp_skip_layout_autocreate=True).create(vals)

        module, name = self._l10n_jp_layout_xmlid()
        imd = self.env["ir.model.data"].sudo().search(
            [("module", "=", module), ("name", "=", name)], limit=1
        )
        if not imd:
            self.env["ir.model.data"].sudo().create(
                {
                    "module": module,
                    "name": name,
                    "model": "report.layout",
                    "res_id": layout.id,
                    "noupdate": False,
                }
            )
        elif imd.res_id != layout.id:
            imd.write({"res_id": layout.id, "noupdate": False})

    @api.model
    def search(self, args=None, offset=0, limit=None, order=None, count=False):
        self._ensure_japan_layout()
        return super().search(args, offset=offset, limit=limit, order=order, count=count)

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        self._ensure_japan_layout()
        limit = max(limit or 0, 10)
        return super().name_search(name=name, args=args, operator=operator, limit=limit)
