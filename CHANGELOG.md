# Changelog

## [v2.0.0] - 2026-03-09

### 🚀 重大更新 - OpenClaw 主配置集成

#### 🔗 OpenClaw 配置深度集成
- **自动读取 API**: LLM 配置自动从 `~/.openclaw/openclaw.json` 读取
- **Provider 支持**: 支持 xunfei 和 nvidia 两个 provider
- **模型选择**: 可在 OMG 配置文件中指定使用的模型 ID

#### ⚙️ 配置优先级
1. 函数参数 (provider, model)
2. OMG 配置文件 (`memory/config.json`)
3. OpenClaw 主配置 (`~/.openclaw/openclaw.json`)
4. 环境变量 (备用)

#### 📝 OMG 配置文件新增项
```json
"llm": {
  "enabled": true,
  "provider": "xunfei",
  "model": "xminimaxm25",
  "timeout_seconds": 30
}
```

#### 🧪 可用模型列表
| Provider | 模型 |
|----------|------|
| xunfei | xminimaxm25, xopglm5, xopkimik25, xopqwen35397b, xop3qwen1b7 |
| nvidia | nemotron-3-nano-30b-a3b, qwen3.5-397b-a17b, minimax-m2.1, deepseek-v3.2, glm4.7, kimi-k2.5 |

### 🔄 架构优化
- 重构 `llm_integration.py`，支持多 provider 动态切换
- 新增 `get_llm_config()` 函数，统一配置获取逻辑
- 新增 `get_omg_config()` 函数，读取 OMG 本地配置

### 📦 Skill 安装
- 创建 OpenClaw Skill: `/home/administrator/openclaw/skills/openclaw-omg/`
- 文档自动同步更新
