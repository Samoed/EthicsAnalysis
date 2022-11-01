from datetime import datetime

import pytest
from fastapi import status


@pytest.mark.parametrize(
    "data",
    [
        {"parser_state": "new", "date": "2022-10-02T11:23:03"},
        {"date": datetime.now().isoformat()},
        {"parser_state": "new"},
        {},
    ],
)
@pytest.mark.parametrize(
    "item",
    [
        {
            "source_id": 1,
            "date": "2022-10-02T10:12:01.154Z",
            "title": "string",
            "text": "string",
            "bank_id": "1000",
            "link": "string",
            "comments_num": 0,
        },
        {
            "source_id": 1,
            "date": "2022-10-02T10:12:01.154Z",
            "title": "string",
            "text": "string",
            "bank_id": "1000",
            "link": "string",
        },
    ],
)
async def test_post_text_200(client, item, data, post_source):
    response = await client.post(
        "/text/",
        json={
            "items": [],
        }
        | data,
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {"message": "OK"}


@pytest.mark.parametrize(
    "data",
    [
        {},
        {"items": [{"source_id": 0}]},
        {"items": [{"date": "2022-10-02T10:12:01.154Z"}]},
        {"items": [{"title": "string"}]},
        {"items": [{"text": "string"}]},
        {"items": [{"bank_id": "string"}]},
        {"items": [{"link": "string"}]},
        {"items": [{"comments_num": 0}]},
        {"items": [{"source_id": 0, "date": "2022-10-02T10:12:01.154Z"}]},
        {"items": [{"source_id": 0, "title": "string"}]},
        {"items": [{"source_id": 0, "text": "string"}]},
        {"items": [{"source_id": 0, "bank_id": "string"}]},
        {"items": [{"source_id": 0, "link": "string"}]},
        {"items": [{"source_id": 0, "comments_num": 0}]},
        {"items": [{"date": "2022-10-02T10:12:01.154Z", "title": "string"}]},
        {"items": [{"date": "2022-10-02T10:12:01.154Z", "text": "string"}]},
        {"items": [{"date": "2022-10-02T10:12:01.154Z", "bank_id": "string"}]},
        {"items": [{"date": "2022-10-02T10:12:01.154Z", "link": "string"}]},
        {"items": [{"date": "2022-10-02T10:12:01.154Z", "comments_num": 0}]},
        {"items": [{"title": "string", "text": "string"}]},
        {"items": [{"title": "string", "bank_id": "string"}]},
        {"items": [{"title": "string", "link": "string"}]},
        {"items": [{"title": "string", "comments_num": 0}]},
        {"items": [{"text": "string", "bank_id": "string"}]},
        {"items": [{"text": "string", "link": "string"}]},
        {"items": [{"text": "string", "comments_num": 0}]},
        {"items": [{"bank_id": "string", "link": "string"}]},
        {"items": [{"bank_id": "string", "comments_num": 0}]},
        {"items": [{"link": "string", "comments_num": 0}]},
        {"items": [{"source_id": 0, "date": "2022-10-02T10:12:01.154Z", "title": "string"}]},
        {"items": [{"source_id": 0, "date": "2022-10-02T10:12:01.154Z", "text": "string"}]},
        {"items": [{"source_id": 0, "date": "2022-10-02T10:12:01.154Z", "bank_id": "string"}]},
        {"items": [{"source_id": 0, "date": "2022-10-02T10:12:01.154Z", "link": "string"}]},
        {"items": [{"source_id": 0, "date": "2022-10-02T10:12:01.154Z", "comments_num": 0}]},
        {"items": [{"source_id": 0, "title": "string", "text": "string"}]},
        {"items": [{"source_id": 0, "title": "string", "bank_id": "string"}]},
        {"items": [{"source_id": 0, "title": "string", "link": "string"}]},
        {"items": [{"source_id": 0, "title": "string", "comments_num": 0}]},
        {
            "items": [
                {
                    "source_id": 0,
                    "date": "2022-10-02T10:12:01.154Z",
                    "title": "string",
                    "text": "string",
                    "bank_id": "string",
                    "link": "string",
                    "comments_num": 0,
                }
            ],
            "date": "test",
        },
        {
            "items": [
                {
                    "source_id": 0,
                    "date": "2022-10-02T10:12:01.154Z",
                    "title": "string",
                    "text": "string",
                    "bank_id": "test",
                    "link": "string",
                    "comments_num": 0,
                }
            ],
            "date": "test",
        },
    ],
)
async def test_post_text_422(client, data):
    response = await client.post("/text/", json=data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text


@pytest.mark.parametrize(
    "data",
    [
        {
            "items": [
                {
                    "source_id": 2,
                    "date": "2022-10-02T10:12:01.154Z",
                    "title": "string",
                    "text": "string",
                    "bank_id": "1000",
                    "link": "string",
                    "comments_num": 0,
                }
            ]
        },
        {
            "items": [
                {
                    "source_id": 1,
                    "date": "2022-10-02T10:12:01.154Z",
                    "title": "string",
                    "text": "string",
                    "bank_id": "0",
                    "link": "string",
                }
            ],
            "date": "2022-10-02T11:23:03",
        },
    ],
)
async def test_post_text_404(client, data, post_source):
    response = await client.post("/text/", json=data)
    assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
    assert response.json() == {"message": "Source or bank not found"}


@pytest.mark.asyncio
async def test_get_text(client, post_text, post_source, post_model):
    response = await client.get("/text/sentences?sources=example.com&model_id=1")
    sentences = [
        {
            "id": 1,
            "sentence": "string",
        },
        {
            "id": 2,
            "sentence": "some text",
        },
    ]
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {"items": sentences}
    response = await client.post("/source/", json={"site": "test", "source_type": "test"})
    assert response.status_code == status.HTTP_200_OK, response.text
    response = await client.post(
        "/text/",
        json={
            "items": [
                {
                    "source_id": 2,
                    "date": "2022-10-02T10:12:01.154Z",
                    "title": "string",
                    "text": "string",
                    "bank_id": "1000",
                    "link": "string",
                    "comments_num": 0,
                }
            ]
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    response = await client.get("/text/sentences?sources=example.com&sources=test&model_id=1")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {"items": sentences}
    response = await client.get("/text/sentences?sources=example.com&sources=test&model_id=1&limit=1")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {"items": [sentences[0]]}


@pytest.mark.asyncio
async def test_update_source(client, post_source):
    date = datetime.now().isoformat()
    parser_state = "test"
    response = await client.post(
        "/text/",
        json={
            "items": [
                {
                    "source_id": 1,
                    "date": "2022-10-02T10:12:01.154Z",
                    "title": "string",
                    "text": "string",
                    "bank_id": "1000",
                    "link": "string",
                    "comments_num": 0,
                }
            ],
            "date": date,
            "parser_state": parser_state,
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    response = await client.get("/source/item/1")
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["last_update"] == date
    assert data["parser_state"] == parser_state


@pytest.mark.asyncio
async def test_update_two_source_in_request(client):
    response = await client.post(
        "/source/",
        json={"site": "example.com", "source_type": "review"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    response = await client.post(
        "/source/",
        json={"site": "test.com", "source_type": "test"},
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    date = datetime.now().isoformat()
    parser_state = "test"
    response = await client.post(
        "/text/",
        json={
            "items": [
                {
                    "source_id": 1,
                    "date": "2022-10-02T10:12:01.154Z",
                    "title": "string",
                    "text": "string",
                    "bank_id": "1000",
                    "link": "string",
                    "comments_num": 0,
                },
                {
                    "source_id": 2,
                    "date": "2022-10-02T10:12:01.154Z",
                    "title": "string",
                    "text": "string",
                    "bank_id": "1000",
                    "link": "string",
                    "comments_num": 0,
                },
            ],
            "date": date,
            "parser_state": parser_state,
        },
    )
    assert response.status_code == status.HTTP_200_OK, response.text
    response = await client.get("/source/item/1")
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["last_update"] == date
    assert data["parser_state"] == parser_state
    response = await client.get("/source/item/2")
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert data["last_update"] == date
    assert data["parser_state"] == parser_state
