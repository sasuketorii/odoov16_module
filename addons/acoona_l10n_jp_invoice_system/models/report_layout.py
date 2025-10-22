# -*- coding: utf-8 -*-
import base64
import logging
from functools import lru_cache

from odoo import api, fields, models
from odoo.modules.module import get_resource_path

_logger = logging.getLogger(__name__)


class ReportLayout(models.Model):
    _inherit = "report.layout"

    key = fields.Char(compute="_compute_key", store=True)

    @api.depends("view_id")
    def _compute_key(self):
        """
        view_id の XML ID を key として返す。
        XML ID が見つからない場合は、自動的にサロゲート ID を発行し、
        それでも取得できない場合は標準レイアウトへフォールバックする。
        """
        for record in self:
            fallback_key = self._fallback_template_key()
            template_key = False
            view = record.view_id
            if view and view.exists():
                # 既存の XML ID を優先的に取得
                xmlids = view.get_external_id()
                template_key = xmlids.get(view.id)

                if not template_key:
                    # view.key は module.name 形式であればそのまま利用する
                    template_key = getattr(view, "key", False)

                if not template_key:
                    # XML ID が無い場合はサロゲートを作成して追記
                    template_key = record._ensure_view_xmlid(view)

            if not template_key and fallback_key:
                template_key = fallback_key

            if not template_key:
                _logger.warning(
                    "Report layout %s (ID: %s) lacks a usable template key. "
                    "QWeb will fallback to the base layout.",
                    record.display_name,
                    record.id,
                )

            record.key = template_key

    @staticmethod
    def _fallback_template_key():
        """XML ID が特定できない場合に使用する標準レイアウトのキーを返す。"""
        return "web.external_layout_standard"

    def _ensure_view_xmlid(self, view):
        """
        XML ID を持たないビューに対して、重複が無いようサロゲート ID を自動発行する。
        """
        IrModelData = self.env["ir.model.data"].sudo()
        imd = IrModelData.search(
            [("model", "=", "ir.ui.view"), ("res_id", "=", view.id)], limit=1
        )
        if not imd:
            module = "acoona_l10n_jp_invoice_system"
            base_name = f"auto_report_layout_view_{view.id}"
            name = base_name
            index = 1
            while IrModelData.search(
                [("module", "=", module), ("name", "=", name)], limit=1
            ):
                index += 1
                name = f"{base_name}_{index}"

            try:
                imd = IrModelData.create(
                    {
                        "module": module,
                        "name": name,
                        "model": "ir.ui.view",
                        "res_id": view.id,
                        "noupdate": False,
                    }
                )
            except Exception as error:
                _logger.warning(
                    "Failed to create surrogate XML ID for view %s (ID: %s): %s",
                    view.display_name,
                    view.id,
                    error,
                )
                return False

        return f"{imd.module}.{imd.name}" if imd else False

    def _l10n_jp_layout_vals(self, view):
        return {
            "name": "Japan",
            "sequence": 6,
            "view_id": view.id,
            "image": "/web/static/img/placeholder.png",
            "pdf": self._l10n_jp_layout_binary("pdf/preview_japan.pdf"),
        }

    def _l10n_jp_layout_xmlid(self):
        return ("acoona_l10n_jp_invoice_system", "report_layout_japan")

    @staticmethod
    @lru_cache()
    def _l10n_jp_layout_binary(relative_path):
        resource_path = get_resource_path(
            "acoona_l10n_jp_invoice_system", "static", *relative_path.split("/")
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
            "acoona_l10n_jp_invoice_system.external_layout_jp", raise_if_not_found=False
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
