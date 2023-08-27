from datasette import hookimpl
from markupsafe import Markup, escape

FILE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif")
DEFAULT_MAX_WIDTH, DEFAULT_MAX_HEIGHT = (200, 200)


@hookimpl
def render_cell(value, datasette):
    if not isinstance(value, str):
        return

    if datasette and (
        plugin_config := datasette.plugin_config("datasette-render-image-tags")
    ):
        pass
    else:
        plugin_config = {}
    max_width = plugin_config.get("max_width", DEFAULT_MAX_WIDTH)
    max_height = plugin_config.get("max_height", DEFAULT_MAX_HEIGHT)
    fixed_width = plugin_config.get("fixed_width", None)

    value = value.strip()

    if (
        not value
        or " " in value
        or not (value.startswith("http://") or value.startswith("https://"))
        or all(not value.lower().endswith(ext) for ext in FILE_EXTENSIONS)
    ):
        return None
    if fixed_width is not None:
        return Markup(
            f'<img src="{escape(value)}" width="{fixed_width}" loading="lazy">'
        )
    style = f"display: block;margin: 0 auto;max-width: {max_width}px;max-height: {max_height}px;"
    return Markup(f'<img src="{escape(value)}" loading="lazy" style="{style}">')
