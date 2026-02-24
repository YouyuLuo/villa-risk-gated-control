# ViLLA 决策链路解析：如何阻止一次“灾难性”的误触发？

本剧本基于 `sample_record.json` 中的真实评估数据，展示 ViLLA 如何在面临具有欺骗性的场景时，通过 **Risk-Gated** 机制保证系统的可靠性。

## 场景还原 (Scene: BR01)
* **输入视频**: 卧室场景（`BR01`）。
* **真实发生事件**: 用户躺在床上盖着被子玩手机 (`phone_scrolling`)。
* **可用设备**: 窗帘 (`curtain`)，台灯 (`desk_lamp`)。

## 阶段 1：大模型提议 (VLM Proposal)
在这个阶段，VLM 充当“观察者”和“提议者”。它很容易过度反应。
* **观察 (Observation)**: "A person is lying on a bed with a blanket, using a phone."
* **内部推理 (Rationale)**: VLM 认为躺在床上玩手机对眼睛不好，判定为光线过暗 (`too_dark: true`) 且有危险 (`hazard: true`)。
* **危险的提议 (Candidates)**: VLM 强烈建议以 **0.8** 的高置信度打开台灯 (`desk_lamp` brightness 50)。

> **⚠️ 痛点**: 如果采用端到端直接控制（Direct Execution），此时台灯会被突然打开，严重打扰试图入睡或正在休息的用户。这就是为什么 Direct 模式的误触发率高达 64.87%。

## 阶段 2：风险门控验证 (Risk-Gated Verification)
这是 ViLLA 的核心防御塔。系统并不盲目听从 VLM。
* 系统提取当前的物理传感器状态和预设的房间策略 (`policy_signals`)。
* 经过严格的 Neuro-Symbolic 逻辑对比，发现当前物理环境并不满足 `too_dark` 的硬性指标，且玩手机不足以触发 `hazard` 紧急预案。
* **门控结果**: 触发 `gate_reason: "reject_all"`，全盘否决 VLM 的提议。

## 阶段 3：最终执行 (Execution)
* **输出动作 (Pred Action)**: `[{"type": "none", "param": {}}]`
* **结果**: 系统保持沉默。成功拦截了一次 False Activation（误触发），整个决策链路耗时仅 5.62 秒。

**总结**: 通过解耦“提议”与“授权”，ViLLA 在保留大模型泛化能力的同时，引入了决定论的安全下限。