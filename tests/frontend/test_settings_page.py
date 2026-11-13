"""设置页测试：「导出配置」按钮展示与下载触发脚本。"""

from src.frontend.settings import (
    EXPORT_BUTTON_ID,
    SETTINGS_PAGE_TITLE,
    render_settings_page,
)
from src.settings import (
    EXPORT_BUTTON_LABEL,
    EXPORT_ENDPOINT,
    LANGUAGE_CONVENTION,
    PROJECT_NAME,
    SOURCE_DIRECTORY,
    ProjectConfig,
)


def test_settings_page_shows_export_button():
    html = render_settings_page()
    assert "导出配置" in html
    assert EXPORT_BUTTON_LABEL == "导出配置"
    assert f'id="{EXPORT_BUTTON_ID}"' in html
    assert "<button" in html


def test_settings_page_button_requests_export_endpoint():
    html = render_settings_page()
    assert EXPORT_ENDPOINT in html
    assert "addEventListener" in html
    assert "download" in html


def test_settings_page_renders_project_config():
    html = render_settings_page()
    assert PROJECT_NAME in html
    assert LANGUAGE_CONVENTION in html
    assert SOURCE_DIRECTORY in html
    assert SETTINGS_PAGE_TITLE == "设置"


def test_settings_page_escapes_dynamic_values():
    html = render_settings_page(
        ProjectConfig(
            project_name="<script>alert(1)</script>",
            language_convention="python",
            source_directory="src",
        )
    )
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_settings_page_has_no_extra_config_editing_controls():
    html = render_settings_page()
    assert "<input" not in html
    assert "<form" not in html
    assert "type=\"submit\"" not in html
