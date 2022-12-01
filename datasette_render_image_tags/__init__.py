from datasette import hookimpl
from markupsafe import Markup, escape

ENDS = (".jpg", ".jpeg", ".png", ".gif", ".webp")


@hookimpl
def render_cell(value):
    if not isinstance(value, str):
        return
    value = value.strip()
    if not value or " " in value:
        return
    if not (value.startswith("http://") or value.startswith("https://")):
        return
    if any(value.lower().endswith(end) for end in ENDS):
        return Markup('<img src="{}" width="200" loading="lazy">'.format(escape(value)))
