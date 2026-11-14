<div align="center">

<img src="https://raw.githubusercontent.com/konbakuyomu/smartsearch/main/assets/branding/smart-search.png" alt="Smart Search" width="104">

# Smart Search

### 让 AI 联网查资料、读原网页，回答时附上能核对的来源

**服务商由你挑，Key 由你填；每个问题走哪个渠道，由 Jev 判断。**

简体中文 | [English](README.md)

[![npm](https://img.shields.io/npm/v/@konbakuyomu/smart-search?style=flat-square&color=4A62C9&label=npm)](https://www.npmjs.com/package/@konbakuyomu/smart-search)
[![CI](https://img.shields.io/github/actions/workflow/status/konbakuyomu/smartsearch/ci.yml?branch=main&style=flat-square&label=CI)](https://github.com/konbakuyomu/smartsearch/actions/workflows/ci.yml)
[![App](https://img.shields.io/badge/App-Windows%20%7C%20macOS-728CE2?style=flat-square)](https://github.com/konbakuyomu/smartsearch/releases/latest)
[![Node.js](https://img.shields.io/badge/Node.js-18%2B-3C873A?style=flat-square)](https://nodejs.org/)
[![Skills](https://img.shields.io/badge/Skills-17%20Agents-D97757?style=flat-square)](#支持的-ai-工具)
[![License](https://img.shields.io/badge/license-MIT-2F9E4F?style=flat-square)](https://github.com/konbakuyomu/smartsearch/blob/main/LICENSE)

[下载 App](https://github.com/konbakuyomu/smartsearch/releases/latest) · [使用手册](https://github.com/konbakuyomu/smartsearch/tree/main/docs/guide) · [Jev 选路说明](https://github.com/konbakuyomu/smartsearch/blob/main/docs/jev-routing.md) · [反馈问题](https://github.com/konbakuyomu/smartsearch/issues)

[看效果](#看效果) · [快速开始](#快速开始) · [平时怎么用](#平时怎么用) · [工作原理](#工作原理) · [服务商](#能力与服务商) · [命令](#常用命令) · [常见问题](#常见问题)

<code>npm install -g @konbakuyomu/smart-search@latest</code>

</div>

<br>

<p align="center">
  <img src="https://raw.githubusercontent.com/konbakuyomu/smartsearch/main/docs/media/jev-routing.gif" alt="同一个问题：左边内置搜索还在转圈，右边 Smart Search 由 Jev 给候选渠道打分，派发最合适的一个，拿回来源" width="100%">
</p>
<p align="center"><sub>同一个问题，左边是内置搜索，右边是 Smart Search：Jev 给每个已配置的渠道打分，只派发过线的最高一个。图中数值为示例。</sub></p>

> [!IMPORTANT]
> Smart Search 不提供搜索服务本身。搜索和读网页由你选择的服务商完成，API Key 由你提供，保存在本机配置目录。测试服务商和搜索可能消耗对应服务的额度；打开 App 或检查本机环境不会发起付费搜索。

## 这是什么

Smart Search 把搜索、读网页和服务商配置放在一起，接到 Codex、Claude Code、Cursor 等 AI 工具里。它由三部分组成：

| 部分 | 作用 |
| --- | --- |
| **独立 CLI**（`smart-search`） | 真正执行搜索、读网页、在线研究；AI 通过它联网 |
| **桌面 App**（Windows / macOS） | 安装 CLI、配置服务商、更新 Skills、在 App 里搜索和查看活动 |
| **Skills** | 写进 AI 工具的使用说明，告诉 AI 什么时候、怎样调用 CLI |

App 只负责管理；关掉 App 后，AI 仍会按 Skill 里的说明调用 CLI。

适合这些场合：

- **写代码、查 API**：找到当前文档，读与问题相关的页面。
- **了解新变化**：查公告和新闻，补上模型记忆里还没有的信息。
- **核对一个说法**：找到出处，读原文，再与其他来源对照。
- **研究复杂问题**：多轮收集资料，检查缺少的证据，整理带来源的回答。

## 看效果

<table>
  <tr>
    <td width="50%" valign="top">
      <img src="https://raw.githubusercontent.com/konbakuyomu/smartsearch/main/docs/media/ask-ai.gif" alt="在 AI 工具里说「用 Smart Search 查…」，AI 先搜索，再读原网页，回答带来源">
      <p><b>在 AI 里直接问</b><br><sub>说清三件事：用 Smart Search 查、读相关页面、给出来源。AI 先搜索，再读原网页，回答里附上来源。</sub></p>
    </td>
    <td width="50%" valign="top">
      <img src="https://raw.githubusercontent.com/konbakuyomu/smartsearch/main/docs/media/app-setup.gif" alt="在 App 的服务商页面填写 Exa API Key，测试通过后保存">
      <p><b>在 App 里配置服务商</b><br><sub>选服务商、粘贴 Key，先测试（会发一次真实请求），通过后保存。</sub></p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <img src="https://raw.githubusercontent.com/konbakuyomu/smartsearch/main/docs/media/app-search.gif" alt="在 App 的搜索与研究页面搜索，结果和来源链接一起显示">
      <p><b>在 App 里搜索</b><br><sub>「搜索与研究」页选工具、填问题，结果和来源链接一起给，可以复制或导出。</sub></p>
    </td>
    <td width="50%" valign="top">
      <p><b>三支完整视频</b></p>
      <sub>功能片、配置教程和日常使用的完整视频在<a href="#完整视频">下方</a>。三支都用代码逐帧渲染，源文件在 <a href="promo/"><code>promo/</code></a>，可在本地重新生成。</sub>
      <br><br>
      <sub>动画里的 Clawd 是非官方同人形象，与 Anthropic 无关；App 界面为 Windows 版的示意重绘，文字取自源码。</sub>
    </td>
  </tr>
</table>

### 完整视频

**功能片《同一个问题》**（53 秒）：同一个问题，内置搜索和 Smart Search 并排比较：Jev 选路、搜索、读原网页，最后给出带来源的回答。

https://github.com/user-attachments/assets/8909f8b9-394b-4617-b6bb-3c8b6904efc6

**配置教程**（69 秒）：跟着 Windows App 逐页配置：安装 CLI、填写并测试 API Key、打开 Jev 选路、更新 Skills。

https://github.com/user-attachments/assets/d2b17aea-1abe-4658-808a-1f212649e5e1

**日常使用**（62 秒）：在 AI 里直接问、在 App 里搜索和研究、查看活动、常用命令，关掉 App 也能继续用。

https://github.com/user-attachments/assets/915cb409-e012-4aa4-8910-3d213f732386

## 快速开始

### 用 App（推荐）

1. **安装 App，装好 CLI。** 在[发行页](https://github.com/konbakuyomu/smartsearch/releases/latest)下载适合系统的安装包。打开后，「概览」第一步会查找本机的 npm（也可以手动指定路径），点「安装 CLI」即可安装并连接独立 CLI。Windows 上有 WSL 发行版时，按钮按环境分开：「安装到 Windows」「安装到 WSL <发行版>」（WSL 里需要 Node.js 18 或更新版本）。
2. **配置服务商。** 打开「服务商」，为主搜索、文档检索、网页抓取各选一个服务商，填 API Key，点「测试」确认可用后「保存更改」。页面上有每家「申请 Key」的入口。最少配一个检索渠道就能用；三类都配上，选路时可选的渠道更多。
3. **打开 Jev 选路（可选）。** 在「服务商 → 意图路由」填 TypeSafe API Key。路由模式默认是「JEV 语义路由」；不填 Key 时会按本地规则选路。
4. **接入 AI 工具。** 打开「更新 Skills」，勾选你用的 Agent（默认是 Codex、Claude Code、Cursor），点「更新所选 Skills」。内容不同的文件会先备份，额外文件保留。更新后重新打开 Agent 会话，就可以开始问了。

逐页说明见 [App 配置与使用](https://github.com/konbakuyomu/smartsearch/blob/main/docs/guide/zh-CN/app.md)。

### 只用终端

```sh
npm install -g @konbakuyomu/smart-search@latest
smart-search setup          # 终端向导；也可以用 smart-search ui 打开本地配置页
smart-search doctor --format json
```

新版 npm CLI 只需要 Node.js 18+；平台包自带 Python 运行时，不使用你安装的 Python。用 uv 从源码安装或固定 Python 版本，见 [CLI 安装](https://github.com/konbakuyomu/smartsearch/blob/main/docs/guide/zh-CN/cli.md#cli-安装)。

## 平时怎么用

**在 AI 里**：直接告诉它要查什么，例如：

> 用 Smart Search 查 React 当前文档里 useEffect 的清理规则，读相关页面，并给出来源。

> 用 Smart Search 核对这篇文章里的说法：https://example.com/article

```powershell
smart-search fetch "https://example.com/source" --format markdown --output evidence.md
```

5. 生成 Deep Research 计划：

```powershell
smart-search deep "深度搜索一下最近的比特币行情" --budget standard --format json
```

6. 让 CLI 直接执行 live Deep Research：

```powershell
smart-search research "深度搜索一下最近的比特币行情" --budget deep --format markdown
```

7. 把 skill 安装给 AI 工具：

```powershell
smart-search setup --non-interactive --install-skills codex,claude,cursor,hermes
```

Skill 安装会把内置 `smart-search-cli` 写入用户级工具目录，例如 `~/.codex/skills`、
`~/.claude/skills`、`~/.cursor/skills`、`~/.hermes/skills`。它不会初始化 Trellis、hooks、
agents 或 commands。`--skills-root PATH` 只适合便携安装或测试时高级覆盖根目录。

8. 升级 CLI 后，同步已经安装到全局 AI 工具里的 skill：

```powershell
smart-search skills status --targets codex --format json
smart-search skills update --targets codex --format json
```

`setup --install-skills` 仍然保留给第一次配置使用。平时升级包以后，优先用 `skills status` 和
`skills update`；它们只检查或覆盖 `smart-search-cli` 托管文件，不会改 provider key，也不会创建
Trellis、hooks、agents 或 commands。

## 当前架构

| 能力 | 主要命令 | Provider | 负责什么 |
| --- | --- | --- | --- |
| `main_search` | `search` | xAI Responses、OpenAI-compatible Chat Completions | 综合回答、快速搜索、初步总结 |
| `docs_search` | `context7-library`、`context7-docs`、`exa-search` | Context7、Exa | 官方文档、SDK、API、框架/库文档 |
| `web_search` | `zhipu-search`、`doubao-search`、`zhipu-mcp-search`、`search` 内部意图补强 | 智谱 Web Search API、豆包搜索、智谱 Coding Plan MCP、Tavily、Firecrawl | 中文、国内、时效、域名过滤、补充来源 |
| `web_fetch` | `fetch`、`zhipu-mcp-reader` | Tavily、Jina Reader、智谱 Coding Plan MCP Reader、Firecrawl | 已知 URL 正文抓取、证据提取 |
| `vertical_search` | `anysearch-domains`、`anysearch-search`、`anysearch-extract`、`anysearch-batch`、`sciverse-catalog`、`sciverse-search`、`sciverse-semantic`、`sciverse-read`、`sciverse-relations` | AnySearch 和 Sciverse（实验） | 显式结构化垂直域；Sciverse 覆盖学术文献检索、语义搜索、正文片段和引用关系 |
| `site_map` | `map` | Tavily | 文档站、产品站、目录型站点结构 |
| `deep_planner` | `deep` / `dr` | 本地 planner | 离线生成 Deep Research 计划，不默认联网 |
| `research_executor` | `research` / `rs` | 按 capability 注册的 provider | live 深度研究执行：规划、发现、抓取/读取、gap check、仅基于证据综合 |

同能力兜底关系：

| 能力 | 兜底链 |
| --- | --- |
| `main_search` | xAI Responses -> OpenAI-compatible |
| `docs_search` | Context7 只在库主体命中候选 title/id 时使用；低置信度或空 Context7 命中后由 Exa 同能力兜底，并处理官方域名、论文、产品页、可信站点发现 |
| `web_search` | 豆包搜索 -> 智谱 Web Search API -> 智谱 Coding Plan MCP `web_search_prime` -> Tavily -> Firecrawl |
| `web_fetch` | Tavily -> 带 `JINA_API_KEY` 的 Jina Reader -> 智谱 Coding Plan MCP `webReader` -> Firecrawl |

**在 App 里**：打开「搜索与研究」，选工具（搜索、读取网页、在线研究等），填问题或网页地址，结果和「来源链接」显示在右侧，可以复制或导出。「活动」页能看到每个任务的状态、阶段和用到的服务商，AI 在终端里发起的任务也会记在这里。

**切换语言**：App 默认跟随系统，可在「设置与关于 → 界面语言」选择中文或 English；CLI 单独保存语言偏好，也能用 `--lang zh` / `--lang en` 临时切换。这些设置只改变界面和提示，不翻译来源网页。

## 工作原理

默认的意图路由是 **Jev 语义路由**（`SMART_SEARCH_INTENT_ROUTER=jev`），判断由 TypeSafe 的 Jev 模型完成：

| 字段 | 作用 |
| --- | --- |
| `routing_decision` | 为什么触发了某些补强路径 |
| `provider_attempts` | 每个 provider 的尝试结果 |
| `providers_used` | 最终用到哪些 provider |
| `fallback_used` | 是否触发同能力兜底 |
| `primary_sources` | 主搜索回答里带出的来源 |
| `extra_sources` | Tavily / Firecrawl 等额外发现的候选来源 |
| `source_warning` | 来源和回答之间可能存在的证据边界提醒 |

`routing_decision` 会保留旧字段：`docs_intent`、`zh_current_intent`、`web_current_intent`、`fetch_intent`、`supplemental_paths`；同时新增统一路由字段：`intent_router_mode`、`required_capabilities`、`intent_signals`、`confidence`、`router_engines_used`、`degraded_reason`。

`extra_sources` 只是候选来源，不等于自动事实校验。新闻、政策、财经、医疗、严肃评测、工具选型等高风险问题，建议先发现来源，再 `fetch` 关键网页正文，最后只基于抓到的正文写结论。

搜索引擎选择速记：先用 `search` 做宽泛探索和综合；想让 CLI 执行完整证据流时用 `research`；中文、国内、政策、公告、当前新闻优先补 `doubao-search` 或 `zhipu-search`；只有明确要用 Coding Plan 额度时才走 `zhipu-mcp-*`；库/API/框架文档优先用 Context7；官方域名、论文、产品页、可信站点和低噪声发现再用 Exa；Tavily/Firecrawl 通过 `search --extra-sources` 做横向候选，通过 `fetch` 做正文证据；Jina 用于已知 URL 正文抓取；AnySearch 只在明确要实验性垂直搜索时使用；Sciverse 只在明确要学术 catalog/search/semantic/read/relations 时使用。

## Deep Research 深度搜索

普通问题用：

```powershell
smart-search search "React useEffect cleanup 文档" --format json
```

- **程序列候选，Jev 只做选择。** 候选包括服务商、操作、能力和实际的查询词或网址，以及你的偏好顺序；不包含任何渠道密钥。Jev 不生成任意查询，也不发起工具调用。
- **search 只选一次路。** 选一个合适的渠道，返回结果与来源；不做充分性评估、补搜、过滤或汇总，结果里的 `evidence_assessment.status` 是 `not_evaluated`。检索成功不等于事实已经核验。
- **research 按证据缺口继续。** 每轮由 Jev 挑互补的动作并发执行，读取发现的网页，再从直接答案、细节、时效、权威性、交叉验证几方面判断还缺什么。只有实际读过的正文会进入引用。
- **没有 Jev 也能用。** 没填 TypeSafe Key 或得不到有效判断时，默认（`--fallback auto`）按本地能力规则选路并标记降级；`--fallback off` 则直接报错。显式的 `local` 模式从不调用 Jev。
- **预算有上限。** 在线研究的 quick / standard / deep 上限分别是 2 / 3 / 10 轮、每轮 1 / 2 / 10 个渠道，同时受 Jev 设置约束（默认最多 3 轮、每轮 3 个渠道）；证据够了会提前停止。

阈值是初始策略，不保证判断一定正确。完整说明、配置项和输出字段见 [Jev 多渠道路由](https://github.com/konbakuyomu/smartsearch/blob/main/docs/jev-routing.md)。

## 能力与服务商

每类能力任选一家即可，Key 填在 App 的「服务商」页或用 `smart-search config set` 写入。

| 能力 | 可选服务商 | 做什么 |
| --- | --- | --- |
| 主搜索 | xAI、OpenAI 兼容接口 | 由模型联网搜索并回答，附引用 |
| 文档检索 | Context7、Exa | 查软件库、API 文档和官方页面 |
| 网页搜索 | 智谱、智谱 Coding Plan、Tavily、TinyFish、DeepSeek、Firecrawl、元宝搜索 | 发现网页和摘录 |
| 网页抓取 | Jina、Firecrawl、智谱网页阅读、Tavily、TinyFish、DeepSeek | 把已知网址读成正文 |
| 垂直检索（实验性） | AnySearch、SciVerse | 特定领域与学术检索；SciVerse 只在明确指定时调用 |
| 意图路由（可选） | Jev（TypeSafe） | 给候选渠道打分并选路 |

## 支持的 AI 工具

```text
search, exa-search, exa-similar, zhipu-search, doubao-search, context7-library, context7-docs, fetch, map
```

`doctor` 是 preflight 配置预检，不是 research step。`smart-search deep` 这一步本身是离线 planner；后续执行计划里的 `steps[].command` 时才会联网。

换句话说，`doctor` 只是配置预检；它帮助 AI 判断当前 provider 是否可用，但不算 Deep Research 的取证步骤。

如果你希望 CLI 直接执行完整 live Deep Research，用：

```powershell
smart-search research "OpenAI Responses API web_search 和 Chat Completions 联网搜索怎么选" --budget deep --fallback auto --format json
smart-search rs "https://example.com/source" --fallback off --format markdown
```

`research` 会执行 plan -> discover -> fetch/read -> gap check -> evidence-only synthesis。默认 `--fallback auto`，会在同一 capability 内兜底；`--fallback off` 只尝试每个 capability 选中的第一个 provider，适合手动调试某个 provider。

`research` JSON 会包含 `final_answer`、`citations`、`evidence_items`、`gap_check`、`provider_attempts`、`fallback_used`、`degraded`、`route_policy_version` 和 `evidence_dir`。发现阶段的 snippet 只是候选，不会直接变成 citation；只有 fetch/read 到正文的来源才会被引用。兜底仍然补不齐证据时，`research` 会降级输出 gap，不会编造结论。

`research` 的路由是 capability-first 加 provider 优势：

- Context7 优先处理库/API/框架文档，但自动选择必须让查询主体词命中候选的 title 或 id。description、trust、benchmark 只用于同类候选的次级排序；没有合格候选时 Context7 记为空，再由同能力 Exa 兜底。
- 智谱 Web Search API 优先处理中文、国内、时效、政策、公告搜索。
- 智谱 Coding Plan MCP 仍是单独额度路线，通过 `web_search_prime` 和 `webReader` 加入对应 capability。
- Jina 优先用于已知公开 URL、PDF、arXiv 正文抽取；ReaderLM-v2 仍要求 `JINA_API_KEY`。
- Firecrawl 优先用于 JS-heavy、动态页面、浏览器式抽取、OCR/PDF 或强兜底抓取。
- AnySearch 只在垂直意图清楚时加入，例如 CVE、金融、法律、学术、代码库/仓库搜索。
- Sciverse 第一版是 explicit-only，不参与 `research` provider 兜底；学术引用关系请直接使用 `sciverse-*` 命令。

高级路由覆盖项是 `SMART_SEARCH_RESEARCH_PREFERRED_PROVIDERS` 和 `SMART_SEARCH_RESEARCH_DISABLED_PROVIDERS`。它们只能在 provider 已支持的 capability 内调整顺序或禁用，不能把 provider 移到另一个 capability。

可以用这些标准问题测试是否进入深搜模式：

```powershell
smart-search deep "深度搜索一下最近的比特币行情" --format json
smart-search deep "OpenAI Responses API web_search 和 Chat Completions 联网搜索怎么选" --budget deep --format json
smart-search deep "帮我核验这个说法是真是假：某某工具已经完全替代 Tavily 做 AI 搜索了" --format json
smart-search deep "https://example.com/source" --format json
```

看到输出里有 `mode=deep_research`、`decomposition`、多步 `steps`、`evidence_policy=fetch_before_claim`、`preflight.executed_by_deep_command=false`，就说明已经进入 Deep Research 计划模式。

## API 和 Key 申请入口

普通用户优先用 `smart-search setup` 配置。环境变量仍然支持 CI 和高级用户。
默认交互式 setup 已包含可选智能意图路由小节，可以直接配置 embeddings 和 classifier 路由，不需要进入 `--advanced`。

| Provider / 路线 | 用途 | 主要配置项 | 官方文档 | Key / 控制台 |
| --- | --- | --- | --- | --- |
| xAI Responses API | 主搜索，走 `web_search,x_search` 工具 | `XAI_API_KEY`、`XAI_API_URL`、`XAI_MODEL`、`XAI_TOOLS` | [docs.x.ai](https://docs.x.ai/docs) | [xAI API keys](https://console.x.ai/team/default/api-keys) |
| OpenAI-compatible Chat Completions | 主搜索，适合 OpenAI 官方或兼容中转；这里不会发送 xAI search tools | `OPENAI_COMPATIBLE_API_URL`、`OPENAI_COMPATIBLE_API_KEY`、`OPENAI_COMPATIBLE_MODEL`、`OPENAI_COMPATIBLE_STREAM` | [OpenAI platform docs](https://platform.openai.com/docs) | [OpenAI API keys](https://platform.openai.com/api-keys) 或你的兼容服务商 |
| Exa | 官方文档、API、论文、产品页、可信网页的低噪声发现 | `EXA_API_KEY` | [Exa docs](https://docs.exa.ai/) | [Exa API keys](https://dashboard.exa.ai/api-keys) |
| Context7 | SDK、库、框架、API 文档兜底 | `CONTEXT7_API_KEY`、`CONTEXT7_BASE_URL` | [Context7 docs](https://context7.com/docs) | [Context7](https://context7.com/) |
| 智谱 Web Search API | 中文、国内、时效、域名过滤类来源发现 | `ZHIPU_API_KEY`、`ZHIPU_API_URL`、`ZHIPU_SEARCH_ENGINE` | [智谱联网搜索文档](https://docs.bigmodel.cn/cn/guide/tools/web-search) | [智谱 API keys](https://open.bigmodel.cn/usercenter/apikeys) |
| 豆包搜索（Search Infinity） | 中文、国内、时效来源发现，走字节搜索索引 | `DOUBAO_SEARCH_API_KEY`、`DOUBAO_SEARCH_API_URL` | [豆包搜索 Custom 版](https://www.volcengine.com/docs/87772/2272953) | [联网搜索 API Key](https://console.volcengine.com/search-infinity/api-key) |
| 智谱 Coding Plan Remote MCP | 使用 Coding Plan 额度做联网搜索、网页读取、开源仓库发现 | `ZHIPU_MCP_API_KEY`、`ZHIPU_MCP_SEARCH_API_URL`、`ZHIPU_MCP_READER_API_URL`、`ZHIPU_MCP_ZREAD_API_URL` | [联网搜索 MCP](https://docs.bigmodel.cn/cn/coding-plan/mcp/search-mcp-server)、[网页读取 MCP](https://docs.bigmodel.cn/cn/coding-plan/mcp/reader-mcp-server)、[zread MCP](https://docs.bigmodel.cn/cn/coding-plan/mcp/zread-mcp-server) | [智谱 API keys](https://open.bigmodel.cn/usercenter/apikeys) |
| Tavily | 额外来源、URL fetch、站点 map | `TAVILY_API_URL`、`TAVILY_API_KEY`、`TAVILY_ENABLED` | [Tavily docs](https://docs.tavily.com/) | [Tavily app](https://app.tavily.com/home) |
| Jina Reader | 已知 URL 正文抓取；满足 standard 最低配置必须有 key | `JINA_API_KEY`、`JINA_READER_API_URL`、`JINA_RESPOND_WITH`、`JINA_TIMEOUT_SECONDS` | [Jina Reader](https://jina.ai/reader/) | [Jina AI](https://jina.ai/) |
| Firecrawl | fetch 兜底、补充网页来源 | `FIRECRAWL_API_URL`、`FIRECRAWL_API_KEY` | [Firecrawl docs](https://docs.firecrawl.dev/) | [Firecrawl API keys](https://www.firecrawl.dev/app/api-keys) |
| AnySearch | 实验垂直搜索验收入口，不是默认兜底 | `ANYSEARCH_API_URL`、`ANYSEARCH_API_KEY`、`ANYSEARCH_TIMEOUT_SECONDS` | [AnySearch 文档](https://www.anysearch.com/docs) | [AnySearch API keys](https://www.anysearch.com/console/api-keys) |
| Sciverse | 显式实验学术检索、语义论文检索、正文片段和引用/参考文献关系，不是默认兜底 | `SCIVERSE_API_TOKEN`、`SCIVERSE_API_URL`、`SCIVERSE_TIMEOUT_SECONDS` | [Sciverse Agent Tools](https://github.com/opendatalab/Sciverse-Agent-Tools) | Sciverse 控制台 / token 提供方 |

意图路由配置：

| 配置项 | 用途 |
| --- | --- |
| `SMART_SEARCH_INTENT_ROUTER` | `hybrid`、`rules` 或 `off`，默认 `hybrid` |
| `INTENT_EMBEDDING_API_URL` | 可选 OpenAI-compatible embeddings endpoint，用于语义能力路由；推荐 setup preset 使用 `https://api.siliconflow.cn/v1/embeddings` |
| `INTENT_EMBEDDING_API_KEY` | 可选 embeddings key；`doctor` 和 config 输出会脱敏 |
| `INTENT_EMBEDDING_MODEL` | embeddings 模型名；推荐 setup preset 使用 `Qwen/Qwen3-Embedding-8B` |
| `INTENT_EMBEDDING_THRESHOLD` | 语义路由阈值，默认 `0.74`；推荐 8B setup 值是 `0.475`；这是模型相关参数 |
| `INTENT_EMBEDDING_MARGIN` | top1 与第二名分数差阈值，默认 `0.05`；推荐 8B setup 值是 `0.053`；差距不足时只记录 ambiguous 信号，不直接加 capability |
| `INTENT_CLASSIFIER_API_URL` | 可选 OpenAI-compatible chat-completions endpoint，用于结构化意图分类 |
| `INTENT_CLASSIFIER_API_KEY` | 可选 classifier key；`doctor` 和 config 输出会脱敏 |
| `INTENT_CLASSIFIER_MODEL` | classifier 模型名 |
| `INTENT_ROUTER_TIMEOUT_SECONDS` | 可选远程路由调用超时，默认 `8` |

默认 `hybrid` 是 fail-open：embeddings 或 classifier 没配置、超时或失败时，会在 `degraded_reason` 里说明，然后自动退回本地规则。语义路由只有在 top1 相似度达到 `INTENT_EMBEDDING_THRESHOLD`，并且 top1 与第二名差值达到 `INTENT_EMBEDDING_MARGIN` 时，才会直接添加 capability；否则只记录 ambiguous 信号。classifier 可以补充 capability，但未知 capability 和 provider 名会被忽略；provider 仍然只能由 capability-first 注册表选择。

普通用户推荐直接使用 Qwen3-Embedding-8B preset：`INTENT_EMBEDDING_API_URL=https://api.siliconflow.cn/v1/embeddings`、`INTENT_EMBEDDING_MODEL=Qwen/Qwen3-Embedding-8B`、`INTENT_EMBEDDING_THRESHOLD=0.475`、`INTENT_EMBEDDING_MARGIN=0.053`。选择 8B 模型且没有手动配置 threshold/margin 时，`smart-search setup` 会自动补齐这两个推荐值。

embedding 余弦分数强依赖模型。`route-calibrate` 保留给高级复验：换 `INTENT_EMBEDDING_MODEL`、换 embedding endpoint，或者后续加入真实 query 校准集后再运行：

```powershell
smart-search route-calibrate --models "Qwen/Qwen3-Embedding-8B" --format markdown
```

再按报告推荐值设置 `INTENT_EMBEDDING_THRESHOLD` 和 `INTENT_EMBEDDING_MARGIN`。校准主指标是 semantic-only Macro-F1；full-route Macro-F1 只用来验证 rules/classifier 兜底后的真实路由表现。

几个容易混淆的点：

- xAI 官方联网搜索路线是 Responses API `/responses`，只通过 `XAI_*` 配置。兼容中转/网关走 Chat Completions `/chat/completions`，只通过 `OPENAI_COMPATIBLE_*` 配置。
- `OPENAI_COMPATIBLE_STREAM=true` 或 `smart-search search --stream` 只会给 OpenAI-compatible 的 `search` 和 provider 侧 `fetch` 设置 `stream=true`。它是中转长请求兼容开关，不改变 xAI Responses、URL 描述和来源排序行为。
- 旧的 `SMART_SEARCH_API_URL`、`SMART_SEARCH_API_KEY`、`SMART_SEARCH_API_MODE`、`SMART_SEARCH_MODEL`、`SMART_SEARCH_XAI_TOOLS` 不再是受支持配置项。请显式使用 `XAI_*` 或 `OPENAI_COMPATIBLE_*`。
- 不要给 OpenAI-compatible Chat Completions 中转强塞 xAI 的 `web_search` / `x_search` 工具或旧 `search_parameters`。
- `zhipu-search` 对应的是智谱 Web Search API，不是 Chat Completions `tools=[web_search]`，不是 Search Agent，也不是 MCP Server。
- `doubao-search` 对应豆包搜索 / Search Infinity REST：`https://open.feedcoopapi.com/search_api/web_search`。它不是方舟 Ark Chat Completions Key，也不是方舟 Responses 联网插件。
- 智谱 Coding Plan 是单独的 Remote MCP 路线：`web_search_prime` 对应 `web_search`，`webReader` 对应 `web_fetch`，zread 工具对应显式仓库/文档发现命令。它不会混进现有 `/paas/v4/web_search` 智谱 REST provider。
- 智谱 Coding Plan MCP 需要单独的 Coding Plan 权益。普通 `ZHIPU_API_KEY` 能用 Web Search API，不代表能用 `zhipu-mcp-search` 或 zread。未配置或未授权 `ZHIPU_MCP_API_KEY` 时，Smart Search 会跳过这些 MCP provider；`standard` 最低配置和同 capability 兜底仍会通过已配置的 REST/search/fetch provider 工作。
- Jina Reader 不是通用搜索 provider。只有配置 `JINA_API_KEY` 后才计入 `standard`；`JINA_RESPOND_WITH=readerlm-v2` 也必须配置 `JINA_API_KEY`。
- `ZHIPU_SEARCH_ENGINE` 默认是 `search_std`。官方值包括 `search_std`、`search_pro`、`search_pro_sogou`、`search_pro_quark`；`config set` 仍允许自定义值，方便官方以后新增服务。
- `TAVILY_API_URL` 只影响 Tavily，不会代理智谱。Tavily Hikari / 号池用 `https://<host>/api/tavily`；setup 会把根域名或 `/mcp` 输入规范化成这个 REST base。
- `TAVILY_ENABLED` 默认是 `true`。即使已有 key，设为 `false` 也会禁用 Tavily：它会从 web-search 和 fetch 路由中移除，直接 Tavily 调用和 `doctor` 都不会发 Tavily 请求，`map` 会本地返回配置错误。它不会启用 Firecrawl，也不会改变同 capability 兜底边界。
- `FIRECRAWL_API_URL` 默认是 `https://api.firecrawl.dev/v2`。
- AnySearch 默认走 `https://api.anysearch.com/mcp` 的 JSON-RPC 2.0 `tools/call`。没有 key 时允许匿名请求；有 key 时发送 `Authorization: Bearer ...`。HTTP 200 但 `result.isError=true` 会按 provider error 处理，不能当成功证据。`--sub-domain-params` 会先解析成 JSON object，随后可重复的 `--param key=value` 覆盖同名键；参数不合法时会在发请求前失败。
- Sciverse 默认走 `https://api.sciverse.space` 的 native HTTP/OpenAPI。必须配置 `SCIVERSE_API_TOKEN`；未配置时本地返回 `config_error` 且不发网络请求；已配置时发送 `Authorization: Bearer ...`。它保持 explicit-only：不是 `docs_search`，不满足 `standard`，不进入默认 `search` / `research` 兜底。
- `doctor` 和 `route` 会报告 intent router 的配置状态、embedding 模型、threshold、margin、配置来源、超时和是否可降级，不会暴露 router API key。

非交互配置示例：

```powershell
smart-search setup --non-interactive `
  --xai-api-key "your-xai-key" `
  --xai-model "grok-4-fast" `
  --openai-compatible-api-url "https://api.openai.com/v1" `
  --openai-compatible-api-key "your-openai-or-relay-key" `
  --openai-compatible-model "gpt-4.1" `
  --openai-compatible-stream "false" `
  --validation-level "balanced" `
  --fallback-mode "auto" `
  --minimum-profile "standard" `
  --intent-router "hybrid" `
  --intent-embedding-api-url "https://api.siliconflow.cn/v1/embeddings" `
  --intent-embedding-api-key "your-siliconflow-key" `
  --intent-embedding-model "Qwen/Qwen3-Embedding-8B" `
  --intent-embedding-threshold "0.475" `
  --intent-embedding-margin "0.053" `
  --exa-key "your-exa-key" `
  --context7-key "your-context7-key" `
  --zhipu-key "your-zhipu-key" `
  --zhipu-api-url "https://open.bigmodel.cn/api" `
  --zhipu-search-engine "search_pro_sogou" `
  --doubao-key "your-doubao-search-key" `
  --doubao-api-url "https://open.feedcoopapi.com" `
  --zhipu-mcp-key "your-zhipu-coding-plan-key" `
  --jina-key "your-jina-key" `
  --tavily-api-url "https://api.tavily.com" `
  --tavily-key "your-tavily-key" `
  --firecrawl-api-url "https://api.firecrawl.dev/v2" `
  --firecrawl-key "your-firecrawl-key"
```

默认最低配置是 `SMART_SEARCH_MINIMUM_PROFILE=standard`，至少需要：

- `main_search`：xAI Responses 或 OpenAI-compatible 二选一；
- `docs_search`：Exa 或 Context7 二选一；
- `web_fetch`：Tavily、带 `JINA_API_KEY` 的 Jina、智谱 Coding Plan MCP Reader、Firecrawl 四选一。

缺少任一最低能力时，`doctor` 和 `search` 会 fail closed 并返回缺失 capability。`SMART_SEARCH_MINIMUM_PROFILE=off` 只建议本地实验使用。

AnySearch 是可选实验配置，不满足也不改变 `standard` 最低配置：

```powershell
smart-search setup --non-interactive --anysearch-api-url "https://api.anysearch.com/mcp" --anysearch-key "your-anysearch-key"
smart-search anysearch-domains security --format json
smart-search anysearch-search "CVE-2024-3094" --domain security --sub-domain vuln --param type=cve --param value=CVE-2024-3094 --max-results 3 --format json
smart-search anysearch-extract "https://example.com/source" --max-length 12000 --format json
smart-search anysearch-batch "AAPL" "RAG papers" --max-results 2 --format json
```

简单垂直域仍支持点号简写，例如 `code.doc` 会由 CLI 发成 `domain=code` 加 `sub_domain=doc`。需要结构化参数的垂直域应先用 `anysearch-domains` 查看要求，再用拆分形式加 `--sub-domain-params` JSON object 和/或重复 `--param key=value`；重复参数会覆盖 JSON 中同名键，JSON 不合法、缺少 `=` 或空 key 会在发请求前失败。`anysearch-domains DOMAIN` 会调用 live `get_sub_domains`；省略 `DOMAIN` 时读取其 `tools/list` schema。`anysearch-extract --max-length` 上游只发送 `url`，仅在值为正时本地截断成功结果的顶层和 results 文本字段。

Sciverse 也是可选实验配置，不满足也不改变 `standard` 最低配置：

```powershell
smart-search setup --non-interactive --sciverse-token "your-sciverse-token" --sciverse-api-url "https://api.sciverse.space"
smart-search sciverse-catalog --collection papers --format json
smart-search sciverse-search "transformer retrieval" --year-from 2020 --page-size 5 --format json
smart-search sciverse-semantic "attention mechanism" --top-k 3 --mode balanced --format json
smart-search sciverse-read "doc-id-from-search" --offset 0 --limit 4096 --format json
smart-search sciverse-relations "unique-id-from-search" --relation CITATIONS --page-size 25 --format json
```

`sciverse-read` 用 `doc_id`，`sciverse-relations` 用 `unique_id`。`CITATIONS` 表示引用目标论文的论文；`REFERENCES` 表示目标论文引用的论文；`RELATED_WORKS` 表示相关工作。`--filters-advanced` 和 `--sort-advanced` 接收 JSON array，用于第一版没有提升成一等参数的学术字段。

本机配置文件位置：

- Windows 默认：`%LOCALAPPDATA%\smart-search\config.json`。
- Linux/macOS 默认：`~/.config/smart-search/config.json`。
- `SMART_SEARCH_CONFIG_DIR` 是高级覆盖项，适合 CI、容器、沙箱或便携安装。
- 更早的 Windows 源码默认路径曾是 `~\.config\smart-search\config.json`，但有些安装会通过 `SMART_SEARCH_CONFIG_DIR` 提前固定到 `%LOCALAPPDATA%\smart-search`。如果新版默认位置还没有配置，但旧 home 路径存在配置，Smart Search 会以 `legacy_windows_home` 方式继续读取旧配置，避免升级后配置丢失；`doctor` 会同时报告当前生效路径、默认路径、旧 home 路径、`SMART_SEARCH_CONFIG_DIR` 的值，以及这个覆盖项是不是只是等于当前默认路径。

常用环境变量：

| 变量 | 用途 |
| --- | --- |
| `XAI_API_KEY` | xAI Responses provider key |
| `XAI_API_URL` | xAI API 地址，默认 `https://api.x.ai/v1` |
| `XAI_MODEL` | xAI 模型名 |
| `XAI_TOOLS` | xAI Responses 工具列表，通常 `web_search,x_search` |
| `OPENAI_COMPATIBLE_API_URL` | OpenAI-compatible `/v1` base URL |
| `OPENAI_COMPATIBLE_API_KEY` | OpenAI-compatible key |
| `OPENAI_COMPATIBLE_MODEL` | 兼容模型名 |
| `OPENAI_COMPATIBLE_STREAM` | OpenAI-compatible 中转兼容开关，接受 `true/1/yes`，默认 `false` |
| `ANYSEARCH_API_URL` | AnySearch JSON-RPC endpoint，默认 `https://api.anysearch.com/mcp` |
| `ANYSEARCH_API_KEY` | 可选 AnySearch key |
| `ANYSEARCH_TIMEOUT_SECONDS` | AnySearch 请求超时，默认 `30` |
| `SCIVERSE_API_TOKEN` | 显式 Sciverse 学术命令需要的 token |
| `SCIVERSE_API_URL` | Sciverse API base URL，默认 `https://api.sciverse.space` |
| `SCIVERSE_TIMEOUT_SECONDS` | Sciverse 请求超时，默认 `30` |
| `SMART_SEARCH_INTENT_ROUTER` | 意图路由模式：`hybrid`、`rules`、`off`，默认 `hybrid` |
| `INTENT_EMBEDDING_API_URL` | 可选 embeddings endpoint，用于语义路由 |
| `INTENT_EMBEDDING_API_KEY` | 可选 embeddings key |
| `INTENT_EMBEDDING_MODEL` | embeddings 模型名 |
| `INTENT_EMBEDDING_THRESHOLD` | 语义路由阈值，默认 `0.74`，换模型后用 `route-calibrate` 校准 |
| `INTENT_EMBEDDING_MARGIN` | top1 与第二名分数差阈值，默认 `0.05` |
| `INTENT_CLASSIFIER_API_URL` | 可选 classifier chat-completions endpoint |
| `INTENT_CLASSIFIER_API_KEY` | 可选 classifier key |
| `INTENT_CLASSIFIER_MODEL` | classifier 模型名 |
| `INTENT_ROUTER_TIMEOUT_SECONDS` | 可选路由调用超时，默认 `8` |
| `EXA_API_KEY` | Exa key |
| `CONTEXT7_API_KEY` | Context7 key |
| `ZHIPU_API_KEY` | 智谱 Web Search key |
| `ZHIPU_API_URL` | 智谱 API 地址，默认 `https://open.bigmodel.cn/api` |
| `ZHIPU_SEARCH_ENGINE` | 智谱搜索服务，例如 `search_pro_sogou` |
| `DOUBAO_SEARCH_API_KEY` | 豆包搜索 / Search Infinity key，不是方舟 Ark key |
| `DOUBAO_SEARCH_API_URL` | 豆包搜索 API 地址，默认 `https://open.feedcoopapi.com` |
| `DOUBAO_SEARCH_TIMEOUT_SECONDS` | 豆包搜索超时，默认 `30` |
| `ZHIPU_MCP_API_KEY` | 智谱 Coding Plan Remote MCP key |
| `ZHIPU_MCP_SEARCH_API_URL` | 智谱 Coding Plan 联网搜索 MCP endpoint |
| `ZHIPU_MCP_READER_API_URL` | 智谱 Coding Plan 网页读取 MCP endpoint |
| `ZHIPU_MCP_ZREAD_API_URL` | 智谱 Coding Plan zread MCP endpoint |
| `ZHIPU_MCP_TIMEOUT_SECONDS` | 智谱 Coding Plan MCP 请求超时，默认 `30` |
| `JINA_API_KEY` | Jina Reader key；满足 standard 必须配置 |
| `JINA_READER_API_URL` | Jina Reader endpoint，默认 `https://r.jina.ai` |
| `JINA_RESPOND_WITH` | Jina Reader 响应模式，例如 `readerlm-v2`；需要 `JINA_API_KEY` |
| `JINA_TIMEOUT_SECONDS` | Jina Reader 请求超时，默认 `30` |
| `TAVILY_API_URL` | Tavily REST base |
| `TAVILY_API_KEY` | Tavily key |
| `TAVILY_ENABLED` | 默认 `true`；只有 `true`、`1`、`yes` 启用 Tavily，其他值禁用且不发 Tavily 网络请求 |
| `TAVILY_TIMEOUT_SECONDS` | Tavily 连通性检查超时，默认 `30`；公益站/号池较慢时可调大 |
| `FIRECRAWL_API_URL` | Firecrawl REST base |
| `FIRECRAWL_API_KEY` | Firecrawl key |
| `SMART_SEARCH_VALIDATION_LEVEL` | `fast`、`balanced`、`strict` |
| `SMART_SEARCH_FALLBACK_MODE` | `auto` 或 `off` |
| `SMART_SEARCH_RESEARCH_PREFERRED_PROVIDERS` | `research` 路由优先 provider CSV，只能在同 capability 内调整顺序 |
| `SMART_SEARCH_RESEARCH_DISABLED_PROVIDERS` | `research` 禁用 provider CSV，不能改变 provider capability 边界 |
| `SMART_SEARCH_CONFIG_DIR` | 指定本机配置和日志根目录 |

## 常用命令

| 命令 | 简写 | 用途 |
| --- | --- | --- |
| `search` | `s` | 快速联网搜索和综合回答 |
| `route` | `rt` | 只解释需要哪些 capability，不调用 provider |
| `deep` | `dr` | Deep Research 离线计划 |
| `research` | `rs` | live Deep Research 执行 |
| `fetch` | `f` | 抓一个 URL 正文 |
| `map` | `m` | 读取站点结构 |
| `exa-search` | `exa`、`x` | Exa 来源发现 |
| `exa-similar` | `xs` | 从一个 URL 找相似页面 |
| `zhipu-search` | `z`、`zp` | 智谱 Web Search API |
| `doubao-search` | `dd`、`volc-search` | 豆包搜索 / Search Infinity |
| `zhipu-mcp-search` | `zmcp-search` | 智谱 Coding Plan MCP `web_search_prime` |
| `zhipu-mcp-reader` | `zmcp-reader` | 智谱 Coding Plan MCP `webReader` |
| `zhipu-mcp-search-doc` | `zmcp-doc` | 通过 zread MCP 搜开源仓库文档 |
| `zhipu-mcp-repo-structure` | `zmcp-tree` | 通过 zread MCP 读仓库结构 |
| `zhipu-mcp-read-file` | `zmcp-file` | 通过 zread MCP 读单个仓库文件 |
| `anysearch-domains` | `as-domains` | 实验 AnySearch 域名/能力发现 |
| `anysearch-search` | `as-search`、`as` | 实验 AnySearch 垂直/通用搜索 |
| `anysearch-extract` | `as-extract` | 实验 AnySearch URL 抽取 |
| `anysearch-batch` | `as-batch` | 实验 AnySearch 批量搜索，最多 5 条 |
| `sciverse-catalog` | `sv-catalog` | 实验 Sciverse 学术字段 catalog |
| `sciverse-search` | `sv-search`、`sv` | 实验 Sciverse 结构化学术检索 |
| `sciverse-semantic` | `sv-semantic` | 实验 Sciverse 语义论文检索 |
| `sciverse-read` | `sv-read` | 用 `doc_id` 读取 Sciverse 正文片段 |
| `sciverse-relations` | `sv-relations` | 用 `unique_id` 查询 Sciverse 引用/参考文献/相关工作 |
| `context7-library` | `c7`、`ctx7` | 查 Context7 库候选 |
| `context7-docs` | `c7d`、`c7docs`、`ctx7-docs` | 抓 Context7 文档 |
| `route-calibrate` | `route-cal`、`rcal` | 评测 embedding 路由模型并推荐 threshold/margin |
| `doctor` | `d` | 配置和连通性检查 |
| `setup` | `init` | 配置向导 |
| `config` | `cfg` | 本机配置读写 |
| `model` | `mdl` | 查看显式 provider 模型；修改请用 `config set XAI_MODEL` 或 `OPENAI_COMPATIBLE_MODEL` |
| `smoke` | `sm` | provider 路由冒烟测试 |
| `regression` | `reg` | 离线回归测试 |

全部命令见 [完整命令参考](https://github.com/konbakuyomu/smartsearch/blob/main/docs/guide/zh-CN/cli-reference.md)。

## 常见问题

```powershell
smart-search search "query" --validation balanced --extra-sources 3 --timeout 90 --format json --output result.json
smart-search route "React useEffect API docs" --format markdown
smart-search route-calibrate --models "Qwen/Qwen3-Embedding-8B" --format markdown
smart-search research "query" --budget deep --fallback auto --format json --output research.json
smart-search search "query" --stream --format json
smart-search search "query" --no-stream --format json
smart-search search "nba战报" --format content
smart-search exa-search "OpenAI Responses API documentation" --include-domains platform.openai.com developers.openai.com --num-results 5 --include-text --format json
smart-search context7-library "react" "hooks" --format json
smart-search context7-docs "/reactjs/react.dev" "useEffect cleanup" --format json
smart-search zhipu-search "今天国内 AI 新闻" --search-engine search_pro_sogou --count 5 --format json
smart-search doubao-search "今天国内 AI 新闻" --count 5 --format json
smart-search zhipu-mcp-search "今天国内 AI 新闻" --count 5 --format json
smart-search zhipu-mcp-reader "https://example.com/source" --format json
smart-search zhipu-mcp-search-doc "owner/repo" "install" --format json
smart-search anysearch-search "CVE-2024-3094" --domain security --sub-domain vuln --param type=cve --param value=CVE-2024-3094 --max-results 3 --format json
smart-search anysearch-extract "https://example.com/source" --max-length 12000 --format json
smart-search sciverse-search "transformer retrieval" --year-from 2020 --page-size 5 --format json
smart-search sciverse-relations "unique-id-from-search" --relation CITATIONS --format json
smart-search exa-similar "https://example.com/source" --num-results 5 --format json
smart-search fetch "https://example.com/source" --format markdown --output page.md
smart-search map "https://docs.example.com" --instructions "Find API reference pages" --max-depth 1 --limit 50 --format json
smart-search doctor --format markdown
smart-search smoke --mock --format json
smart-search regression
```

至少一个可用的检索渠道就能搜索。App 的「检查配置」和概览页按主搜索、文档检索、网页抓取三类提示；三类都配上，Jev 才有足够的渠道可选，读原网页也有专门的抓取服务。

</details>

<details>
<summary><strong>不填 TypeSafe Key 能用吗？</strong></summary>

能。Jev 是可选的。没有 Key 时，默认按本地能力规则选路，结果里会标记为降级；也可以在「意图路由」里直接选「本地路由」。

</details>

<details>
<summary><strong>关掉 App 还能用吗？</strong></summary>

能。搜索由独立 CLI 执行，AI 按 Skill 里的说明直接调用它。如果关闭时还有 App 发起的任务在运行，App 会问你是留在后台继续，还是取消任务再退出；取消只影响 App 自己发起的任务，不会终止外部 CLI。

</details>

<details>
<summary><strong>会花钱吗？</strong></summary>

Smart Search 本身免费开源。服务商测试、搜索、`doctor` 和 `route --remote` 会调用你配置的服务，可能消耗对应额度。`route`（不加 `--remote`）、`deep` 和打开 App 都不会发起付费请求。

</details>

1. 用 `search`、`exa-search`、`zhipu-search`、`doubao-search` 或 `exa-similar` 找候选 URL。
2. 用 `fetch` 抓关键 URL 正文。
3. 最终回答只引用 fetch 正文能支撑的事实。
4. 没有 fetch 的来源标为未验证候选。

服务商由你选择，可以同时配置多家；每次搜索由 Jev 按问题挑渠道；回答所依据的网页可以抓下原文核对。Skill 会让 AI 在同一任务里统一使用 Smart Search，不混用别的联网途径。

</details>

<details>
<summary><strong>Windows 提示 SmartScreen，macOS 提示无法验证开发者？</strong></summary>

Windows 的 `-signed.exe` 安装包使用自签名证书，仍可能出现 SmartScreen 提示，详见 [Windows 签名与首次启动](docs/windows-signing.md)。macOS 包使用 ad-hoc 完整性签名和独立的 Sparkle EdDSA 更新签名，尚无 Developer ID 签名或公证。

- 降低 `--extra-sources`；
- 把大问题拆成多个小问题；
- 先用 `exa-search`、`zhipu-search` 或 `doubao-search` 找来源，再 `fetch` 关键网页。

<details>
<summary><strong>App 和 CLI 怎么更新？</strong></summary>

两者分别更新。App 每次启动时检查，有新版本会弹窗询问；也可以在「设置与关于 → App 更新」检查并下载，确认后才下载；CLI 在「概览 → 1. 准备本地环境」更新，或运行 `npm install -g @konbakuyomu/smart-search@latest`。CLI 升级后会维护已接入的 Skills，并保留个人修改。

</details>

## 已知限制

- 搜索命中只是线索。重要结论请读来源正文，不要只凭摘要下判断。
- 普通搜索不做证据评估；需要核对时用在线研究，或让 AI 读原网页。
- Jev 的阈值（选路 0.5、证据充分 0.75）是初始策略，需要用实际问题校准。
- 服务商的可用性、额度和返回质量由服务商决定。
- 旧版 Inno 安装需要先完成一次完整迁移；最终的 GUI 和旧安装迁移验收单独记录，不由自动构建和升级检查代替。

## 文档

| 主题 | 链接 |
| --- | --- |
| App 配置与使用 | [docs/guide/zh-CN/app.md](https://github.com/konbakuyomu/smartsearch/blob/main/docs/guide/zh-CN/app.md) |
| CLI 使用指南 | [docs/guide/zh-CN/cli.md](https://github.com/konbakuyomu/smartsearch/blob/main/docs/guide/zh-CN/cli.md) |
| 服务商与配置 | [docs/guide/zh-CN/configuration.md](https://github.com/konbakuyomu/smartsearch/blob/main/docs/guide/zh-CN/configuration.md) |
| 搜索、研究与证据 | [docs/guide/zh-CN/research.md](https://github.com/konbakuyomu/smartsearch/blob/main/docs/guide/zh-CN/research.md) |
| Jev 多渠道路由 | [docs/jev-routing.md](https://github.com/konbakuyomu/smartsearch/blob/main/docs/jev-routing.md) |
| 排障 | [docs/guide/zh-CN/troubleshooting.md](https://github.com/konbakuyomu/smartsearch/blob/main/docs/guide/zh-CN/troubleshooting.md) |
| 开发与发布 | [docs/guide/zh-CN/development.md](https://github.com/konbakuyomu/smartsearch/blob/main/docs/guide/zh-CN/development.md) |

## 致谢

感谢 [LINUX DO](https://linux.do/) 社区的反馈和讨论。

[![Star History Chart](https://api.star-history.com/svg?repos=konbakuyomu/smartsearch&type=Date)](https://www.star-history.com/#konbakuyomu/smartsearch&Date)

## 许可证

本项目采用 [MIT](https://github.com/konbakuyomu/smartsearch/blob/main/LICENSE) 许可。动画中的 Clawd 是 Anthropic 吉祥物的非官方同人形象，与 Anthropic 无关，也未获其认可。
