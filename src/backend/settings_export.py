"""设置页 · 项目配置导出下载接口（GET /settings/export）。

不依赖第三方 Web 框架：请求处理函数返回一个轻量的响应对象，
真实服务端拿到响应后按 headers 原样回写即可让浏览器下载 JSON 文件。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from urllib.parse import quote

from src.settings import EXPORT_ENDPOINT, ProjectConfig, export_project_config_json

JSON_CONTENT_TYPE = "application/json; charset=utf-8"


@dataclass(frozen=True)
class ExportResponse:
    """导出接口响应：状态码 + 响应头 + 响应体。"""

    status_code: int
    headers: dict[str, str] = field(default_factory=dict)
    body: bytes = b""

    @property
    def content_disposition(self) -> str:
        return self.headers.get("Content-Disposition", "")

    @property
    def download_filename(self) -> str:
        disposition = self.content_disposition
        marker = 'filename="'
        start = disposition.find(marker)
        if start == -1:
            return ""
        start += len(marker)
        end = disposition.find('"', start)
        return disposition[start:end] if end != -1 else disposition[start:]

    def json(self) -> dict:
        return json.loads(self.body.decode("utf-8"))


def build_export_response(
    config: ProjectConfig | None = None,
    export_date: date | None = None,
) -> ExportResponse:
    """按当前项目配置生成下载响应（200 + JSON 附件）。"""
    body, filename = export_project_config_json(config, export_date)
    return ExportResponse(
        status_code=200,
        headers={
            "Content-Type": JSON_CONTENT_TYPE,
            # filename 给不支持 RFC 5987 的客户端，filename* 保证中文项目名不乱码
            "Content-Disposition": (
                f'attachment; filename="{filename}"; '
                f"filename*=UTF-8''{quote(filename, safe='')}"
            ),
        },
        body=body.encode("utf-8"),
    )


def handle_settings_export(
    method: str = "GET",
    path: str = EXPORT_ENDPOINT,
    config: ProjectConfig | None = None,
    export_date: date | None = None,
) -> ExportResponse:
    """路由入口：只有 GET /settings/export 会触发导出下载。"""
    if path != EXPORT_ENDPOINT:
        return ExportResponse(404, {"Content-Type": "text/plain; charset=utf-8"}, b"Not Found")
    if method.upper() != "GET":
        return ExportResponse(
            405,
            {"Content-Type": "text/plain; charset=utf-8", "Allow": "GET"},
            b"Method Not Allowed",
        )
    return build_export_response(config, export_date)
