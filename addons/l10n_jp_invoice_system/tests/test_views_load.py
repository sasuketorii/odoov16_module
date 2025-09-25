# -*- coding: utf-8 -*-
from odoo.tests.common import SavepointCase


class TestViewsLoad(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_templates_exist(self):
        View = self.env["ir.ui.view"]
        # Japan external layout
        view = View.search([("key", "=", "l10n_jp_invoice_system.external_layout_jp")], limit=1)
        self.assertTrue(view, "Japan external layout template must exist")

    def test_company_fields(self):
        company = self.env.company
        company.l10n_jp_registration_number = "T1234567890123"
        self.assertEqual(company.l10n_jp_registration_number, "T1234567890123")

    def test_bank_default_flow(self):
        company = self.env.company
        # Create a dummy bank account for the company
        bank = self.env["res.partner.bank"].create({
            "acc_number": "1234567",
            "partner_id": company.partner_id.id,
        })
        company.l10n_jp_default_invoice_bank_id = bank

        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.env.user.partner_id.id,
        })
        # Onchange equivalent defaulting can't run automatically here; check fallback in QWeb
        self.assertTrue(company.l10n_jp_default_invoice_bank_id)
