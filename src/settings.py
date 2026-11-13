"""设置页 · 项目配置导出服务。

导出内容包括项目名称、语言约定和源码目录；导出文件名同时包含项目名与导出日期，
形如 ``项目名_YYYYMMDD.json``。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from typing import Any, Mapping

PROJECT_NAME = "验收-团队协作遗留-1112"
LANGUAGE_CONVENTION = "python / — / pytest"
SOURCE_DIRECTORY = "src"

EXPORT_ENDPOINT = "/settings/export"
EXPORT_BUTTON_LABEL = "导出配置"

# 文件名里不允许出现的字符（路径分隔符与 Windows 保留字符）
_UNSAFE_FILENAME_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


@dataclass(frozen=True)
class ProjectConfig:
    """当前项目配置。"""

    project_name: str = PROJECT_NAME
    language_convention: str = LANGUAGE_CONVENTION
    source_directory: str = SOURCE_DIRECTORY


CURRENT_PROJECT_CONFIG = ProjectConfig()


def build_export_payload(config: ProjectConfig | None = None) -> dict[str, str]:
    """把当前项目配置组装成可序列化的导出字典。"""
    cfg = CURRENT_PROJECT_CONFIG if config is None else config
    return {
        "project_name": cfg.project_name,
        "language_convention": cfg.language_convention,
        "source_directory": cfg.source_directory,
    }


def _safe_filename_part(value: str) -> str:
    """去掉文件名非法字符，避免导出文件名带出路径分隔符。"""
    cleaned = _UNSAFE_FILENAME_CHARS.sub("_", value).strip().strip(".")
    return cleaned or "project"


def build_export_filename(
    project_name: str | None = None,
    export_date: date | None = None,
) -> str:
    """生成导出文件名：``项目名_YYYYMMDD.json``。"""
    name = CURRENT_PROJECT_CONFIG.project_name if project_name is None else project_name
    day = date.today() if export_date is None else export_date
    return f"{_safe_filename_part(name)}_{day:%Y%m%d}.json"


def export_project_config(
    config: ProjectConfig | None = None,
    export_date: date | None = None,
) -> tuple[dict[str, str], str]:
    """返回 (导出字典, 导出文件名)。"""
    cfg = CURRENT_PROJECT_CONFIG if config is None else config
    return build_export_payload(cfg), build_export_filename(cfg.project_name, export_date)


def export_project_config_json(
    config: ProjectConfig | None = None,
    export_date: date | None = None,
) -> tuple[str, str]:
    """返回 (JSON 文本, 导出文件名)，供下载接口直接使用。"""
    payload, filename = export_project_config(config, export_date)
    return json.dumps(payload, ensure_ascii=False, indent=2), filename


def serialize_config_source(source: Mapping[str, Any] | None = None) -> ProjectConfig:
    """把外部配置字典（例如设置页表单）转成 ProjectConfig。"""
    if source is None:
        return CURRENT_PROJECT_CONFIG
    return ProjectConfig(
        project_name=str(source.get("project_name", PROJECT_NAME)),
        language_convention=str(
            source.get("language_convention", LANGUAGE_CONVENTION)
        ),
        source_directory=str(source.get("source_directory", SOURCE_DIRECTORY)),
    )
