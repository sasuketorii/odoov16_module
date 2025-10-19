# -*- coding: utf-8 -*-
from odoo.tests.common import SavepointCase


class TestReportLayoutGuard(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.layout_model = cls.env["report.layout"].with_context(
            active_test=False
        ).sudo()
        cls.view_model = cls.env["ir.ui.view"].sudo()
        cls.standard_view = cls.env.ref("web.external_layout_standard")

    def test_write_converts_layout_to_view(self):
        """write 時に report.layout を渡しても自動的に ir.ui.view へ変換される。"""
        layout = self.layout_model.search(
            [("view_id", "=", self.standard_view.id)], limit=1
        )
        self.assertTrue(layout, "標準レイアウトの report.layout が見つかりません。")
        company = self.env.company
        company.write({"external_report_layout_id": layout.id})
        self.assertEqual(
            company.external_report_layout_id, self.standard_view,
            "外部レイアウト参照は ir.ui.view を指す必要があります。",
        )

    def test_guard_repairs_invalid_view(self):
        """既に壊れた参照があってもガードが標準に戻す。"""
        bogus_view = self.view_model.create(
            {
                "name": "Test Non QWeb View",
                "type": "tree",
                "model": "res.partner",
                "arch_db": "<tree string='Dummy'/>",
            }
        )
        company = self.env.company
        company.sudo().with_context(rlg_skip_guard=True).write(
            {"external_report_layout_id": bogus_view.id}
        )

        company._rlg_guard_external_layout_pointer()
        self.assertEqual(
            company.external_report_layout_id,
            self.standard_view,
            "ガード後は標準レイアウトへ復旧しているはずです。",
        )
