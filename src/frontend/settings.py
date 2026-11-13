"""设置页 · 前端渲染。

设置页只负责展示当前项目配置与一个「导出配置」按钮，点击后请求
``GET /settings/export`` 并由浏览器下载 JSON 文件。不引入需求外的配置编辑功能。
"""

from __future__ import annotations

from html import escape

from src.settings import (
    EXPORT_BUTTON_LABEL,
    EXPORT_ENDPOINT,
    CURRENT_PROJECT_CONFIG,
    ProjectConfig,
)

SETTINGS_PAGE_TITLE = "设置"
EXPORT_BUTTON_ID = "export-config"


def render_settings_page(config: ProjectConfig | None = None) -> str:
    """渲染设置页 HTML（含「导出配置」按钮）。"""
    cfg = CURRENT_PROJECT_CONFIG if config is None else config
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{escape(SETTINGS_PAGE_TITLE)}</title>
</head>
<body>
<main class="settings">
  <h1>{escape(SETTINGS_PAGE_TITLE)}</h1>
  <section class="settings-section">
    <h2>项目配置</h2>
    <dl class="settings-project-config">
      <dt>项目名称</dt><dd id="project-name">{escape(cfg.project_name)}</dd>
      <dt>语言约定</dt><dd id="language-convention">{escape(cfg.language_convention)}</dd>
      <dt>源码目录</dt><dd id="source-directory">{escape(cfg.source_directory)}</dd>
    </dl>
    <div class="settings-actions">
      <button type="button" id="{EXPORT_BUTTON_ID}" class="btn btn-primary">{escape(EXPORT_BUTTON_LABEL)}</button>
    </div>
  </section>
</main>
<script>
(function () {{
  var button = document.getElementById("{EXPORT_BUTTON_ID}");
  if (!button) {{ return; }}
  button.addEventListener("click", function () {{
    fetch("{EXPORT_ENDPOINT}", {{ method: "GET" }})
      .then(function (response) {{
        if (!response.ok) {{ throw new Error("导出失败：" + response.status); }}
        var disposition = response.headers.get("Content-Disposition") || "";
        var match = /filename="?([^";]+)"?/.exec(disposition);
        var filename = match ? match[1] : "project_config.json";
        return response.blob().then(function (blob) {{
          var url = URL.createObjectURL(blob);
          var link = document.createElement("a");
          link.href = url;
          link.download = filename;
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
          URL.revokeObjectURL(url);
        }});
      }})
      .catch(function (error) {{
        window.alert(error && error.message ? error.message : "导出失败");
      }});
  }});
}})();
</script>
</body>
</html>
"""
