# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

# 全角カナのパターン（記号・スペース含む）
ZENKAKU_KANA_PATTERN = r'^[ァ-ンヴァ-ヶー・（）\s]+$'

# 半角→全角カナの簡易マップ
HALF_TO_FULL_KANA = str.maketrans({
  'ｱ':'ア','ｲ':'イ','ｳ':'ウ','ｴ':'エ','ｵ':'オ','ｶ':'カ','ｷ':'キ','ｸ':'ク','ｹ':'ケ','ｺ':'コ',
  'ｻ':'サ','ｼ':'シ','ｽ':'ス','ｾ':'セ','ｿ':'ソ','ﾀ':'タ','ﾁ':'チ','ﾂ':'ツ','ﾃ':'テ','ﾄ':'ト',
  'ﾅ':'ナ','ﾆ':'ニ','ﾇ':'ヌ','ﾈ':'ネ','ﾉ':'ノ','ﾊ':'ハ','ﾋ':'ヒ','ﾌ':'フ','ﾍ':'ヘ','ﾎ':'ホ',
  'ﾏ':'マ','ﾐ':'ミ','ﾑ':'ム','ﾒ':'メ','ﾓ':'モ','ﾔ':'ヤ','ﾕ':'ユ','ﾖ':'ヨ','ﾗ':'ラ','ﾘ':'リ',
  'ﾙ':'ル','ﾚ':'レ','ﾛ':'ロ','ﾜ':'ワ','ｦ':'ヲ','ﾝ':'ン','ｧ':'ァ','ｨ':'ィ','ｩ':'ゥ','ｪ':'ェ','ｫ':'ォ',
  'ｯ':'ッ','ｬ':'ャ','ｭ':'ュ','ｮ':'ョ','ｰ':'ー','･':'・','(': '（', ')': '）', ' ':'　'
})

class ResPartnerBank(models.Model):
  _inherit = 'res.partner.bank'

  jpBranchCode = fields.Char('支店番号', size=3, required=True)
  jpBranchName = fields.Char('支店名（カナ）')
  jpAccountType = fields.Selection([
    ('ordinary', '普通'),
    ('current', '当座'),
    ('savings', '貯蓄'),
    ('fixed', '定期'),
    ('other', 'その他'),
  ], string='口座種類', required=True, default='ordinary')
  jpAccountHolderKana = fields.Char('口座名義人（カナ）', required=True, help='全角カナで入力')

  @api.constrains('jpBranchCode')
  def _check_branch_code(self):
    for rec in self:
      if not re.fullmatch(r'\d{3}', rec.jpBranchCode or ''):
        raise ValidationError(_('支店番号は3桁の数字で入力してください。'))

  @api.constrains('acc_number')
  def _check_acc_number(self):
    for rec in self:
      if not re.fullmatch(r'\d{7}', (rec.acc_number or '').zfill(7)):
        raise ValidationError(_('口座番号は7桁の数字で入力してください。'))

  @api.onchange('acc_number')
  def _onchange_acc_number(self):
    if self.acc_number:
      self.acc_number = self.acc_number.zfill(7)

  @api.onchange('jpAccountHolderKana')
  def _onchange_kana_fullwidth(self):
    if self.jpAccountHolderKana:
      self.jpAccountHolderKana = self.jpAccountHolderKana.translate(HALF_TO_FULL_KANA)

  @api.onchange('jpBranchName')
  def _onchange_branch_kana_fullwidth(self):
    if self.jpBranchName:
      self.jpBranchName = self.jpBranchName.translate(HALF_TO_FULL_KANA)
      # 銀行＋支店名（カナ）から支店番号を自動補完
      if self.bank_id:
        branch = self.env['jp.bank.branch'].search([
          ('bank_id', '=', self.bank_id.id),
          ('branch_name_kana', '=', self.jpBranchName)
        ], limit=1)
        if branch:
          self.jpBranchCode = branch.branch_code

  @api.constrains('jpAccountHolderKana')
  def _check_kana(self):
    for rec in self:
      if rec.jpAccountHolderKana and not re.fullmatch(ZENKAKU_KANA_PATTERN, rec.jpAccountHolderKana):
        raise ValidationError(_('口座名義人（カナ）は全角カナで入力してください。')) 