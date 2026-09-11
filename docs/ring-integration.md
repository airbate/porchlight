# Ring Integration — M0 Verification Checklist

> 状态：⚠️ 未核实。这是 M0 周（9/11–9/18）第一优先级任务。
> 硬性要求回顾：项目须**运行时真实调用** Ring API/SDK/模拟器（不能只在 README 提及）；物理设备可选。

## 待核实问题清单

| # | 问题 | 为什么重要 | 核实方式 |
|---|------|-----------|---------|
| 1 | 本次 hackathon 的 Ring 开发者资源入口在哪（Devpost resources 页？developer.ring.com？） | 决定我们用哪套 API/SDK | 通读 Devpost 资源标签页 + Build Session 回放（youtu.be/ws61g53S2b4）Ring 段落 |
| 2 | 模拟器如何获取：网页版？CLI？需要审批？ | 无硬件路径的根基 | 注册后实测 |
| 3 | API 形态：REST？事件推送（webhook）还是轮询？图像帧怎么拿？ | 决定 `ring_client.py` 的适配器写法 | 读官方文档 |
| 4 | 认证方式与凭据申请周期（OAuth? API key? 审核要几天？） | 若审核周期 >1 周要提前排期 | 注册流程实测，记录耗时 → 写进 Friction Log |
| 5 | 是否收费（Ring Device Access 历史上有商业授权费） | 超出 $0 预算要触发 go/no-go | 注册/文档确认 |
| 6 | 中国大陆网络访问 Ring 门户/模拟器是否稳定 | 日常开发依赖 | 实测，必要时配稳定代理 |
| 7 | 演示要求："真实数据流"在 Ring 赛道的具体验收口径 | 视频拍摄方式依赖它 | 规则原文 + Q&A/updates 页 |

## 核实后的动作

- [ ] 把确认的工具链形态写回本文档（替换本节）
- [ ] 按真实 API 形态实现 `backend/app/ring_client.py` 的适配器（当前是占位协议 + fixture 回放）
- [ ] 把过程中的坑记入 `docs/friction-log.md`

## 降级预案（9/18 go/no-go）

1. 模拟器免费可用 → 继续 PorchLight（Ring 主赛道）
2. 模拟器不可用/收费过高 → 检查是否有 hackathon 官方提供的沙箱凭据（updates 页/Q&A）
3. 仍不可行 → 切换 Bee 方向（需 Apple Watch）或 Alexa+ MCP 方向，里程碑表平移 1 周，本仓库改名复用
