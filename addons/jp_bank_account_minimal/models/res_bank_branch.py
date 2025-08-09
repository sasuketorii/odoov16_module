# -*- coding: utf-8 -*-
from odoo import models, fields

class JpBankBranch(models.Model):
  _name = 'jp.bank.branch'
  _description = '日本銀行支店マスタ（最小）'
  _order = 'bank_id, branch_code'
  _rec_name = 'display_name'

  bank_id = fields.Many2one('res.bank', string='銀行', required=True, index=True)
  branch_code = fields.Char('支店番号', size=3, required=True, index=True)
  branch_name = fields.Char('支店名', required=True)
  branch_name_kana = fields.Char('支店名（カナ）')
  display_name = fields.Char('表示名', compute='_compute_display', store=False)

  def _compute_display(self):
    for rec in self:
      rec.display_name = f"{rec.bank_id.name or ''} {rec.branch_name or ''} ({rec.branch_code or ''})"

  _sql_constraints = [
    ('uniq_bank_branch', 'unique(bank_id, branch_code)', '同一銀行の支店番号は一意である必要があります。'),
  ] 