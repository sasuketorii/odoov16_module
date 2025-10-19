from odoo import api, fields, models


class ResCompany(models.Model):
    """日本向け請求書レイアウトに必要な会社設定を追加する。"""

    _inherit = "res.company"

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

    def write(self, vals):
        if self.env.context.get("acoona_invoice_skip_layout_sync"):
            return super().write(vals)

        tracked_keys = {"acoona_invoice_use_jp_layout", "external_report_layout_id"}
        should_sync = bool(tracked_keys.intersection(vals))
        previous_layouts = {}
        previous_flags = {}
        if should_sync:
            previous_layouts = {
                company.id: (
                    company.external_report_layout_id.exists().id
                    if company.external_report_layout_id
                    else False
                )
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
                company.id: (
                    company.external_report_layout_id.exists().id
                    if company.external_report_layout_id
                    else False
                )
                for company in target
            }
            previous_flags = {company.id: False for company in target}
            target._acoona_invoice_sync_layout(previous_layouts, previous_flags)

        return records[0] if single else records

    def _acoona_invoice_sync_layout(self, previous_layouts, previous_flags):
        """会社設定のトグルに応じて PDF レイアウトを自動連携する。"""
        layout_model = self.env["report.layout"].sudo()
        layout_model._ensure_japan_layout()
        layout = self.env.ref(
            "l10n_jp_invoice_system.report_layout_japan", raise_if_not_found=False
        )
        if not layout:
            return

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
            prev_layout_rec = (
                layout_model.browse(prev_layout_id).exists()
                if prev_layout_id
                else layout_model.browse()
            )

            if company.acoona_invoice_use_jp_layout:
                updates = {}
                if (
                    prev_layout_rec
                    and prev_layout_rec.id != layout.id
                    and not company.acoona_invoice_previous_layout_id
                ):
                    updates["acoona_invoice_previous_layout_id"] = prev_layout_rec.id
                if company.external_report_layout_id != layout:
                    updates["external_report_layout_id"] = layout.id
                if updates:
                    company_ctx.write(updates)
            else:
                if prev_flag and prev_flag != company.acoona_invoice_use_jp_layout:
                    updates = {}
                    if company.external_report_layout_id == layout:
                        restore_candidate = layout_model.browse(
                            company.acoona_invoice_previous_layout_id.id
                        ).exists()
                        if restore_candidate:
                            restore_id = restore_candidate.id
                        else:
                            restore_candidate = (
                                prev_layout_rec if prev_layout_rec else layout_model.browse()
                            )
                            restore_id = restore_candidate.id if restore_candidate else False
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
