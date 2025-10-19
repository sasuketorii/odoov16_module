from odoo import models


class ReportLayout(models.Model):
    """削除前に参照している会社設定をクリアして整合性を保つ。"""

    _inherit = "report.layout"

    def unlink(self):
        companies = self.env["res.company"].with_context(active_test=False).search(
            [("acoona_invoice_previous_layout_id", "in", self.ids)]
        )
        if companies:
            companies.with_context(acoona_invoice_skip_layout_sync=True).write(
                {"acoona_invoice_previous_layout_id": False}
            )
        return super().unlink()
