# -*- coding: utf-8 -*-
from odoo import Command, fields
from odoo.tests.common import SavepointCase


class TestViewsLoad(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def test_templates_exist(self):
        View = self.env["ir.ui.view"]
        # Japan external layout
        view = View.search([("key", "=", "acoona_l10n_jp_invoice_system.external_layout_jp")], limit=1)
        self.assertTrue(view, "Japan external layout template must exist")

    def test_company_fields(self):
        company = self.env.company
        company.l10n_jp_registration_number = "T1234567890123"
        self.assertEqual(company.l10n_jp_registration_number, "T1234567890123")

    def test_bank_default_flow(self):
        company = self.env.company
        bank = self.env["res.partner.bank"].create({
            "acc_number": "1234567",
            "partner_id": company.partner_id.id,
            "allow_out_payment": True,
        })

        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.env.user.partner_id.id,
        })
        self.assertEqual(move.l10n_jp_invoice_bank_id, bank)
        bank_info = move._get_jp_bank_info()
        self.assertTrue(bank_info.get("lines"))

    def test_bank_info_formats_account_type_label(self):
        company = self.env.company
        company.l10n_jp_invoice_bank_note = "振込手数料はご負担ください。"

        res_bank = self.env["res.bank"].create({
            "name": "テスト銀行",
        })
        bank = self.env["res.partner.bank"].create({
            "acc_number": "0123456",
            "acc_type": "bank",
            "partner_id": company.partner_id.id,
            "allow_out_payment": True,
            "bank_id": res_bank.id,
            "l10n_jp_branch_name": "本店営業部",
            "l10n_jp_branch_code": "001",
            "acc_holder_name": "株式会社テスト",
            "acc_holder_name_kana": "ｶ)ﾃｽﾄ",
        })

        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.env.user.partner_id.id,
        })

        self.assertEqual(move.l10n_jp_invoice_bank_id, bank)
        bank_info = move._get_jp_bank_info()
        self.assertEqual(bank_info["lines"][0], "テスト銀行 本店営業部(支店番号: 001)")
        self.assertEqual(bank_info["lines"][1], "普通 0123456")
        self.assertEqual(bank_info["lines"][2], "ｶ)ﾃｽﾄ")
        self.assertEqual(bank_info["note"], "振込手数料はご負担ください。")

    def test_sale_bank_info_formats(self):
        company = self.env.company
        company.l10n_jp_invoice_bank_note = "振込手数料は貴社ご負担でお願いします。"

        company.partner_id.bank_ids.unlink()
        res_bank = self.env["res.bank"].create({"name": "テスト銀行"})
        bank = self.env["res.partner.bank"].create({
            "acc_number": "9876543",
            "acc_type": "general",
            "partner_id": company.partner_id.id,
            "allow_out_payment": True,
            "bank_id": res_bank.id,
            "l10n_jp_branch_name": "刈谷",
            "l10n_jp_branch_code": "411",
            "acc_holder_name": "株式会社テスト",
        })

        product = self.env["product.product"].create({
            "name": "テスト商品",
            "type": "service",
            "list_price": 1000,
        })

        order = self.env["sale.order"].create({
            "partner_id": self.env.user.partner_id.id,
            "order_line": [
                Command.create({
                    "product_id": product.id,
                    "name": "テスト商品",
                    "product_uom_qty": 1,
                    "price_unit": 1000.0,
                }),
            ],
        })

        bank_info = order._l10n_jp_bank_info()
        self.assertEqual(bank_info["lines"][0], "テスト銀行 刈谷(支店番号: 411)")
        self.assertEqual(bank_info["lines"][1], "総合 9876543")
        self.assertEqual(bank_info["note"], "振込手数料は貴社ご負担でお願いします。")

    def test_purchase_bank_info_formats(self):
        company = self.env.company
        vendor = self.env["res.partner"].create({
            "name": "仕入先A",
        })

        product = self.env["product.product"].create({
            "name": "仕入商品",
            "type": "product",
        })

        company.partner_id.bank_ids.unlink()
        res_bank = self.env["res.bank"].create({"name": "購買銀行"})
        self.env["res.partner.bank"].create({
            "acc_number": "5550001",
            "acc_type": "checking",
            "partner_id": company.partner_id.id,
            "allow_out_payment": True,
            "bank_id": res_bank.id,
            "l10n_jp_branch_name": "名古屋",
            "l10n_jp_branch_code": "123",
            "acc_holder_name": "株式会社テスト",
        })

        po = self.env["purchase.order"].create({
            "partner_id": vendor.id,
            "order_line": [
                Command.create({
                    "product_id": product.id,
                    "name": "仕入商品",
                    "product_qty": 2.0,
                    "product_uom": product.uom_po_id.id,
                    "price_unit": 5000.0,
                    "date_planned": fields.Datetime.now(),
                }),
            ],
        })

        bank_info = po._l10n_jp_company_bank_info()
        if bank_info.get("lines"):
            self.assertIn("支店番号", bank_info["lines"][0])
            self.assertTrue(bank_info["lines"][1])

    def test_tax_summary_multiple_rates(self):
        company = self.env.company
        TaxGroup = self.env["account.tax.group"]
        Tax = self.env["account.tax"]

        group_standard = TaxGroup.create({
            "name": "標準税率 10%",
            "company_id": company.id,
        })
        group_reduced = TaxGroup.create({
            "name": "軽減税率 8%",
            "company_id": company.id,
        })

        tax_standard = Tax.create({
            "name": "消費税 10%",
            "amount": 10.0,
            "amount_type": "percent",
            "type_tax_use": "sale",
            "tax_group_id": group_standard.id,
            "company_id": company.id,
        })
        tax_reduced = Tax.create({
            "name": "消費税 8%",
            "amount": 8.0,
            "amount_type": "percent",
            "type_tax_use": "sale",
            "tax_group_id": group_reduced.id,
            "company_id": company.id,
        })

        income_account = self.env["account.account"].search([
            ("company_id", "=", company.id),
            ("account_type", "=", "income"),
        ], limit=1)
        if not income_account:
            income_account = self.env["account.account"].create({
                "code": "JPTEST100",
                "name": "Test Income",
                "account_type": "income",
                "company_id": company.id,
            })

        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.env.user.partner_id.id,
            "invoice_line_ids": [
                Command.create({
                    "name": "標準課税品目",
                    "price_unit": 1000.0,
                    "quantity": 1.0,
                    "account_id": income_account.id,
                    "tax_ids": [Command.set([tax_standard.id])],
                }),
                Command.create({
                    "name": "軽減課税品目",
                    "price_unit": 2000.0,
                    "quantity": 1.0,
                    "account_id": income_account.id,
                    "tax_ids": [Command.set([tax_reduced.id])],
                }),
            ],
        })
        move._compute_amount()

        summary = move._get_jp_tax_summary()
        self.assertEqual(len(summary), 2)
        summary_by_name = {entry["name"]: entry for entry in summary}
        self.assertIn(group_standard.name, summary_by_name)
        self.assertIn(group_reduced.name, summary_by_name)
        self.assertAlmostEqual(summary_by_name[group_standard.name]["base"], 1000.0, places=2)
        self.assertAlmostEqual(summary_by_name[group_standard.name]["tax"], 100.0, places=2)
        self.assertAlmostEqual(summary_by_name[group_reduced.name]["base"], 2000.0, places=2)
        self.assertAlmostEqual(summary_by_name[group_reduced.name]["tax"], 160.0, places=2)

        standard_line, reduced_line = move.invoice_line_ids
        self.assertEqual(move._get_jp_line_tax_display(standard_line), "10%")
        self.assertEqual(move._get_jp_line_tax_display(reduced_line), "8%※")

    def test_tax_summary_price_included_tax(self):
        company = self.env.company
        TaxGroup = self.env["account.tax.group"]
        Tax = self.env["account.tax"]

        group_standard = TaxGroup.create({
            "name": "標準税率(内) 10%",
            "company_id": company.id,
        })

        tax_price_included = Tax.create({
            "name": "仮受消費税(内) 10%",
            "amount": 10.0,
            "amount_type": "percent",
            "type_tax_use": "sale",
            "price_include": True,
            "tax_group_id": group_standard.id,
            "company_id": company.id,
        })

        income_account = self.env["account.account"].search([
            ("company_id", "=", company.id),
            ("account_type", "=", "income"),
        ], limit=1)
        if not income_account:
            income_account = self.env["account.account"].create({
                "code": "JPTEST200",
                "name": "Test Income Price Include",
                "account_type": "income",
                "company_id": company.id,
            })

        move = self.env["account.move"].create({
            "move_type": "out_invoice",
            "partner_id": self.env.user.partner_id.id,
            "invoice_line_ids": [
                Command.create({
                    "name": "税込み課税品目",
                    "price_unit": 1290000.0,
                    "quantity": 1.0,
                    "account_id": income_account.id,
                    "tax_ids": [Command.set([tax_price_included.id])],
                }),
            ],
        })
        move._compute_amount()

        summary = move._get_jp_tax_summary()
        self.assertEqual(len(summary), 1)
        line = summary[0]
        self.assertEqual(line["name"], group_standard.name)
        self.assertAlmostEqual(line["base"], 1172727.0, places=2)
        self.assertAlmostEqual(line["tax"], 117273.0, places=2)

    def test_report_layout_without_xmlid_has_key(self):
        """XML ID を持たないレイアウトでも key が自動補完されることを確認。"""
        View = self.env["ir.ui.view"]
        ReportLayout = self.env["report.layout"].with_context(
            l10n_jp_skip_layout_autocreate=True
        )

        custom_view = View.create({
            "name": "test_external_layout_without_xmlid",
            "type": "qweb",
            "arch_db": """<?xml version="1.0" encoding="utf-8"?>
<template>
    <t t-name="test.external_layout_without_xmlid">
        <div>Test External Layout</div>
    </t>
</template>
""",
        })

        layout = ReportLayout.create({
            "name": "Test Layout Without XMLID",
            "sequence": 999,
            "view_id": custom_view.id,
            "image": False,
            "pdf": False,
        })

        self.assertTrue(layout.key)
        # 生成された key からテンプレートを参照できることを確認
        template_view = self.env.ref(layout.key)
        self.assertTrue(template_view.exists())

    def test_company_layout_pointer_uses_view(self):
        """external_report_layout_id が常に ir.ui.view を指すことを確認。"""
        company = self.env.company
        japan_layout = self.env.ref("acoona_l10n_jp_invoice_system.report_layout_japan")
        standard_view = self.env.ref("web.external_layout_standard")
        company.with_context(acoona_invoice_skip_layout_sync=True).write({
            "external_report_layout_id": standard_view.id,
            "acoona_invoice_previous_layout_id": False,
            "acoona_invoice_use_jp_layout": False,
        })

        company._acoona_invoice_fix_external_layout_pointer()
        self.assertEqual(company.external_report_layout_id, standard_view)

        company.write({"acoona_invoice_use_jp_layout": True})
        previous_layout = company.acoona_invoice_previous_layout_id
        self.assertEqual(company.external_report_layout_id, japan_layout.view_id)
        self.assertTrue(previous_layout)
        self.assertEqual(previous_layout.view_id, standard_view)

        company.write({"acoona_invoice_use_jp_layout": False})
        self.assertEqual(company.external_report_layout_id, standard_view)

        company.write({"acoona_invoice_use_jp_layout": True})
        self.assertEqual(company.external_report_layout_id, japan_layout.view_id)
