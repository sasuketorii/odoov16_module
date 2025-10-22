# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['report.layout']._ensure_japan_layout()
    
    # Acoona Invoice の機能を統合
    # 日本レイアウトが有効な会社に対して、適切なレイアウトを設定
    companies = env["res.company"].search([])
    layout = env.ref(
        "acoona_l10n_jp_invoice_system.report_layout_japan",
        raise_if_not_found=False
    )
    
    if layout:
        for company in companies:
            if company.acoona_invoice_use_jp_layout:
                # external_report_layout_id が未設定または削除済みの場合に設定
                if (
                    not company.external_report_layout_id
                    or not company.external_report_layout_id.exists()
                ):
                    company.with_context(
                        acoona_invoice_skip_layout_sync=True
                    ).write({
                        "external_report_layout_id": layout.view_id.id
                    })

    companies._acoona_invoice_fix_external_layout_pointer()
    companies._l10n_jp_configure_default_taxes()


def post_load_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.company'].search([])._l10n_jp_configure_default_taxes()

    # 既存レイアウトの key を再計算し、欠損している XML ID を補完
    layouts = env["report.layout"].sudo().with_context(
        l10n_jp_skip_layout_autocreate=True
    ).search([])
    layouts._compute_key()


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    layout = env.ref("acoona_l10n_jp_invoice_system.report_layout_japan", raise_if_not_found=False)
    if not layout:
        return

    companies = env['res.company'].with_context(active_test=False).search(
        [("external_report_layout_id", "=", layout.view_id.id)]
    )
    if companies:
        companies.write({"external_report_layout_id": False})

    env['ir.model.data'].sudo().search([
        ("module", "=", "acoona_l10n_jp_invoice_system"),
        ("name", "=", "report_layout_japan"),
    ]).unlink()

    layout.unlink()
