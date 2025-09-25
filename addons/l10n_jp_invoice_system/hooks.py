# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['report.layout']._ensure_japan_layout()


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    layout = env.ref("l10n_jp_invoice_system.report_layout_japan", raise_if_not_found=False)
    if not layout:
        return

    companies = env['res.company'].with_context(active_test=False).search(
        [("external_report_layout_id", "=", layout.id)]
    )
    if companies:
        companies.write({"external_report_layout_id": False})

    env['ir.model.data'].sudo().search([
        ("module", "=", "l10n_jp_invoice_system"),
        ("name", "=", "report_layout_japan"),
    ]).unlink()

    layout.unlink()
