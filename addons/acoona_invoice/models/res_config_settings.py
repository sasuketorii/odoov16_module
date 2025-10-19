from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    """会社設定をウィザードから更新できるよう関連フィールドを定義する。"""

    _inherit = "res.config.settings"

    acoona_invoice_use_jp_layout = fields.Boolean(
        related="company_id.acoona_invoice_use_jp_layout",
        readonly=False,
    )
    acoona_invoice_department = fields.Char(
        related="company_id.acoona_invoice_department",
        readonly=False,
    )
    acoona_invoice_responsible_title = fields.Char(
        related="company_id.acoona_invoice_responsible_title",
        readonly=False,
    )
    acoona_invoice_responsible_name = fields.Char(
        related="company_id.acoona_invoice_responsible_name",
        readonly=False,
    )
    acoona_invoice_payment_note = fields.Text(
        related="company_id.acoona_invoice_payment_note",
        readonly=False,
    )
    acoona_invoice_footer_note = fields.Text(
        related="company_id.acoona_invoice_footer_note",
        readonly=False,
    )
