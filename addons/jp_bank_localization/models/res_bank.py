# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re
from .kana_converter import convert_to_halfwidth_kana

class ResBank(models.Model):
    _inherit = 'res.bank'
    
    jp_bank_code = fields.Char(
        '銀行コード',
        size=4,
        help='全銀協の4桁銀行コード'
    )
    jp_branch_code = fields.Char(
        '支店コード',
        size=3,
        help='3桁の支店コード'
    )
    jp_branch_name = fields.Char(
        '支店名'
    )
    jp_bank_name_kana = fields.Char(
        '銀行名（カナ）',
        help='半角カナで入力'
    )
    jp_branch_name_kana = fields.Char(
        '支店名（カナ）',
        help='半角カナで入力'
    )
    jp_bank_type = fields.Selection([
        ('city', '都市銀行'),
        ('regional', '地方銀行'),
        ('trust', '信託銀行'),
        ('shinkin', '信用金庫'),
        ('credit', '信用組合'),
        ('agricultural', '農協'),
        ('labor', '労働金庫'),
        ('postal', 'ゆうちょ銀行'),
        ('online', 'ネット銀行'),
        ('other', 'その他')
    ], string='銀行種別', default='other')
    
    @api.constrains('jp_bank_code')
    def _check_jp_bank_code(self):
        for record in self:
            if record.jp_bank_code and not re.match(r'^\d{4}$', record.jp_bank_code):
                raise ValidationError(_('銀行コードは4桁の数字で入力してください。'))
    
    @api.constrains('jp_branch_code')
    def _check_jp_branch_code(self):
        for record in self:
            if record.jp_branch_code and not re.match(r'^\d{3}$', record.jp_branch_code):
                raise ValidationError(_('支店コードは3桁の数字で入力してください。'))
    
    
    @api.onchange('jp_bank_name_kana')
    def _onchange_jp_bank_name_kana(self):
        if self.jp_bank_name_kana:
            self.jp_bank_name_kana = convert_to_halfwidth_kana(self.jp_bank_name_kana)
    
    @api.onchange('jp_branch_name_kana')
    def _onchange_jp_branch_name_kana(self):
        if self.jp_branch_name_kana:
            self.jp_branch_name_kana = convert_to_halfwidth_kana(self.jp_branch_name_kana)