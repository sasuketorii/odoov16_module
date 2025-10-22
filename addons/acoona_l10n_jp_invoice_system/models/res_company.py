# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError
import re


class ResCompany(models.Model):
    _inherit = "res.company"

    # OCAの l10n_jp_account_report_registration_number が無い環境でも動くように、
    # 本モジュール側で登録番号フィールドを提供する（既存に同名があれば再定義されない）。
    l10n_jp_registration_number = fields.Char(
        string="Japan Registration Number",
        help="Qualified Invoice Registration No. (e.g., T1234567890123)",
    )

    # Acoona Invoice の機能を統合
    acoona_invoice_use_jp_layout = fields.Boolean(
        string="日本向け請求書レイアウトを使用",
        default=True,
        help="有効にすると Acoona の日本版請求書レイアウトを適用します。",
    )
    acoona_invoice_previous_layout_id = fields.Many2one(
        "report.layout",
        string="以前の帳票レイアウト",
        copy=False,
        ondelete="set null",
        help="日本向けレイアウト適用前に選択されていた帳票レイアウトを保持します。",
    )
    acoona_invoice_department = fields.Char(
        string="請求部署名",
        help="発行元として表示する部署名を指定します。",
    )
    acoona_invoice_responsible_title = fields.Char(
        string="担当者肩書",
        help="担当者名の前に付与する肩書（例: 営業部）。",
    )
    acoona_invoice_responsible_name = fields.Char(
        string="担当者氏名",
        help="請求書に表示する担当者名。",
    )
    acoona_invoice_payment_note = fields.Text(
        string="支払案内メッセージ",
        help="支払条件や振込に関する案内文をテーブル情報の下に表示します。",
    )
    acoona_invoice_footer_note = fields.Text(
        string="請求書備考デフォルト",
        help="請求書 PDF の備考欄に常に表示する定型文。",
    )

    # 日本向け請求書の表示カスタマイズ
    l10n_jp_invoice_attention_suffix = fields.Char(
        string="請求先敬称 (JP)",
        default="御中",
        help="請求先の名称末尾に付与する敬称（法人=御中／個人=様など）。",
    )
    l10n_jp_invoice_opening_text = fields.Char(
        string="請求書リード文 (JP)",
        default="下記の通り、ご請求申し上げます。",
        help="請求書本文冒頭に表示するリード文です。",
    )
    l10n_jp_invoice_bank_note = fields.Char(
        string="振込手数料注記 (JP)",
        default="振込手数料は貴社でご負担ください。",
        help="振込先ブロックの下部に表示する注意書きです。",
    )

    @api.constrains("l10n_jp_registration_number")
    def _check_jp_registration_number(self):
        pattern = re.compile(r"^T\d{13}$")
        for rec in self:
            if rec.l10n_jp_registration_number and not pattern.match(rec.l10n_jp_registration_number):
                raise ValidationError(
                    "Japan Registration Number must be 'T' followed by 13 digits."
                )

    @api.model
    def _ensure_japan_report_layout(self):
        view = self.env.ref("acoona_l10n_jp_invoice_system.external_layout_jp", raise_if_not_found=False)
        if not view:
            return

        layout_model = self.env["report.layout"].sudo()
        layout_model._ensure_japan_layout()

    def write(self, vals):
        if self.env.context.get("acoona_invoice_skip_layout_sync"):
            return super().write(vals)

        tracked_keys = {"acoona_invoice_use_jp_layout", "external_report_layout_id"}
        should_sync = bool(tracked_keys.intersection(vals))
        previous_layouts = {}
        previous_flags = {}
        if should_sync:
            previous_layouts = {
                company.id: company._acoona_invoice_view_to_layout(
                    company.external_report_layout_id
                ).id
                for company in self
            }
            previous_flags = {
                company.id: company.acoona_invoice_use_jp_layout for company in self
            }

        result = super().write(vals)

        if should_sync:
            self._acoona_invoice_sync_layout(previous_layouts, previous_flags)

        return result

    @api.model
    def create(self, vals_list):
        single = False
        if isinstance(vals_list, dict):
            vals_list = [vals_list]
            single = True

        records = super().create(vals_list)
        target = records.filtered("acoona_invoice_use_jp_layout")
        if target:
            previous_layouts = {
                company.id: company._acoona_invoice_view_to_layout(
                    company.external_report_layout_id
                ).id
                for company in target
            }
            previous_flags = {company.id: False for company in target}
            target._acoona_invoice_sync_layout(previous_layouts, previous_flags)

        records._l10n_jp_configure_default_taxes()

        return records[0] if single else records

    def _l10n_jp_configure_default_taxes(self):
        Tax = self.env["account.tax"].sudo()
        for company in self:
            sale_tax = Tax.search(
                [
                    ("company_id", "=", company.id),
                    ("type_tax_use", "=", "sale"),
                    ("amount", "=", 10.0),
                    ("price_include", "=", False),
                ],
                limit=1,
            )
            purchase_tax = Tax.search(
                [
                    ("company_id", "=", company.id),
                    ("type_tax_use", "=", "purchase"),
                    ("amount", "=", 10.0),
                    ("price_include", "=", False),
                ],
                limit=1,
            )

            updates = {}
            if sale_tax and company.account_sale_tax_id != sale_tax:
                updates["account_sale_tax_id"] = sale_tax.id
            if purchase_tax and company.account_purchase_tax_id != purchase_tax:
                updates["account_purchase_tax_id"] = purchase_tax.id

            if updates:
                company.with_context(acoona_invoice_skip_layout_sync=True).write(updates)

    def _acoona_invoice_sync_layout(self, previous_layouts, previous_flags):
        """会社設定のトグルに応じて PDF レイアウトを自動連携する。"""
        layout_model = self.env["report.layout"].sudo()
        layout_model._ensure_japan_layout()
        layout = self.env.ref(
            "acoona_l10n_jp_invoice_system.report_layout_japan", raise_if_not_found=False
        )
        if not layout:
            return

        self._acoona_invoice_fix_external_layout_pointer()

        for company in self:
            # 削除済みレイアウトへの参照をクリーンアップ
            if (
                company.acoona_invoice_previous_layout_id
                and not company.acoona_invoice_previous_layout_id.exists()
            ):
                company.with_context(acoona_invoice_skip_layout_sync=True).write(
                    {"acoona_invoice_previous_layout_id": False}
                )
            prev_flag = previous_flags.get(company.id)
            prev_layout_id = previous_layouts.get(company.id)
            company_ctx = company.with_context(acoona_invoice_skip_layout_sync=True)
            prev_layout_rec = layout_model.browse(prev_layout_id).exists()
            current_layout = company._acoona_invoice_view_to_layout(
                company.external_report_layout_id
            )

            if company.acoona_invoice_use_jp_layout:
                updates = {}
                if (
                    current_layout
                    and current_layout.id != layout.id
                    and not company.acoona_invoice_previous_layout_id
                ):
                    updates["acoona_invoice_previous_layout_id"] = current_layout.id
                if company.external_report_layout_id != layout.view_id:
                    updates["external_report_layout_id"] = self._acoona_invoice_layout_view_id(
                        layout
                    )
                if updates:
                    company_ctx.write(updates)
            else:
                if prev_flag and prev_flag != company.acoona_invoice_use_jp_layout:
                    updates = {}
                    if company.external_report_layout_id == layout.view_id:
                        restore_candidate = (
                            company.acoona_invoice_previous_layout_id.exists()
                        )
                        if restore_candidate:
                            restore_id = self._acoona_invoice_layout_view_id(
                                restore_candidate
                            )
                        else:
                            restore_candidate = (
                                prev_layout_rec if prev_layout_rec else layout_model.browse()
                            )
                            restore_id = self._acoona_invoice_layout_view_id(
                                restore_candidate
                            )
                        updates["external_report_layout_id"] = restore_id
                    if company.acoona_invoice_previous_layout_id:
                        updates["acoona_invoice_previous_layout_id"] = False
                    if updates:
                        company_ctx.write(updates)
                elif (
                    not company.acoona_invoice_use_jp_layout
                    and company.acoona_invoice_previous_layout_id.exists()
                ):
                    company_ctx.write({"acoona_invoice_previous_layout_id": False})

    @api.model
    def _register_hook(self):
        res = super()._register_hook()
        self._ensure_japan_report_layout()
        self._acoona_invoice_fix_external_layout_pointer()
        return res

    @staticmethod
    def _acoona_invoice_layout_view_id(layout):
        """report.layout レコードから外部レイアウトビューの ID を取得。"""
        return layout.view_id.id if layout and layout.view_id.exists() else False

    def _acoona_invoice_view_to_layout(self, view):
        """ir.ui.view から対応する report.layout を解決。"""
        layout_model = self.env["report.layout"].sudo()
        if not view:
            return layout_model.browse()
        return layout_model.search([("view_id", "=", view.id)], limit=1)

    def _acoona_invoice_fix_external_layout_pointer(self):
        """
        external_report_layout_id が report.layout の ID を直接指している古い状態を補正。
        """
        layout_model = self.env["report.layout"].sudo()
        for company in self.sudo().with_context(active_test=False):
            view = company.external_report_layout_id
            if not view:
                continue
            candidate_layout = layout_model.browse(view.id).exists()
            if candidate_layout and candidate_layout.view_id and candidate_layout.view_id != view:
                company.with_context(acoona_invoice_skip_layout_sync=True).write(
                    {
                        "external_report_layout_id": candidate_layout.view_id.id,
                    }
                )
