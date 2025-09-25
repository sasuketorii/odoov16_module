# -*- coding: utf-8 -*-
# インストール後フック: 日本語・日本円の有効化と既定設定
from odoo import api, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    インストール後に実行されるフック
    - 日本語言語と日本円通貨を有効化
    - 既定の ir.config_parameter を設定
    - 既存会社の通貨をJPYへ更新
    - 管理者ユーザーの言語を日本語へ更新
    """
    env = api.Environment(cr, SUPERUSER_ID, {})

    try:
        # 日本語言語を有効化
        japanese_lang = env['res.lang'].search([('code', '=', 'ja_JP')], limit=1)
        if japanese_lang:
            japanese_lang.active = True
            _logger.info('Japanese language activated')
        else:
            _logger.warning('Japanese language not found')

        # 日本円通貨を有効化
        jpy_currency = env.ref('base.JPY', raise_if_not_found=False)
        if jpy_currency:
            jpy_currency.active = True
            _logger.info('JPY currency activated')
        else:
            _logger.warning('JPY currency not found')

        # デフォルト言語を日本語に設定
        env['ir.config_parameter'].sudo().set_param('web.default_lang', 'ja_JP')

        # デフォルト通貨を日本円に設定
        if jpy_currency:
            env['ir.config_parameter'].sudo().set_param('base.default_currency_id', jpy_currency.id)

            # 既存会社の通貨は「仕訳が存在しない会社のみ」安全に更新
            try:
                aml_model = env['account.move.line']
            except Exception:
                aml_model = None

            updated = 0
            skipped = 0
            for company in env['res.company'].search([]):
                can_update = True
                if aml_model is not None:
                    has_moves = bool(aml_model.sudo().search([('company_id', '=', company.id)], limit=1))
                    can_update = not has_moves
                if can_update:
                    company.write({'currency_id': jpy_currency.id})
                    updated += 1
                else:
                    skipped += 1
            _logger.info('Company currency update: updated=%s, skipped=%s (existing journal items)', updated, skipped)

        # 既存ユーザーのデフォルト言語を更新（管理者のみ）
        admin_group = env.ref('base.group_system', raise_if_not_found=False)
        if admin_group:
            admin_users = env['res.users'].search([('groups_id', 'in', [admin_group.id])])
            admin_users.write({'lang': 'ja_JP'})
            _logger.info('Updated %s admin users to Japanese language', len(admin_users))

        cr.commit()
        _logger.info('JP Default Settings post_init_hook completed successfully')

    except Exception as e:
        _logger.exception('Error in post_init_hook: %s', e)
        cr.rollback()
        raise
