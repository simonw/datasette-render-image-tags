from datasette.app import Datasette
from urllib.parse import urlencode
from markupsafe import escape
import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "value,expect_img",
    (
        (1, False),
        (1.2, False),
        (None, False),
        ("dog", False),
        ("noprotocol.jpg", False),
        ("https://blah/has_url.png", True),
        ("http://blah/has_url.jpg", True),
        ("https://blah/has_url.jpeg", True),
        ("https://blah/has_url.gif", True),
        ("https://blah/has_url.webp", True),
        (" https://blah/has_url.gif ", True),
        ("https://blah/has_url.mp3", False),
    ),
)
async def test_mp3_audio(value, expect_img):
    datasette = Datasette(memory=True)
    response = await datasette.client.get(
        "/_memory?"
        + urlencode(
            {
                "sql": "select :value as value",
                "value": value,
            }
        )
    )
    assert response.status_code == 200
    html = response.text
    if expect_img:
        expected = '<img src="{}" width="200" loading="lazy">'.format(
            escape(value.strip())
        )
        assert expected in html
    else:
        assert "<img " not in html
