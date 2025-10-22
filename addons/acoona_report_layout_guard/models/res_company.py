# -*- coding: utf-8 -*-
"""
res.company 拡張
----------------------------------
外部帳票レイアウト参照が常に ir.ui.view を指すように強制する。
"""

import logging

from odoo import api, models

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    _inherit = "res.company"

    # ------------------------------------------------------------------
    # 書き込みフック
    # ------------------------------------------------------------------
    def write(self, vals):
        """
        external_report_layout_id で report.layout の ID が渡されたら、
        対応する ir.ui.view の ID に変換してから保存する。
        """
        if vals:
            if "external_report_layout_id" in vals:
                _logger.debug(
                    "RLG prepare write input: company_ids=%s value=%s",
                    self.ids,
                    vals["external_report_layout_id"],
                )
            vals = self._rlg_prepare_external_layout_vals(vals)

        result = super().write(vals)

        if not self.env.context.get("rlg_skip_guard"):
            self._rlg_guard_external_layout_pointer()

        return result

    @api.model
    def create(self, vals_list):
        """
        作成時も同様にビュー ID へ変換し、作成後に参照を検証しておく。
        """
        single = False
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
            single = True

        prepared = [self._rlg_prepare_external_layout_vals(vals) for vals in vals_list]
        records = super().create(prepared)

        records._rlg_guard_external_layout_pointer()

        return records[0] if single else records

    # ------------------------------------------------------------------
    # 公開ユーティリティ
    # ------------------------------------------------------------------
    def _rlg_guard_external_layout_pointer(self):
        """
        report.layout の ID が紛れ込んでいる／無効なビューを指している場合は補正する。
        """
        layout_model = self.env["report.layout"].with_context(active_test=False).sudo()
        standard_view = self.env.ref(
            "web.external_layout_standard", raise_if_not_found=False
        )

        for company in self.sudo().with_context(rlg_skip_guard=True):
            view = company.external_report_layout_id
            if not view:
                continue

            # report.layout の ID をそのまま保持していないか確認
            layout = layout_model.browse(view.id).exists()
            if layout and layout.view_id and layout.view_id != view:
                _logger.debug(
                    "RLG guard: company %s had report.layout %s -> fixing to view %s",
                    company.id,
                    layout.id,
                    layout.view_id.id,
                )
                company.write({"external_report_layout_id": layout.view_id.id})
                view = layout.view_id

            # テンプレートキーが無い・QWeb でない場合は標準にフォールバック
            if not view or not view.exists() or view.type != "qweb" or not view.key:
                _logger.debug(
                    "RLG guard: company %s fallback to standard layout (view=%s exists=%s type=%s key=%s)",
                    company.id,
                    view.id if view else None,
                    view.exists() if view else None,
                    view.type if view else None,
                    view.key if view else None,
                )
                if standard_view:
                    company.write({"external_report_layout_id": standard_view.id})

    def _rlg_reset_to_standard_layout(self):
        """
        標準レイアウトへ戻す（アンインストールフックで利用）。
        """
        standard_view = self.env.ref(
            "web.external_layout_standard", raise_if_not_found=False
        )
        if not standard_view:
            return
        self.sudo().with_context(rlg_skip_guard=True).write(
            {"external_report_layout_id": standard_view.id}
        )

    # ------------------------------------------------------------------
    # 内部ヘルパー
    # ------------------------------------------------------------------
    def _rlg_prepare_external_layout_vals(self, vals):
        """
        write/create の値を事前加工し、外部レイアウトが report.layout を指さないようにする。
        """
        if "external_report_layout_id" not in vals:
            return vals

        vals = dict(vals)
        vals["external_report_layout_id"] = self._rlg_external_layout_view_id(
            vals["external_report_layout_id"]
        )
        return vals

    def _rlg_external_layout_view_id(self, value):
        """
        任意の入力（レコード／整数 ID／[id, name] 形式など）から、
        適切な ir.ui.view の ID を返す。
        """
        if not value:
            return value

        layout_model = self.env["report.layout"].with_context(active_test=False).sudo()
        view_model = self.env["ir.ui.view"].with_context(active_test=False).sudo()

        # レコードセットが渡された場合
        if isinstance(value, models.BaseModel):
            if value._name == "report.layout":
                return value.view_id.exists().id or False
            if value._name == "ir.ui.view":
                return value.id
            value = value.id

        # フォームビュー等から [id, display_name] 形式が渡される場合に備える
        if isinstance(value, (list, tuple)):
            if value and isinstance(value[0], int):
                value = value[0]
            else:
                return value

        if isinstance(value, int):
            layout = layout_model.browse(value).exists()
            if layout and layout.view_id:
                _logger.debug(
                    "RLG convert: report.layout %s -> view %s", layout.id, layout.view_id.id
                )
                return layout.view_id.id
            view = view_model.browse(value).exists()
            if view:
                _logger.debug("RLG convert: view %s remains", view.id)
                return view.id

        return value
