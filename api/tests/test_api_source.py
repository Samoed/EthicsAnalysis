from datetime import datetime

import pytest


@pytest.mark.parametrize(
    "data",
    [
        {"site": "example.com", "source_type": "review"},
    ],
)
def test_post_source_200(client, data):
    response = client.post(
        "/source/",
        json=data,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1


@pytest.mark.parametrize(
    "data",
    [
        {"site": "example.com"},
        {"source_type": "example.com"},
        {"sitea": 1, "source_type": "review"},
    ],
)
def test_post_source_422(client, data):
    response = client.post(
        "/source/",
        json=data,
    )
    assert response.status_code == 422, response.text


def test_get_source_200(client, post_source):
    response = client.get("/source")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {
        "items": [{"id": 1, "site": "example.com", "source_type_id": 1, "last_update": None, "parser_state": None}]
    }


def test_get_source_item_200(client, post_source):
    response = client.get("/source/item/1")
    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {
        "id": 1,
        "site": "example.com",
        "source_type_id": 1,
        "last_update": None,
        "parser_state": None,
    }


def test_get_source_404(client):
    response = client.get("/source")
    assert response.status_code == 200, response.text
    assert response.json() == {"items": []}


def test_get_source_item_404(client):
    response = client.get("/source/item/1")
    assert response.status_code == 404, response.text


def test_get_source_type(client, post_source):
    response = client.post(
        "/source/",
        json={"site": "example2.com", "source_type": "news"},
    )
    assert response.status_code == 200, response.text
    response = client.get("/source/type")
    assert response.status_code == 200, response.text
    assert response.json() == {
        "items": [
            {"id": 1, "name": "review"},
            {"id": 2, "name": "news"},
        ]
    }


def test_post_existing_source(client):
    source = {"site": "example.com", "source_type": "review"}
    response = client.post(
        "/source/",
        json=source,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1
    response = client.post(
        "/source/",
        json=source,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1


@pytest.mark.parametrize(
    "data",
    [
        {"parser_state": "test"},
        {"last_update": datetime.now().isoformat()},
        {"parser_state": "test", "last_update": datetime.now().isoformat()},
    ],
)
def test_patch_source_200(client, post_source, data):
    response = client.patch(
        "/source/item/1",
        json=data,
    )
    assert response.status_code == 200, response.text
    response_data = response.json()
    assert response_data["id"] == 1
    assert response_data["site"] == "example.com"
    assert response_data["source_type_id"] == 1
    assert response_data["parser_state"] == data.get("parser_state", None)
    assert response_data["last_update"] == data.get("last_update", None)


def test_patch_source_404(client, post_source):
    response = client.patch(
        "/source/item/2",
        json={"parser_state": "test"},
    )
    assert response.status_code == 404, response.text


@pytest.mark.parametrize("data", [{"last_update": "test"}, {"last_update": "2021-01-01"}])
def test_patch_source_422(client, post_source, data):
    response = client.patch(
        "/source/item/1",
        json=data,
    )
    assert response.status_code == 422, response.text


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"parser_state": None, "last_update": None},
    ],
)
def test_patch_source_400(client, post_source, data):
    response = client.patch(
        "/source/item/1",
        json=data,
    )
    assert response.status_code == 400, response.text
