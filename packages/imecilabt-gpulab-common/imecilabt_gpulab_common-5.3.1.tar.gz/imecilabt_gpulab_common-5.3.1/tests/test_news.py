from imecilabt.gpulab.model.news import News

from dataclass_dict_convert import datetime_now, dump_rfc3339, parse_rfc3339


def test_news_from_json1():
    json_in = """{
    "id": "9a6355d0-6d06-11ea-a8da-7b5b9b861935",
    "created": "2020-03-23T06:38:34Z",
    "enabled": true,
    "type": "WARNING",
    "title": "Planned Maintenance Friday Morning",
    "text": "TestText",
    "notBefore": "2020-03-24T00:00:00Z",
    "notAfter": "2020-03-30T12:00:00Z",
    "tags": [ "MAINTENANCE", "WEBSITE", "CLI" ]
 }"""
    actual = News.from_json(json_in)
    assert actual.id == "9a6355d0-6d06-11ea-a8da-7b5b9b861935"
    assert actual.created == parse_rfc3339("2020-03-23T06:38:34Z")
    assert actual.enabled is True
    assert actual.type == "WARNING"
    assert actual.title == "Planned Maintenance Friday Morning"
    assert actual.text == "TestText"
    assert actual.not_before == parse_rfc3339("2020-03-24T00:00:00Z")
    assert actual.not_after == parse_rfc3339("2020-03-30T12:00:00Z")
    assert actual.tags == ["MAINTENANCE", "WEBSITE", "CLI"]


def test_news_from_json2():
    json_in = """{
    "id": "9a6355d0-6d06-11ea-a8da-7b5b9b861935",
    "created": "2020-03-23T06:38:34Z",
    "enabled": false,
    "type": "WARNING",
    "title": "Planned Maintenance Friday Morning",
    "text": "TestText",
    "notBefore": null,
    "notAfter": null,
    "tags": [ "MAINTENANCE" ]
 }"""
    actual = News.from_json(json_in)
    assert actual.id == "9a6355d0-6d06-11ea-a8da-7b5b9b861935"
    assert actual.created == parse_rfc3339("2020-03-23T06:38:34Z")
    assert actual.enabled is False
    assert actual.type == "WARNING"
    assert actual.title == "Planned Maintenance Friday Morning"
    assert actual.text == "TestText"
    assert actual.not_before is None
    assert actual.not_after is None
    assert actual.tags == ["MAINTENANCE"]


def test_news_from_json3():
    json_in = """{
    "id": "9a6355d0-6d06-11ea-a8da-7b5b9b861935",
    "created": "2020-03-23T06:38:34Z",
    "enabled": true,
    "type": "WARNING",
    "title": "Planned Maintenance Friday Morning",
    "text": "TestText",
    "tags": [  ]
 }"""
    actual = News.from_json(json_in)
    assert actual.id == "9a6355d0-6d06-11ea-a8da-7b5b9b861935"
    assert actual.created == parse_rfc3339("2020-03-23T06:38:34Z")
    assert actual.enabled is True
    assert actual.type == "WARNING"
    assert actual.title == "Planned Maintenance Friday Morning"
    assert actual.text == "TestText"
    assert actual.not_before is None
    assert actual.not_after is None
    assert actual.tags == []


def test_news_to_json1():
    news_in = News(
        id="9a6355d0-6d06-11ea-a8da-7b5b9b861935",
        created=parse_rfc3339("2020-03-23T06:38:34Z"),
        enabled=True,
        type="WARNING",
        title="Planned Maintenance Friday Morning",
        text="TestText",
        tags=["MAINTENANCE", "WEBSITE", "CLI"],
        not_before=parse_rfc3339("2020-03-24T00:00:00Z"),
        not_after=parse_rfc3339("2020-03-30T12:00:00Z"),
    )
    actual = news_in.to_dict()
    assert actual['id'] == "9a6355d0-6d06-11ea-a8da-7b5b9b861935"
    assert actual['created'] == "2020-03-23T06:38:34Z"
    assert actual['enabled'] is True
    assert actual['type'] == "WARNING"
    assert actual['title'] == "Planned Maintenance Friday Morning"
    assert actual['text'] == "TestText"
    assert actual['notBefore'] == "2020-03-24T00:00:00Z"
    assert actual['notAfter'] == "2020-03-30T12:00:00Z"
    assert actual['tags'] == ["MAINTENANCE", "WEBSITE", "CLI"]


def test_news_to_json2():
    news_in = News(
        id="9a6355d0-6d06-11ea-a8da-7b5b9b861935",
        created=parse_rfc3339("2020-03-23T06:38:34Z"),
        enabled=False,
        type="WARNING",
        title="Planned Maintenance Friday Morning",
        text="TestText",
        tags=["MAINTENANCE"],
        not_before=None,
        not_after=None,
    )
    actual = news_in.to_dict()
    assert actual['id'] == "9a6355d0-6d06-11ea-a8da-7b5b9b861935"
    assert actual['created'] == "2020-03-23T06:38:34Z"
    assert actual['enabled'] is False
    assert actual['type'] == "WARNING"
    assert actual['title'] == "Planned Maintenance Friday Morning"
    assert actual['text'] == "TestText"
    assert actual['tags'] == ["MAINTENANCE"]
    assert 'notBefore' not in actual or actual['notBefore'] is None
    assert 'notAfter' not in actual or actual['notAfter'] is None


def test_news_to_json3():
    news_in = News(
        id="9a6355d0-6d06-11ea-a8da-7b5b9b861935",
        created=parse_rfc3339("2020-03-23T06:38:34Z"),
        enabled=True,
        type="WARNING",
        title="Planned Maintenance Friday Morning",
        text="TestText",
        tags=[],
    )
    actual = news_in.to_dict()
    assert actual['id'] == "9a6355d0-6d06-11ea-a8da-7b5b9b861935"
    assert actual['created'] == "2020-03-23T06:38:34Z"
    assert actual['enabled'] is True
    assert actual['type'] == "WARNING"
    assert actual['title'] == "Planned Maintenance Friday Morning"
    assert actual['text'] == "TestText"
    assert actual['tags'] == []
    assert 'notBefore' not in actual or actual['notBefore'] is None
    assert 'notAfter' not in actual or actual['notAfter'] is None
