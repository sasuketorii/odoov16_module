# -*- coding: utf-8 -*-
"""mail.render.mixin に対するAcoonaデブランディング拡張。"""

from odoo import api, models

from .mail_branding_utils import clean_odoo_branding, is_mail_debranding_enabled


class MailRenderMixin(models.AbstractModel):
    _inherit = "mail.render.mixin"

    @api.model
    def _render_template(
        self,
        template_src,
        model,
        res_ids,
        engine="inline_template",
        add_context=None,
        options=None,
        post_process=False,
    ):
        rendered = super()._render_template(
            template_src,
            model,
            res_ids,
            engine=engine,
            add_context=add_context,
            options=options,
            post_process=post_process,
        )
        if not is_mail_debranding_enabled(self.env):
            return rendered
        return {
            res_id: clean_odoo_branding(payload)
            for res_id, payload in rendered.items()
        }

    def _render_template_postprocess(self, html, **kwargs):
        html = super()._render_template_postprocess(html, **kwargs)
        if is_mail_debranding_enabled(self.env):
            return clean_odoo_branding(html)
        return html
