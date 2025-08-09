# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re

KANA_PATTERN = r'^[ｱ-ﾝﾞﾟｧ-ｫｬｭｮｯｰ\s\-\(\)0-9A-Z]+$'

class ResPartnerBank(models.Model):
  _inherit = 'res.partner.bank'

  jpBranchCode = fields.Char('支店番号', size=3, required=True)
  jpBranchName = fields.Char('支店名')
  jpAccountType = fields.Selection([
    ('ordinary', '普通'),
    ('current', '当座'),
    ('savings', '貯蓄'),
    ('fixed', '定期'),
    ('other', 'その他'),
  ], string='口座種類', required=True, default='ordinary')
  jpAccountHolderKana = fields.Char('口座名義人（カナ）', required=True, help='半角カナで入力')

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
  def _onchange_kana(self):
    if self.jpAccountHolderKana:
      # 全角カナ→半角カナ（簡易: 濁点/半濁点は既存に倣い省略可）
      trans = str.maketrans({
        'ア':'ｱ','イ':'ｲ','ウ':'ｳ','エ':'ｴ','オ':'ｵ','カ':'ｶ','キ':'ｷ','ク':'ｸ','ケ':'ｹ','コ':'ｺ',
        'サ':'ｻ','シ':'ｼ','ス':'ｽ','セ':'ｾ','ソ':'ｿ','タ':'ﾀ','チ':'ﾁ','ツ':'ﾂ','テ':'ﾃ','ト':'ﾄ',
        'ナ':'ﾅ','ニ':'ﾆ','ヌ':'ﾇ','ネ':'ﾈ','ノ':'ﾉ','ハ':'ﾊ','ヒ':'ﾋ','フ':'ﾌ','ヘ':'ﾍ','ホ':'ﾎ',
        'マ':'ﾏ','ミ':'ﾐ','ム':'ﾑ','メ':'ﾒ','モ':'ﾓ','ヤ':'ﾔ','ユ':'ﾕ','ヨ':'ﾖ','ラ':'ﾗ','リ':'ﾘ',
        'ル':'ﾙ','レ':'ﾚ','ロ':'ﾛ','ワ':'ﾜ','ヲ':'ｦ','ン':'ﾝ','ァ':'ｧ','ィ':'ｨ','ゥ':'ｩ','ェ':'ｪ','ォ':'ｫ',
        'ッ':'ｯ','ャ':'ｬ','ュ':'ｭ','ョ':'ｮ','ー':'ｰ','・':'･','　':' '
      })
      self.jpAccountHolderKana = self.jpAccountHolderKana.translate(trans)

  @api.constrains('jpAccountHolderKana')
  def _check_kana(self):
    for rec in self:
      if rec.jpAccountHolderKana and not re.fullmatch(KANA_PATTERN, rec.jpAccountHolderKana):
        raise ValidationError(_('口座名義人（カナ）は半角カナで入力してください。')) 