# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re
from .kana_converter import convert_to_halfwidth_kana

class JpBank(models.Model):
    _name = 'jp.bank'
    _description = '日本の銀行マスタ'
    _order = 'bank_code, branch_code'
    _rec_name = 'display_name'
    
    bank_code = fields.Char(
        '銀行コード',
        size=4,
        required=True,
        help='全銀協の4桁銀行コード'
    )
    bank_name = fields.Char(
        '銀行名',
        required=True
    )
    bank_name_kana = fields.Char(
        '銀行名（カナ）',
        required=True,
        help='半角カナで入力'
    )
    branch_code = fields.Char(
        '支店コード',
        size=3,
        required=True,
        help='3桁の支店コード'
    )
    branch_name = fields.Char(
        '支店名',
        required=True
    )
    branch_name_kana = fields.Char(
        '支店名（カナ）',
        required=True,
        help='半角カナで入力'
    )
    display_name = fields.Char(
        '表示名',
        compute='_compute_display_name',
        store=True
    )
    bank_type = fields.Selection([
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
    
    swift_code = fields.Char(
        'SWIFTコード',
        size=11,
        help='国際送金用SWIFTコード'
    )
    active = fields.Boolean(
        '有効',
        default=True
    )
    
    _sql_constraints = [
        ('unique_bank_branch', 'UNIQUE(bank_code, branch_code)', 
         '同じ銀行コード・支店コードの組み合わせが既に存在します。'),
    ]
    
    @api.depends('bank_name', 'branch_name', 'bank_code', 'branch_code')
    def _compute_display_name(self):
        for record in self:
            if record.bank_name and record.branch_name:
                record.display_name = f"{record.bank_name} {record.branch_name} ({record.bank_code}-{record.branch_code})"
            else:
                record.display_name = record.bank_name or ''
    
    @api.constrains('bank_code')
    def _check_bank_code(self):
        for record in self:
            if not re.match(r'^\d{4}$', record.bank_code or ''):
                raise ValidationError(_('銀行コードは4桁の数字で入力してください。'))
    
    @api.constrains('branch_code')
    def _check_branch_code(self):
        for record in self:
            if not re.match(r'^\d{3}$', record.branch_code or ''):
                raise ValidationError(_('支店コードは3桁の数字で入力してください。'))
    
    @api.constrains('bank_name_kana', 'branch_name_kana')
    def _check_kana(self):
        for record in self:
            if record.bank_name_kana and not self._is_valid_kana(record.bank_name_kana):
                raise ValidationError(_('銀行名（カナ）は半角カナで入力してください。'))
            if record.branch_name_kana and not self._is_valid_kana(record.branch_name_kana):
                raise ValidationError(_('支店名（カナ）は半角カナで入力してください。'))
    
    def _is_valid_kana(self, text):
        pattern = r'^[ｱ-ﾝﾞﾟｧ-ｫｬｭｮｯｰ\s\-\(\)0-9A-Z]+$'
        return bool(re.match(pattern, text))
    
    
    @api.onchange('bank_name_kana')
    def _onchange_bank_name_kana(self):
        if self.bank_name_kana:
            self.bank_name_kana = convert_to_halfwidth_kana(self.bank_name_kana)
    
    @api.onchange('branch_name_kana')
    def _onchange_branch_name_kana(self):
        if self.branch_name_kana:
            self.branch_name_kana = convert_to_halfwidth_kana(self.branch_name_kana)