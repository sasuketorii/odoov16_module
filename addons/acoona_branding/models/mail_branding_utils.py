"""メール送信時のOdooブランド除去ユーティリティ。"""

import re
from typing import Union

from lxml import etree, html
from odoo import tools


DEBRAND_PARAM_KEY = "acoona_branding.mail_debrand"
DEBRAND_TRUE_VALUES = {"True", "true", "1", True}

ODOO_LINK_PATTERN = re.compile(
    r"<a\b[^>]*href=\"https?://[^\"]*odoo\.com[^\"]*\"[^>]*>.*?</a>",
    re.I | re.S,
)
ODOO_DOMAIN_PATTERN = re.compile(r"https?://[^\s'\"]*odoo\.com[^\s'\"]*", re.I)
ODOO_UTM_PATTERN = re.compile(r"[?&](utm_(source|medium|campaign|term|content)=[^&#]*)", re.I)
POWERED_BY_PATTERN = re.compile(r"powered\s*by\s*odoo", re.I)


def is_mail_debranding_enabled(env) -> bool:
    """設定パラメータからメールのデブランディング有効/無効を判定する。"""
    param_value = env["ir.config_parameter"].sudo().get_param(
        DEBRAND_PARAM_KEY, default="True"
    )
    return str(param_value) in DEBRAND_TRUE_VALUES


def _strip_wrapper_markup(markup: str) -> str:
    """fragments_fromstringを使った際のラッパー<div>を除去する。"""
    markup = markup.strip()
    if markup.lower().startswith("<div>") and markup.lower().endswith("</div>"):
        return markup[5:-6]
    return markup


def _drop_powered_by_blocks(root: html.HtmlElement) -> bool:
    """"Powered by Odoo" を含む要素全体を削除する。"""
    removed = False
    for node in list(root.iter()):
        if not isinstance(node.tag, str):
            continue
        text_content = "".join(node.itertext()).lower()
        if "powered" in text_content and "odoo" in text_content:
            node.drop_tree()
            removed = True
    return removed


def _drop_odoo_links(root: html.HtmlElement) -> bool:
    """odoo.comドメインを指すリンクを除去する。"""
    removed = False
    for anchor in list(root.iter("a")):
        href = anchor.get("href", "").lower()
        if "odoo.com" not in href:
            continue
        parent = anchor.getparent()
        text_in_parent = "".join(parent.itertext()).lower() if parent is not None else ""
        if parent is not None and "powered" in text_in_parent and "odoo" in text_in_parent:
            parent.drop_tree()
        else:
            anchor.drop_tree()
        removed = True
    return removed


def clean_odoo_branding(html_payload: Union[str, bytes]) -> Union[str, bytes]:
    """Odooブランド要素（リンク・文言）を可能な限り除去して返す。"""
    if not html_payload:
        return html_payload

    original_is_bytes = isinstance(html_payload, (bytes, bytearray))
    html_text = tools.ustr(html_payload)
    if "odoo" not in html_text.lower():
        return html_payload

    html_text = ODOO_UTM_PATTERN.sub("", html_text)

    try:
        wrapper = html.fragment_fromstring(html_text, create_parent=True)
    except (etree.ParserError, ValueError):
        cleaned = ODOO_DOMAIN_PATTERN.sub("", ODOO_LINK_PATTERN.sub("", html_text))
        cleaned = POWERED_BY_PATTERN.sub("", cleaned)
    else:
        modified = _drop_odoo_links(wrapper)
        modified |= _drop_powered_by_blocks(wrapper)
        if modified:
            cleaned = html.tostring(wrapper, encoding="unicode", method="html")
            cleaned = _strip_wrapper_markup(cleaned)
        else:
            cleaned = html_text
        cleaned = ODOO_DOMAIN_PATTERN.sub("", cleaned)
        cleaned = POWERED_BY_PATTERN.sub("", cleaned)

    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = cleaned.replace(" ,", ",").replace(" .", ".")

    if original_is_bytes:
        return cleaned.encode("utf-8")
    return cleaned
