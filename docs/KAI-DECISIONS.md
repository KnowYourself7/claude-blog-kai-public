# Kai 的二次开发裁定登记表

这个文件只属于 fork（KnowYourself7/claude-blog-kai），上游没有，同步上游时不会冲突。

- 记录二次开发中需要 Kai 拍板的规则：阈值、数量、取舍。
- 插件文件里要用到时，引用 K 编号，不重复抄写内容。
- 改主意时新加一行，写明取代了哪一条，旧行保留。
- "来源"一栏分三种：课程写明（带瑜东页码）、本项目设计、未写明。
- K-001 到 K-008 记在旧分支 feat/researcher-mcp 的同名文件里，做到对应功能（阶段 3）时逐条带回。

| ID | 要裁定的事 | 来源 | 原来 | Kai 的裁定 | 日期 |
|---|---|---|---|---|---|
| K-009 | 大纲 v1 到 v2 之间停不停下等 Kai 审 | 本项目设计。瑜东 p.125 写明 v1 自审改 v2；p.127 讲师备注说检查必须保留，但已授权全程执行时不必每阶段人工确认 | 插件原文不停，一口气出完整份 brief | 默认停：v1 和自审结果给 Kai 看，等回复（修改意见或 "pass"）再出 v2。请求里带 `--auto` 就不停，自审照做并存进 `outline-v1.md` 末尾。理由：现在处在学习和调试期，要亲眼看每一步 | 2026-09-26 |
| K-010 | brief 及其分步产物存在哪 | 本项目设计。瑜东 p.127 只要求落盘，没规定目录 | 插件原文存 `briefs/[slug]-brief.md`，单文件 | 一篇一个文件夹：`briefs/[slug]/brief.md`、`briefs/[slug]/outline-v1.md`，以后 v2、需求面、证据计划都进同一文件夹 | 2026-09-25 |
| K-012 | brief 各产物的落盘顺序 | 本项目设计。瑜东 p.125 到 p.126 写明 v1 自审改 v2，p.127 阶段门要求结构清楚再往下；课程没有 brief.md 这个文件 | 插件原文 Step 5 一次输出整份 brief，Step 6 一次存盘 | `outline-v1.md` → 自审、停下等审 → `outline-v2.md` → 最后存 `brief.md`（大纲段用 v2 原样）。理由：`/blog write` 读 brief，先写 brief 会带着没审过的大纲 | 2026-09-26 |
| K-013 | DataForSEO 查询用什么地区和语言 | 课程写明要问清（瑜东 p.107 "目标国家与语言"）；默认值是本项目设计 | 插件原文不问地区，用 WebSearch | 默认美国 + 英语（`location_code` 2840、`language_code` `en`），不停下问；请求里写了别的地区才换。每个产物文件记下本次地区语言 | 2026-09-26 |
| K-014 | 项目里已有旧调研文件时怎么办 | 本项目设计。瑜东 p.109 要求逐条判断复用/重新验证/避用，但 02 步暂缓 | 插件原文无规定；9-26 验收时模型整份复用了 9-24 的 research 文件 | 阶段 2 每次都重新调 DataForSEO，不读项目里任何旧调研文件（research/、runs/、旧 briefs）。理由：复杂度最低。做 02 时再定复用规则 | 2026-09-26 |
| K-015 | 怎样用首页结果判断搜索意图 | 瑜东 p.111 写明看首页页面类型分流；讲师的"博客占比低于 30%"是内部规则，不采用 | 插件原文只写 "Note the search intent" | 首页前 10 条自然结果按类型归类：博客/指南页、品类页、产品页、其他（本地、工具、视频、论坛等）。占比最多的一类代表核心意图。博客最多就继续；别的类型最多，或博客与别的类型并列第一，都停下问 Kai：照写 / 换词 / 交给别的页面类型 | 2026-09-26 |
| K-017 | DataForSEO 调用边界 | 本项目设计（取代 K-007 在阶段 2 的适用范围；K-007 是给 researcher 定的） | 无 | 只许 5 个接口：`serp/google/organic/live/advanced`、`serp/google/autocomplete/live/advanced`、`dataforseo_labs/google/keyword_suggestions/live`、`dataforseo_labs/google/related_keywords/live`、`dataforseo_labs/google/keyword_overview/live`。基本 5 次，词少补词最多 +3 次，每次出错最多重试 1 次，不开 clickstream。每次运行按返回的 cost 累加，超过花费上限就停下问 Kai；上限在 2-2 试跑后填 | 2026-09-26 |
