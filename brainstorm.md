# Brainstorm

> 问题和假设是怎么聊出来的。**不是 Agent 直接给的，是来回聊出来的。**
> **倒序写，最新的在最上面。**被自己否掉的想法也留着——那是写 motivation 的素材。

---

## 2026-11-22 · 仿真栈重新评估：Isaac Sim → Gazebo Fortress

**背景：** 11-18 定的是 Isaac Sim，本机核查后发现 3060 笔电只有 6GB VRAM，Isaac Sim 官方最低要 16GB，带传感器直接崩。于是改 Gazebo。

**第一次评估**落在 Gazebo Classic 11，理由是「够轻」。但实际去看参考仓库 [go2_gazebo_sim](https://github.com/OpenMind/go2_gazebo_sim) 时发现：
- 仓库 2025-12 已归档；
- 当前 main 的 `package.xml` 依赖 `ros_gz_sim` + `gz_ros2_control` + `libignition-gazebo6`，即 **Gazebo Fortress（gz-sim 6）**，不是 Classic；
- Gazebo Classic 已于 2025-01 EOL。

**→ 结论：仿真栈定为 Gazebo Fortress。** 理由：Ubuntu 22.04 + Humble 官方配对就是 Fortress；参考仓库开箱即用；不再同时对抗 EOL 软件和参考代码。代价是 handoff 里「Classic 11」的表述要同步改掉。

**对下面 11-18 文献结论的影响：** 「足式 + 开放词汇 + 标准 SR/SPL/DTG + Nav2」的空白判断仍然成立；只是本项目的仿真底座从 Isaac Sim 换成 Fortress，和 Path planning 那篇的 Isaac Sim 基础设施不再同栈。这不影响方法层面的对比。

**留下的教训：** 定仿真栈之前先看参考仓库当前的依赖，不要只看仓库名和 README 标题。

---

## 2026-11-18 · 读文献的初步理解（4 篇已有 + 定下补抓方向）

**已读的 4 篇，各自定位：**

- **LOVON（Peng 2025）**：最贴题的「足式 + 开放词汇」prior，但它是**反应式跟踪**，不是地图语义导航——LLM（DeepSeek R1）拆任务 + YOLO-11 检测 + 小 transformer（L2MM）直接输出速度 [vx,vy,θ]。没有 Nav2、没有地图、没有 SR/SPL，在 Gym-Unreal 视觉跟踪 benchmark 上评 EL/SR。关键 trick：**Laplacian 方差滤波丢运动模糊帧**（足式抖动）。
- **3DGSNav（Zheng 2026）**：ZSON 用 3DGS 当 VLM 记忆 + 主动感知 + frontier 自由视角渲染。标准 ObjectNav 评测（Habitat HM3D/MP3D，SR/SPL）。**真机就是 Go2 四足 + ROS2 + Nav2 + RGB-D（D455）+ 开放词汇检测（YOLOE）+ 足式里程计**——和我们 stack 几乎一致，只是它用 3DGS+VLM 而不是 Grounding DINO + 语义地图。
- **DLOV-3D（Zheng 2025 IROS）**：开放词汇 3D 场景表示（LSeg 像素级 + CLIP 图像级融合），用 Grounding DINO 做 revalidation，LLM 做多实例导航。标准 SR/SPL（RoboTHOR+Habitat）。轮式 LoCoBot。
- **Path planning（Zhang 2025 ICoIAS）**：Unitree Go2 + YOLOv8 + A*/JPS + B-Spline，ROS2 + Isaac Sim 协同仿真。只做避障，不是语义导航。给了具体 ROS2↔Isaac Sim 桥接细节（订阅 /<robot>/front_cam/color_image、/depth_image、/odom，发 /<robot>/cmd_vel）。

**从这里看出的空白（也是核心主张的依据）：**

目前没有工作同时做到「足式 + 开放词汇目标导航 + 标准 SR/SPL/DTG 评测 + Isaac Sim + Nav2」：
- LOVON 有足式+开放词汇，但反应式、无地图、无标准指标。
- 3DGSNav 有开放词汇+标准指标+Nav2-on-四足，但 sim 用 Habitat 不是 Isaac Sim，且 3DGS+VLM 很重。
- Path planning 有 Isaac Sim+ROS2 基础设施，但只避障、无语义目标。

→ 本项目基线正好补这个空：模块化 Nav2 + Grounding DINO + 语义地图，在 Isaac Sim 里，用标准 SR/SPL/DTG 评一个足式机器人。

**一个实践细节（来自 Path planning 那篇）**：Isaac Sim↔ROS2 用 `ros2 bridge.py`；四足模型从厂商 URDF 导入，SDK 的关节/电机名要对齐 URDF；订阅 topic 是 /<robot>/front_cam/color_image、/depth_image、/odom，控制发 /<robot>/cmd_vel。

---

## 2026-11-18 · 开坑：定方向

**我：** 开个新坑，做足式机器人开放词汇语义导航的仿真基线。目标 2–3 个月产出可运行 ROS2 仿真系统 + 可复现评测记录，为后续比赛和论文选方向做准备。

**Agent：** 方向清晰，但有一个环境硬约束要先摆出来：本机是 macOS，Isaac Sim 只支持 Linux + NVIDIA GPU，仿真得在另一台机器上跑。另外按科研工作流的规矩，**复现在提假设之前**——先把 baseline 链跑通、固定评测口径，再谈新方法。

**→ 结论：项目第一步是「跑通闭环 + 固定评测」，不是「想新方法」。这个约束（仿真必须在 Linux+GPU 上跑）直接决定了后面的分工：本机写代码/文档/文献，服务器跑仿真/测指标。**

---

## 2026-11-18 · 从复现里看出来的东西

（待填——复现跑起来之后，把论文里读不出来的现象记在这里）

---

## 待想清楚

- ⬜ 足式本体在 Isaac Sim 里用哪套：Isaac Lab 的 legged 模板（自带四足，省去控制器调试）vs. 自己 import URDF + 自写 MPC/步态控制器。前者快但可能和真实足式平台有差距；后者可控但前期重。
- ⬜ Grounding DINO 在足式机器人上怎么接：相机 RGB 做开放词汇检测 vs. 用现成语义分割；要不要加深度图做 3D 定位。
- ⬜ 评测口径：足式机器人的「成功」判定（到达距离阈值）和轮式 ObjectNav 是否要区分——腿的步态会让「停在目标 1m 内」更难，阈值要不要放宽。
