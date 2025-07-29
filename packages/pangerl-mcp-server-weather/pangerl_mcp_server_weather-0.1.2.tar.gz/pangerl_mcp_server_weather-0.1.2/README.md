# mcp-server-weather

基于 Model Context Protocol (MCP) 的天气查询服务，支持通过 MCP 工具获取指定城市的实时天气。适用于 AI 助手、自动化脚本等场景。

---

## 特性
- 查询任意城市的实时天气
- 支持 MCP 协议，易于集成

---

## 安装

推荐使用 pip 安装：

```bash
pip install .
```

或直接在本地开发环境运行：

```bash
python -m pangerl_mcp_server_weather.server
```

---

## 获取和风天气 API Key

本服务依赖和风天气（QWeather）的 API Key。请按照以下步骤获取：

1. 访问和风天气开发者平台：[https://dev.qweather.com/docs/api/weather/weather-now](https://dev.qweather.com/docs/api/weather/weather-now)
2. 注册并登录账号。
3. 创建项目并获取你的 API Key。
4. 在服务配置或环境变量中填写你的 API Key。

详细开发配置和 API 使用说明请参考和风天气官方文档：[和风天气开发文档](https://dev.qweather.com/docs/)。

---

## MCP 配置

在 Cursor、Claude Code 或其他支持 MCP 的客户端中，添加如下配置到 `.cursor/mcp.json` 或全局 MCP 配置文件：

### uv 本地调试

```json
{
  "mcpServers": {
    "weather": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/weather-python",
        "run",
        "main.py"
      ],
      "env": {
        "QWEATHER_API_KEY": "xxx",
        "QWEATHER_API_HOST": "https://xxx.re.qweatherapi.com"
      }
    }
  }
}
```

### uvx

```json
{
  "mcpServers": {
    "weather": {
      "disabled": false,
      "timeout": 60,
      "type": "stdio",
      "command": "uvx",
      "args": [
        "pangerl-mcp-server-weather"
      ],
      "env": {
        "QWEATHER_API_KEY": "xxx",
        "QWEATHER_API_HOST": "https://xxx.re.qweatherapi.com"
      }
    }
  }
}
```

添加后，重启或刷新 MCP 设置即可。

---

## 工具参数说明

- `get_current_weather`
  - `city` (string, 必填): 城市名称。例如："beijing"、"上海"。

---

## 开发与贡献

欢迎提交 issue 和 PR 进行功能完善与 bug 修复。

---

## 参考资料
- [和风天气开发文档](https://dev.qweather.com/docs/)
- [README 编写指南](https://github.com/Tinymrsb/READMEhowto)
- [GitHub 官方 README 说明](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes)
