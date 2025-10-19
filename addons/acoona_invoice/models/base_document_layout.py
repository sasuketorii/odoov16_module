"""
Document Layout ウィザードの拡張
"""
from odoo import api, models


class BaseDocumentLayout(models.TransientModel):
  """
  Document Layout ウィザードを拡張し、
  削除済みレイアウトへの参照によるエラーを防ぐ。
  """

  _inherit = "base.document.layout"

  @api.model
  def default_get(self, fields_list):
    """
    ウィザードのデフォルト値を取得。
    削除済みレイアウトを参照している場合は適切なレイアウトに設定。
    """
    result = super().default_get(fields_list)

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
          if japan_layout and "report_layout_id" in fields_list:
            result["report_layout_id"] = japan_layout.id
        else:
          # デフォルトレイアウトを取得
          default_layout = self.env["report.layout"].search(
            [], limit=1, order="id asc"
          )
          if default_layout and "report_layout_id" in fields_list:
            result["report_layout_id"] = default_layout.id

    return result

  def _compute_preview(self):
    """
    プレビュー計算の前に、削除済みレイアウトへの参照をクリーンアップ。
    エラーが発生した場合は空のプレビューを返す。
    """
    for wizard in self:
      try:
        # ウィザードの会社を取得
        company = wizard.company_id

        # 削除済みレイアウトへの参照をクリーンアップ
        if (
          company.external_report_layout_id
          and not company.external_report_layout_id.exists()
        ):
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
                "external_report_layout_id": japan_layout.id
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
                "external_report_layout_id": default_layout.id
              })

        # ウィザードのレイアウトも確認
        if (
          wizard.report_layout_id
          and not wizard.report_layout_id.exists()
        ):
          # 会社のレイアウトを使用
          if company.external_report_layout_id:
            wizard.report_layout_id = company.external_report_layout_id
          else:
            # デフォルトレイアウトを使用
            default_layout = self.env["report.layout"].search(
              [], limit=1, order="id asc"
            )
            if default_layout:
              wizard.report_layout_id = default_layout

      except Exception as e:
        # エラーが発生した場合はログに記録して続行
        import logging
        _logger = logging.getLogger(__name__)
        _logger.warning(
          "Failed to prepare document layout for preview: %s", e
        )
        wizard.preview = ""
        continue

    try:
      return super()._compute_preview()
    except Exception as e:
      # プレビュー生成でエラーが発生した場合は空のプレビューを設定
      import logging
      _logger = logging.getLogger(__name__)
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

