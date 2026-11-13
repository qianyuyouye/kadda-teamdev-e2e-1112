"""GET /settings/export 下载接口测试：状态码、响应头与 JSON 内容。"""

import json
from datetime import date

from src.backend.settings_export import (
    JSON_CONTENT_TYPE,
    build_export_response,
    handle_settings_export,
)
from src.settings import (
    EXPORT_ENDPOINT,
    LANGUAGE_CONVENTION,
    PROJECT_NAME,
    SOURCE_DIRECTORY,
)

export_date = date(2026, 11, 13)
EXPECTED_FILENAME = f"{PROJECT_NAME}_20261113.json"


def test_export_endpoint_returns_200():
    response = handle_settings_export(export_date=export_date)
    assert response.status_code == 200


def test_export_content_type_is_json():
    response = handle_settings_export(export_date=export_date)
    assert response.headers["Content-Type"] == JSON_CONTENT_TYPE
    assert response.headers["Content-Type"].startswith("application/json")


def test_export_content_disposition_is_attachment_with_filename():
    response = handle_settings_export(export_date=export_date)
    disposition = response.headers["Content-Disposition"]
    assert disposition.startswith("attachment;")
    assert 'filename="' in disposition
    assert PROJECT_NAME in disposition
    assert "20261113" in disposition
    assert response.download_filename == EXPECTED_FILENAME


def test_export_content_disposition_encodes_chinese_filename():
    response = handle_settings_export(export_date=export_date)
    assert "filename*=UTF-8''" in response.headers["Content-Disposition"]
    encoded = response.headers["Content-Disposition"].split("filename*=UTF-8''")[1]
    assert "%E9%AA%8C%E6%94%B6" in encoded  # 「验收」的 UTF-8 百分号编码
    assert "20261113" in encoded


def test_export_body_is_parseable_json_with_three_fields():
    response = handle_settings_export(export_date=export_date)
    data = response.json()
    assert set(data) == {
        "project_name",
        "language_convention",
        "source_directory",
    }
    assert data["project_name"] == PROJECT_NAME
    assert data["language_convention"] == LANGUAGE_CONVENTION
    assert data["source_directory"] == SOURCE_DIRECTORY


def test_export_body_is_utf8_json_text():
    response = build_export_response(export_date=export_date)
    text = response.body.decode("utf-8")
    assert PROJECT_NAME in text
    assert json.loads(text)["source_directory"] == SOURCE_DIRECTORY


def test_export_only_matches_settings_export_path():
    assert handle_settings_export("GET", EXPORT_ENDPOINT, export_date=export_date).status_code == 200
    assert handle_settings_export("GET", "/settings/other", export_date=export_date).status_code == 404


def test_export_rejects_non_get_method():
    response = handle_settings_export("POST", EXPORT_ENDPOINT, export_date=export_date)
    assert response.status_code == 405
    assert response.headers["Allow"] == "GET"


def test_export_is_repeatable():
    first = handle_settings_export(export_date=export_date)
    second = handle_settings_export(export_date=export_date)
    assert first.body == second.body
    assert first.headers == second.headers
    assert json.loads(first.body) == json.loads(second.body)
