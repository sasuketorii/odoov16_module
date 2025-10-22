# -*- coding: utf-8 -*-
from odoo import models, fields


class AccountSetupBankManualConfig(models.TransientModel):
    _inherit = 'account.setup.bank.manual.config'

    # ウィザードにも日本ローカルの項目を追加
    jpBranchCode = fields.Char('支店番号', size=3)
    jpBranchName = fields.Char('支店名（カナ）')
    jpAccountType = fields.Selection([
        ('ordinary', '普通'),
        ('current', '当座'),
        ('savings', '貯蓄'),
        ('fixed', '定期'),
        ('other', 'その他'),
    ], string='口座種類', default='ordinary')
    jpAccountHolderKana = fields.Char('口座名義人（カナ）')

    # create の上書きは不要（標準に委譲し、常に会社所有で作る）

    def validate(self):
        """標準の口座作成/リンク処理の後に、作成された銀行口座へ日本用項目を書き込む。

        - 標準処理の戻り値は通常、作成/リンクされた `account.journal` を開くアクション。
        - その `res_id` から `bank_account_id` を取得して追記する。
        """
        action = super().validate()
        try:
            journal = None
            # 1) アクションの res_id から取得
            if isinstance(action, dict) and action.get('res_model') == 'account.journal' and action.get('res_id'):
                journal = self.env['account.journal'].browse(action['res_id'])
            # 2) ウィザードのフィールドから取得（リンク or 新規）
            if not journal:
                journal = self.linked_journal_id or getattr(self, 'journal_id', False)

            if journal:
                bank = journal.bank_account_id
                if bank:
                    vals = {
                        'jpBranchCode': self.jpBranchCode,
                        'jpBranchName': self.jpBranchName,
                        'jpAccountType': self.jpAccountType,
                        'jpAccountHolderKana': self.jpAccountHolderKana,
                    }
                    # 未入力は書き込まない（空で上書きしない）
                    vals = {k: v for k, v in vals.items() if v}
                    if vals:
                        bank.write(vals)
        except Exception:
            # 失敗しても標準フローは妨げない（ログに残すのみ）
            self.env['ir.logging'].create({
                'name': 'acoona_jp_bank',
                'type': 'server',
                'level': 'WARNING',
                'dbname': self._cr.dbname,
                'message': 'Failed to propagate JP fields to created bank account from setup wizard.',
                'path': __name__,
                'func': 'validate',
                'line': '0',
            })
        return action
