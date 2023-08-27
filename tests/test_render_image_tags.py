from urllib.parse import urlencode

import pytest
import sqlite_utils
from datasette.app import Datasette


@pytest.fixture(scope="function")
def db_path(tmp_path_factory) -> sqlite_utils.Database:
    db_directory = tmp_path_factory.mktemp("dbs")
    db_path = db_directory / "test.db"
    return db_path


@pytest.mark.asyncio
async def test_plugin_is_installed():
    datasette = Datasette(memory=True)
    response = await datasette.client.get("/-/plugins.json")
    assert response.status_code == 200
    installed_plugins = {p["name"] for p in response.json()}
    assert "datasette-render-image-tags" in installed_plugins


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url,expect_img",
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
        (" https://blah/has_url.gif ", True),
        ("https://blah/has_url.mp3", False),
    ),
)
async def test_img_is_rendered(db_path, url, expect_img):
    datasette = Datasette(
        [db_path],
        metadata={
            "databases": {"test": {"tables": {"images": {"title": "Some images"}}}},
            "plugins": {"datasette-render-image-tags": {}},
        },
    )
    db = sqlite_utils.Database(db_path)
    db["images"].upsert(dict(id=1, url=url), pk="id")
    response = await datasette.client.get("/test/images")
    assert response.status_code == 200
    html = response.text
    if expect_img:
        style = "display: block;margin: 0 auto;max-width: 200px;max-height: 200px;"
        expected = f'<img src="{url.strip()}" loading="lazy" style="{style}">'
        assert expected in html
    else:
        assert "<img " not in html


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    (
        ("https://blah/has_url.png"),
        ("http://blah/has_url.jpg"),
        ("https://blah/has_url.jpeg"),
        ("https://blah/has_url.gif"),
        (" https://blah/has_url.gif "),
    ),
)
async def test_config_changes_size(db_path, url):
    db = sqlite_utils.Database(db_path)
    db["images"].upsert(dict(id=1, url=url), pk="id")
    datasette = Datasette(
        [db_path],
        metadata={
            "databases": {"test": {"tables": {"images": {"title": "Some images"}}}},
            "plugins": {
                "datasette-render-image-tags": dict(max_width=400, max_height=300)
            },
        },
    )

    response = await datasette.client.get("/test/images")
    assert response.status_code == 200

    html = response.text
    style = "display: block;margin: 0 auto;max-width: 400px;max-height: 300px;"
    expected = f'<img src="{url.strip()}" loading="lazy" style="{style}">'
    assert expected in html


if __name__ == "__main__":
    pytest.main([__file__])
