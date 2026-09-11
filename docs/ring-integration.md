# Ring Integration — M0 Verification Checklist

> 状态：⚠️ 未核实。这是 M0 周（9/11–9/18）第一优先级任务。
> 硬性要求回顾：项目须**运行时真实调用** Ring API/SDK/模拟器（不能只在 README 提及）；物理设备可选。

## 待核实问题清单（2026-09-12 更新：门户已抓取，见 docs/主办方深度研究.md）

| # | 问题 | 为什么重要 | 核实方式 |
|---|------|-----------|---------|
| 1 | 注册 `developer.amazon.com/ring` → sandbox + Ring test account 如何获取？ | **接入路径已从"模拟器"修正为 sandbox + test account**（门户无 simulator 字样） | 实际注册走一遍，记录审批耗时 |
| 2 | test account 是否自带 Ring 订阅（门户脚注 "Compatible Ring subscription required"） | 订阅门槛直接决定零成本可行性，make-or-break | 问 hackathon 经理 janet@devpost.com 或注册流程实测 |
| 3 | OAuth 流程实测：Ring App 授权 → code 换 Bearer token；webhook HMAC 验签 | 已知形态，剩实现细节 | 文档 + 实测 |
| 4 | 事件 webhook 的 human/animal/vehicle 分类与我们的 Bedrock 层如何分工 | 差异化红线：不重建平台已有分类 | 读 API 文档，设计去重逻辑 |
| 5 | 官方 Ring MCP Server 可否用于我们的开发流程（API 检索/代码生成） | 提效 + 可写进 Friction Log 正面反馈 | 装上试用 |
| 6 | hackathon 页承诺的"simulator"与门户"sandbox"是否同一物 | 决定无硬件演示形态 | 等 resources 页放出 / 问经理 |
| 7 | 中国大陆访问门户/sandbox 稳定性 | 日常开发依赖 | 实测 |
| 8 | "真实数据流"验收口径 | 决定演示视频拍摄方式 | 规则原文 + updates 页 |

## 核实后的动作

- [ ] 把确认的工具链形态写回本文档（替换本节）
- [ ] 按真实 API 形态实现 `backend/app/ring_client.py` 的适配器（当前是占位协议 + fixture 回放）
- [ ] 把过程中的坑记入 `docs/friction-log.md`

## 降级预案（9/18 go/no-go）

1. 模拟器免费可用 → 继续 PorchLight（Ring 主赛道）
2. 模拟器不可用/收费过高 → 检查是否有 hackathon 官方提供的沙箱凭据（updates 页/Q&A）
3. 仍不可行 → 切换 Bee 方向（需 Apple Watch）或 Alexa+ MCP 方向，里程碑表平移 1 周，本仓库改名复用
