# Handoff

> 每个窗口结束前更新这份。**下一个 Agent 只读 AGENTS.md + 这份就能接上。**
> 写给"完全不知道前情的人"看，不要用只有你懂的简称。
> 最后更新：2026-11-18 · 第 1 个窗口

---

## 一句话现状

**项目刚建骨架，什么都没跑。现在停在「定技术方案 + 抓文献」这一步，还没碰环境。**

---

## 已经确定不用再动的

- ✅ 项目方向定死了：足式机器人 Open-Vocabulary Object Navigation 的 ROS2 仿真基线（Isaac Sim + Nav2 + Grounding DINO + ROS2 action）。
- ✅ 目标：2–3 个月内产出可运行仿真系统 + 可复现评测记录，暂不锁定具体会议/比赛。
- ✅ 环境硬约束确认过：本机是 macOS，跑不了 Isaac Sim；仿真得在 Linux + NVIDIA GPU 的机器上跑。

## 正在做

- 🔄 定技术方案 + 抓文献（还没开始，下一步就是这两件）
  - 已排除：无
  - 待验证：足式本体在 Isaac Sim 里到底用哪套（Isaac Lab 的 legged 模板 / 直接 import URDF + 自写控制器）；Grounding DINO 是跑在相机 RGB 上还是用语义分割的分支。
  - **下一步**：
    1. 抓文献（见「给下一个窗口的第一句话」里的列表）
    2. 确认 Linux + GPU 机器是否可用、Isaac Sim 装哪个版本
    3. 在相关文献里挑 2–3 篇有开源代码的，跑通并写 `复现/<方法>/复现报告.md`

## 还没动

- ⬜ 环境搭建（等确认有 Linux + GPU 机器再做，本机做不了）
- ⬜ 复现 baseline（先读完文献、定好要复现哪几篇再动手）
- ⬜ 提假设 / 进 brainstorm（规矩：**复现在提假设之前**，先跑通 baseline 再说）

---

## 踩过的坑，别再踩

1. （暂无，项目刚开始）

---

## 给下一个窗口的第一句话

> 读 `AGENTS.md` 和本文件。去 `legged-ovon/` 目录。现在做两件事：(1) 用 `fetch-paper.sh` 抓这几类文献——OVON/ObjectNav 的 Habitat 基准（SR/SPL 指标定义）、Isaac Lab 的足式导航模板、Nav2 在仿真里的行为树/action 用法、Grounding DINO 做 open-vocabulary 检测的官方实现；(2) 确认 Linux+GPU 机器和 Isaac Sim 版本。**不要**现在就开始写新方法、也不要碰 brainstorm——先复现。写完更新本文件。
