"""
acoona_invoice モジュールのインストール・アンインストール時フック
"""


def post_init_hook(cr, registry):
  """
  モジュールインストール後の初期化処理。
  日本レイアウトが有効な会社に対して、適切なレイアウトを設定する。
  """
  from odoo import api, SUPERUSER_ID

  env = api.Environment(cr, SUPERUSER_ID, {})
  companies = env["res.company"].search([])

  for company in companies:
    if company.acoona_invoice_use_jp_layout:
      # 日本レイアウトを確保
      layout_model = env["report.layout"].sudo()
      if hasattr(layout_model, "_ensure_japan_layout"):
        layout_model._ensure_japan_layout()

      # 日本レイアウトを取得
      layout = env.ref(
        "l10n_jp_invoice_system.report_layout_japan",
        raise_if_not_found=False
      )

      if layout:
        # external_report_layout_id が未設定または削除済みの場合に設定
        if (
          not company.external_report_layout_id
          or not company.external_report_layout_id.exists()
        ):
          company.with_context(
            acoona_invoice_skip_layout_sync=True
          ).write({
            "external_report_layout_id": layout.id
          })

