"""配置导出服务测试：导出字典字段与文件名规则。"""

from datetime import date

import pytest

from src.settings import (
    CURRENT_PROJECT_CONFIG,
    LANGUAGE_CONVENTION,
    PROJECT_NAME,
    SOURCE_DIRECTORY,
    ProjectConfig,
    build_export_filename,
    build_export_payload,
    export_project_config,
    export_project_config_json,
)

export_date = date(2026, 11, 13)


def _stamp(filename: str) -> str:
    return filename.rsplit("_", 1)[-1].removesuffix(".json")


def test_payload_contains_three_required_fields():
    payload = build_export_payload()
    assert set(payload) == {
        "project_name",
        "language_convention",
        "source_directory",
    }


def test_payload_values_match_current_project_config():
    payload = build_export_payload()
    assert payload["project_name"] == PROJECT_NAME == CURRENT_PROJECT_CONFIG.project_name
    assert payload["language_convention"] == LANGUAGE_CONVENTION
    assert payload["source_directory"] == SOURCE_DIRECTORY


def test_payload_uses_given_config():
    config = ProjectConfig(
        project_name="示例项目",
        language_convention="go / — / go test",
        source_directory="cmd",
    )
    assert build_export_payload(config) == {
        "project_name": "示例项目",
        "language_convention": "go / — / go test",
        "source_directory": "cmd",
    }


def test_filename_contains_project_name_and_export_date():
    filename = build_export_filename(export_date=export_date)
    assert filename == f"{PROJECT_NAME}_20261113.json"
    assert filename.endswith(".json")
    assert PROJECT_NAME in filename


def test_filename_defaults_to_today():
    before = date.today()
    filename = build_export_filename()
    after = date.today()
    assert filename.startswith(f"{PROJECT_NAME}_")
    assert _stamp(filename) in {f"{before:%Y%m%d}", f"{after:%Y%m%d}"}
    assert filename.endswith(".json")


def test_filename_is_safe_for_download():
    filename = build_export_filename(project_name="a/b:c", export_date=export_date)
    assert filename == "a_b_c_20261113.json"
    assert "/" not in filename and ":" not in filename


def test_export_project_config_returns_payload_and_filename():
    payload, filename = export_project_config(export_date=export_date)
    assert payload == build_export_payload()
    assert filename == f"{PROJECT_NAME}_20261113.json"


def test_export_project_config_json_is_loadable():
    import json

    text, filename = export_project_config_json(export_date=export_date)
    data = json.loads(text)
    assert data["project_name"] == PROJECT_NAME
    assert data["language_convention"] == LANGUAGE_CONVENTION
    assert data["source_directory"] == SOURCE_DIRECTORY
    assert filename.endswith(".json")
    # 中文字段值不能被转义成 \uXXXX
    assert PROJECT_NAME in text


def test_export_is_repeatable():
    assert export_project_config(export_date=export_date) == export_project_config(
        export_date=export_date
    )


@pytest.mark.parametrize("export_date_value", [date(2026, 1, 1), date(2026, 12, 31)])
def test_filename_date_component(export_date_value):
    filename = build_export_filename(export_date=export_date_value)
    assert filename == f"{PROJECT_NAME}_{export_date_value:%Y%m%d}.json"
