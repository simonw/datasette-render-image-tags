from datasette import hookimpl
from markupsafe import Markup, escape

ENDS = (".jpg", ".jpeg", ".png", ".gif", ".avif", ".webp", ".svg", ".bmp")
STARTS = (
    "data:image/jpeg",
    "data:image/png",
    "data:image/avif",
    "data:image/webp",
    "data:image/svg",
    "data:image/bmp",
)


@hookimpl
def render_cell(value):
    if not isinstance(value, str):
        return
    value = value.strip()
    if not value or " " in value:
        return
    if not (value.startswith(("http://", "https://", "data:"))):
        return
    if len(value) < 256:
        title = value
    else:
        title = "Value too long to display"

    if any(value.lower().endswith(end) for end in ENDS):
        return Markup(
            '<img title="{}" src="{}" width="200" loading="lazy">'.format(
                escape(title), escape(value)
            )
        )
    if any(value.lower().startswith(start) for start in STARTS):
        return Markup(
            '<img title="{}" src="{}" width="200" loading="lazy">'.format(
                escape(title), escape(value)
            )
        )
