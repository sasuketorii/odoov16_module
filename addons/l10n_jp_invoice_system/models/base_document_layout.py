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
    def default_get(self, fields_list):
        """
        ウィザードのデフォルト値を取得。
        削除済みレイアウトを参照している場合は適切なレイアウトに設定。
        """
        import logging
        _logger = logging.getLogger(__name__)

        result = super().default_get(fields_list)

        _logger.debug(
            "JP layout default_get: fields=%s company=%s layout=%s",
            fields_list,
            result.get("company_id"),
            result.get("report_layout_id"),
        )

        if "company_id" in result:
            company = self.env["res.company"].browse(result["company_id"])

            # external_report_layout_id が削除済みまたは NULL の場合
            if (
                not company.external_report_layout_id
                or not company.external_report_layout_id.exists()
            ):
                # 日本レイアウトが有効な場合
                if company.acoona_invoice_use_jp_layout:
                    layout_model = self.env["report.layout"].sudo()
                    if hasattr(layout_model, "_ensure_japan_layout"):
                        layout_model._ensure_japan_layout()

                    japan_layout = self.env.ref(
                        "l10n_jp_invoice_system.report_layout_japan",
                        raise_if_not_found=False
                    )
                    _logger.debug(
                        "JP layout default_get: company=%s japan_layout=%s fields=%s",
                        company.id,
                        japan_layout.id if japan_layout else None,
                        fields_list,
                    )
                    if japan_layout and "report_layout_id" in fields_list:
                        result["report_layout_id"] = japan_layout.id
                else:
                    # デフォルトレイアウトを取得
                    default_layout = self.env["report.layout"].search(
                        [], limit=1, order="id asc"
                    )
                    if default_layout and "report_layout_id" in fields_list:
                        result["report_layout_id"] = default_layout.id

            # 会社が既に有効なレイアウトを保持していれば、そのレコードをフォームに反映
            if (
                "report_layout_id" in fields_list
                and company.external_report_layout_id
                and company.external_report_layout_id.exists()
            ):
                company_layout = self.env["report.layout"].search(
                    [
                        ("view_id", "=", company.external_report_layout_id.id),
                    ],
                    limit=1,
                )
                if company_layout:
                    result["report_layout_id"] = company_layout.id
                    _logger.debug(
                        "JP layout default_get: company=%s final report_layout_id=%s",
                        company.id,
                        company_layout.id,
                    )

        return result

    def _compute_preview(self):
        """
        プレビュー計算の前に、削除済みレイアウトへの参照をクリーンアップ。
        エラーが発生した場合は空のプレビューを返す。
        """
        import logging
        _logger = logging.getLogger(__name__)
        
        for wizard in self:
            try:
                # ウィザードの会社を取得
                company = wizard.company_id

                # 削除済みまたは未設定のレイアウトを補正
                missing_layout = (
                    not company.external_report_layout_id
                    or not company.external_report_layout_id.exists()
                )
                if missing_layout:
                    # 適切なレイアウトを設定
                    if company.acoona_invoice_use_jp_layout:
                        layout_model = self.env["report.layout"].sudo()
                        if hasattr(layout_model, "_ensure_japan_layout"):
                            layout_model._ensure_japan_layout()

                        japan_layout = self.env.ref(
                            "l10n_jp_invoice_system.report_layout_japan",
                            raise_if_not_found=False
                        )
                        if japan_layout:
                            company.with_context(
                                acoona_invoice_skip_layout_sync=True
                            ).write({
                                "external_report_layout_id": japan_layout.view_id.id
                            })
                    else:
                        # デフォルトレイアウトを設定
                        default_layout = self.env["report.layout"].search(
                            [], limit=1, order="id asc"
                        )
                        if default_layout:
                            company.with_context(
                                acoona_invoice_skip_layout_sync=True
                            ).write({
                                "external_report_layout_id": default_layout.view_id.id
                            })

                # ウィザードのレイアウトも確認
                if (
                    wizard.report_layout_id
                    and not wizard.report_layout_id.exists()
                ):
                    # 会社のレイアウトを使用
                    if company.external_report_layout_id:
                        layout = self.env["report.layout"].search(
                            [("view_id", "=", company.external_report_layout_id.id)],
                            limit=1,
                        )
                        if layout:
                            wizard.report_layout_id = layout
                    else:
                        # デフォルトレイアウトを使用
                        default_layout = self.env["report.layout"].search(
                            [], limit=1, order="id asc"
                        )
                        if default_layout:
                            wizard.report_layout_id = default_layout

            except Exception as e:
                # エラーが発生した場合はログに記録して続行
                _logger.warning(
                    "Failed to prepare document layout for preview: %s", e
                )
                wizard.preview = ""
                continue

        try:
            return super()._compute_preview()
        except Exception as e:
            # プレビュー生成でエラーが発生した場合は空のプレビューを設定
            _logger.warning(
                "Failed to generate document layout preview: %s", e
            )
            for wizard in self:
                wizard.preview = (
                    '<div style="padding: 20px; text-align: center;">'
                    '<p>プレビューを生成できませんでした。</p>'
                    '<p>レイアウトを保存して請求書から確認してください。</p>'
                    '</div>'
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
