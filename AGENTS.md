# legged-ovon

为足式机器人搭建 Open-Vocabulary Object Navigation（OVON）的 ROS2 仿真基线：在 Isaac Sim 里跑通「感知 → 语义定位 → 导航 → 闭环评测」整条链，产出可运行的系统和一份可复现的评测记录。

**核心主张：足式机器人做开放词汇目标导航，现在缺的是一条端到端、可复现的仿真评测闭环。本项目第一步是把「Isaac Sim + Nav2 + Grounding DINO + ROS2 action」这条链跑通并固定评测口径；之后任何假设（改感知、改规划、改本体控制）都只在这条基线上验证，用同一套指标和同一批失败样例比较。基线没跑通之前，不做任何「新方法」。**

目标：暂不锁定具体会议/比赛。2–3 个月内（≈ 2027 年 2 月中前）产出可运行的 ROS2 仿真系统 + 可复现评测记录，为后续比赛和论文选题提供依据。

---

## 你（Agent）每次进来先读什么

1. **本文件** —— 知道我们在做什么、每个目录是干什么的
2. **[handoff.md](handoff.md)** —— 上一个窗口做到哪了、下一步是什么
3. 要动实验就再读 [experiment/results.md](experiment/results.md) 和 [experiment/evaluation.md](experiment/evaluation.md)

**不要读完整个仓库再开始。** 上下文很贵，按需读。

---

## 目录

| 路径 | 是什么 | 什么时候看 |
|---|---|---|
| `related_work/` | 相关文献，每篇 `paper.pdf` + `source/` | 要引用、要对比方法时 |
| `复现/` | 重要 baseline 的复现，每个带一份复现报告 | 要确认 baseline 数字时 |
| `brainstorm.md` | 问题和假设是怎么聊出来的 | 想不通为什么这么设计时 |
| `experiment/` | 实验代码 + 每一版结果 | 跑实验 |
| `DataSet/` | 数据集，处理说明见 `dataset.md` | 要动数据时 |
| `handoff.md` | 进度交接 | **每次都读** |

---

## 读论文的规矩

`related_work/` 里每篇都是 `paper.pdf` + `source/`（LaTeX 源码），按要问什么选：

- 泛读（讲了什么、什么方法）→ `paper.pdf`
- 细查（表里的数、公式、引用）→ `source/*.tex`
- 看图 → 只能 `paper.pdf`，图不在源码里

用 `fetch-paper.sh` 抓的源码已清洗过（旧稿在 `source/.stale/`，注释已剥、原文存 `.orig`）。
手动下的记得自己清一遍。宏多的论文先读 `commands.tex` / `macros.tex` 这类文件。


---

## 硬规矩

1. **不要自己发明术语。**解释你在做什么的时候用论文里已有的词
   （Open-Vocabulary Object Navigation / OVON、Object Goal Navigation / ObjectNav、
   Success Rate / SR、Success weighted by Path Length / SPL、Distance to Goal / DTG、
   Isaac Sim / Isaac Lab、Nav2（behavior tree / planner / controller）、Grounding DINO、
   ROS2 action（navigate_to_pose 与自定义 NavigateToObject）、open-vocabulary detector / VLM），别造新词。
2. **改实验之前先说你要改什么、为什么。**不要直接动手跑。
3. **每版实验都要有名字。**命名规则见 `experiment/results.md`，不许出现 `test2` `final_v2_new`。
4. **跑完必须走标准化测评。**见 `experiment/evaluation.md`，不要临时挑指标。
5. **窗口快满了跟我说，我让你更新 handoff。**不要硬撑到被截断。

---

## 环境硬约束（重要）

Isaac Sim 只支持 **Linux（Ubuntu）+ NVIDIA GPU**，本机是 macOS（Darwin），跑不了仿真。
真正的开发/运行环境得是一台 Linux + NVIDIA GPU 的机器（实验室服务器或云 GPU）。
所有跑仿真、测指标的步骤默认在那边执行；本机只做写代码、写文档、抓文献、Git 管理。
