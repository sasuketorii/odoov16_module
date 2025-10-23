# -*- coding: utf-8 -*-
import re

_FORBIDDEN_CHARS_RE = re.compile(r"[\\/:*?\"<>|]+")
_WHITESPACE_RE = re.compile(r"[\s\u3000]+")


def _clean_segment(segment):
    """Sanitize a filename segment by removing forbidden characters and squashing whitespace."""
    if not segment:
        return ""
    value = str(segment)
    value = _WHITESPACE_RE.sub(" ", value).strip()
    if not value:
        return ""
    value = _FORBIDDEN_CHARS_RE.sub(" ", value)
    return _WHITESPACE_RE.sub(" ", value).strip()


def build_pdf_filename(document_label, partner_block, title_block):
    """Compose a JP friendly PDF filename of the form `[Doc | PartnerTitle]`."""
    doc = _clean_segment(document_label) or "書類"
    partner = _clean_segment(partner_block)
    title = _clean_segment(title_block)

    core = partner or ""
    if title:
        core = f"{core}{title}".strip()

    if core:
        candidate = f"[{doc} | {core}]"
    else:
        candidate = f"[{doc}]"

    # Strip redundant whitespace that may appear around the brackets.
    return candidate.strip()
