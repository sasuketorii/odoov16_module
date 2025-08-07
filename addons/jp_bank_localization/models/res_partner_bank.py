# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re
from .kana_converter import convert_to_halfwidth_kana

class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'
    
    jp_account_type = fields.Selection([
        ('ordinary', '普通'),
        ('current', '当座'),
        ('savings', '貯蓄'),
        ('fixed', '定期'),
        ('other', 'その他')
    ], string='口座種別', default='ordinary')
    
    jp_account_holder = fields.Char(
        '口座名義人（漢字）',
        help='正式な口座名義人名を漢字で入力'
    )
    jp_account_holder_kana = fields.Char(
        '口座名義人（カナ）',
        help='振込用の口座名義人名を半角カナで入力'
    )
    jp_bank_code = fields.Char(
        '銀行コード',
        size=4,
        related='bank_id.jp_bank_code',
        readonly=True,
        store=True
    )
    jp_branch_code = fields.Char(
        '支店コード',
        size=3,
        related='bank_id.jp_branch_code',
        readonly=True,
        store=True
    )
    jp_branch_name = fields.Char(
        '支店名',
        related='bank_id.jp_branch_name',
        readonly=True,
        store=True
    )
    
    # jp_account_number を廃止し、標準の acc_number を利用する
    
    jp_yucho_symbol = fields.Char(
        'ゆうちょ記号',
        size=5,
        help='ゆうちょ銀行の5桁記号番号'
    )
    jp_yucho_number = fields.Char(
        'ゆうちょ番号',
        size=8,
        help='ゆうちょ銀行の8桁番号'
    )
    
    jp_swift_code = fields.Char(
        'SWIFTコード',
        size=11,
        help='国際送金用SWIFTコード'
    )
    
    jp_transfer_fee_burden = fields.Selection([
        ('payer', '振込手数料：振込人負担'),
        ('payee', '振込手数料：受取人負担')
    ], string='振込手数料負担', default='payer')
    
    jp_bank_book_symbol = fields.Char(
        '通帳記号',
        help='通帳に記載されている記号'
    )
    
    jp_is_salary_account = fields.Boolean(
        '給与振込口座',
        default=False
    )
    jp_is_main_account = fields.Boolean(
        '主要取引口座',
        default=False
    )
    
    @api.constrains('acc_number')
    def _check_acc_number(self):
        for record in self:
            if record.acc_number and not re.match(r'^\d{7}$', record.acc_number):
                raise ValidationError(_('口座番号は7桁の数字で入力してください。'))
    
    @api.constrains('jp_yucho_symbol')
    def _check_jp_yucho_symbol(self):
        for record in self:
            if record.jp_yucho_symbol and not re.match(r'^\d{5}$', record.jp_yucho_symbol):
                raise ValidationError(_('ゆうちょ記号は5桁の数字で入力してください。'))
    
    @api.constrains('jp_yucho_number')
    def _check_jp_yucho_number(self):
        for record in self:
            if record.jp_yucho_number and not re.match(r'^\d{8}$', record.jp_yucho_number):
                raise ValidationError(_('ゆうちょ番号は8桁の数字で入力してください。'))
    
    @api.constrains('jp_account_holder_kana')
    def _check_account_holder_kana(self):
        for record in self:
            if record.jp_account_holder_kana and not self._is_valid_kana(record.jp_account_holder_kana):
                raise ValidationError(_('口座名義人（カナ）は半角カナで入力してください。'))
    
    def _is_valid_kana(self, text):
        pattern = r'^[ｱ-ﾝﾞﾟｧ-ｫｬｭｮｯｰ\s\-\(\)0-9A-Z]+$'
        return bool(re.match(pattern, text))
    
    @api.onchange('jp_account_holder_kana')
    def _onchange_jp_account_holder_kana(self):
        if self.jp_account_holder_kana:
            self.jp_account_holder_kana = convert_to_halfwidth_kana(self.jp_account_holder_kana)
    
    @api.onchange('acc_number')
    def _onchange_acc_number(self):
        if self.acc_number:
            self.acc_number = self.acc_number.zfill(7)
    
    def name_get(self):
        result = []
        for bank in self:
            name = bank.acc_number or ''
            if bank.jp_account_holder:
                name = f"{bank.jp_account_holder} - {name}"
            if bank.bank_id and bank.bank_id.name:
                if bank.jp_branch_name:
                    name = f"{bank.bank_id.name} {bank.jp_branch_name} - {name}"
                else:
                    name = f"{bank.bank_id.name} - {name}"
            result.append((bank.id, name))
        return result
    
    @api.model
    def convert_yucho_to_regular(self, symbol, number):
        if not symbol or not number:
            return False, False, False
        
        if len(symbol) == 5 and len(number) == 8:
            branch_code = symbol[1:4]
            
            # チェックディジットはここでは未使用
            # check_digit = int(number[-1])
            account_number = str(int(number[:-1])).zfill(7)
            
            return '9900', branch_code, account_number
        
        return False, False, False
    
    @api.onchange('jp_yucho_symbol', 'jp_yucho_number')
    def _onchange_yucho_account(self):
        if self.jp_yucho_symbol and self.jp_yucho_number:
            bank_code, branch_code, account_number = self.convert_yucho_to_regular(
                self.jp_yucho_symbol, self.jp_yucho_number
            )
            if bank_code:
                self.jp_bank_code = bank_code
                self.jp_branch_code = branch_code
                self.acc_number = account_number
    
    def generate_transfer_format(self):
        self.ensure_one()
        if not all([self.jp_bank_code, self.jp_branch_code, self.acc_number]):
            raise ValidationError(_('振込フォーマットを生成するには、銀行コード、支店コード、口座番号が必要です。'))
        
        account_type_code = {
            'ordinary': '1',
            'current': '2',
            'savings': '4',
            'fixed': '7',
            'other': '9'
        }.get(self.jp_account_type, '1')
        
        format_data = {
            'bank_code': self.jp_bank_code,
            'branch_code': self.jp_branch_code,
            'account_type': account_type_code,
            'account_number': self.acc_number,
            'account_holder_kana': self.jp_account_holder_kana or '',
        }
        
        return format_data