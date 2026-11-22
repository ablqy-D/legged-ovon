# Handoff

> 每个窗口结束前更新这份。**下一个 Agent 只读 AGENTS.md + 这份就能接上。**
> 写给"完全不知道前情的人"看，不要用只有你懂的简称。
> 最后更新：2026-11-22 · 第 3 个窗口

---

## 一句话现状

**环境已装好并验证：Ubuntu 22.04 + ROS2 Humble + Gazebo Fortress + Nav2 + slam_toolbox，Go2 在 Gazebo 里能建图、能到点（`/navigate_to_pose` 返回 SUCCEEDED）。可运行配置在 `experiment/bringup/`。下一步：接开放词汇语义层（检测 → 3D 场景图 → grounding → Nav2 goal），再开始固定评测口径。**

---

## 已经确定不用再动的

- ✅ 项目方向：足式机器人 Open-Vocabulary Object Navigation 的 ROS2 仿真基线。
- ✅ **仿真栈（2026-11-22 两次评估后敲定）**：**Gazebo Fortress（gz-sim 6）** + `ros_gz_sim` + `gz_ros2_control` + Nav2 + 开放词汇检测（YOLO-World/YOLOE，Grounding DINO 留作后续消融）+ ROS2 action，跑在 Ubuntu 22.04 / ROS2 Humble 上。
- ✅ 为什么不用 Isaac Sim：3060 笔电 6GB VRAM，Isaac Sim 官方最低要 RTX 4080 16GB，8GB 笔记本卡带传感器都会冻死。Gazebo + Nav2 在 6GB 没问题。
- ✅ 为什么不用 Gazebo Classic 11：Classic 已于 2025-01 EOL；参考仓库 `go2_gazebo_sim` 当前 main 已迁到 `ros_gz_sim` + `gz_ros2_control`（Fortress），沿用 Classic 等于同时对抗 EOL 和参考代码，没必要。
- ✅ 参考代码库：
  - [go2-semantic-nav](https://github.com/yusufdxb/go2-semantic-nav) = 语义层蓝图（Go2 + Nav2 + YOLO-World/YOLOE 检测 + 3D 物体场景图 + CLIP 语言 grounding + `/semantic/ground_and_navigate` action → Nav2 goal）。Phase 1 已过 workstation eval。
  - [go2_gazebo_sim](https://github.com/OpenMind/go2_gazebo_sim) = 仿真环境（Go2 模型 + Nav2 + SLAM + LiDAR，Gazebo Fortress / ros_gz）。⚠️ 仓库已归档（README 指向 OpenMind/unitree-sdk，但该仓库当前不可访问），按现有 main 用。
- ✅ 4 篇已有论文定位 + 空白结论（详见 brainstorm.md「读文献的初步理解」）：目前没有「足式 + 开放词汇 + 标准 SR/SPL/DTG + Nav2」的现成组合，本项目补这个空。
- ✅ **环境 + 空场景闭环（2026-11-22 第 3 个窗口验证）**：
  - 工作区 `~/ros2_ws`，第三方仓库 `src/go2_gazebo_sim` @ `f490369`。
  - 控制器 `joint_states_controller` + `joint_group_effort_controller` 均 active；`/cmd_vel` 能驱动 `/odom` 变化。
  - 传感器：`/scan`、`/unitree_lidar/points`、`/rgb_image`（640×480@10Hz）、`/imu/data`、`/odom` 都有数据。
  - slam_toolbox 建成 168×169 @0.05m 地图并保存。
  - Nav2（AMCL + DWB + Navfn）目标 `(1.0,-0.3)`：1 次 recovery 后 `SUCCEEDED`。
  - **可运行配置在 `experiment/bringup/`**（`config/slam.yaml`、`config/nav2_params.yaml`、`launch/go2_nav2.launch.py`、`maps/maze.*`）；`~/ros2_ws/{config,launch,maps}` 已软链过去。
  - 复现报告：[`复现/go2_gazebo_sim/README.md`](复现/go2_gazebo_sim/README.md)。

## 正在做

- 🔄 下一步：接语义层（还没开始）
  - **下一步**：
    1. 先沿迷宫走廊走一圈，建一张覆盖更大的地图，再跑多目标到点到点测试（当前地图未知区域 65%）
    2. 调 Nav2 近目标行为：`Failed to make progress` 反复触发（CHAMP 低速 + 15s 进度检查 + 0.25m 容差），先固定一套稳定的参数
    3. 接语义层：Gazebo RGB-D → 开放词汇检测（YOLO-World/YOLOE）→ 3D 场景图 → 语言 grounding → `/navigate_to_pose`
    4. 语义层跑通后再定 `experiment/evaluation.md` 的 episode 集与 SR/SPL/DTG

## 还没动

- ⬜ 覆盖更大区域的 SLAM 地图 / 多目标到点测试
- ⬜ 开放词汇检测 + 3D 场景图 + grounding
- ⬜ v1/v2/v3 正式实验与标准化测评
- ⬜ 提假设 / 进 brainstorm（规矩：复现在提假设之前）

---

## 踩过的坑，别再踩

1. **VLFM 的 arXiv ID 容易记错** —— 正确是 2312.03275，不是 2312.07500。
2. **fetch-paper.sh 末尾 `[ "$NMACRO" -gt 80 ] && ...` 在宏数少时返回 1** —— 文件其实都下好了，别被 exit code 1 骗了。
3. **Isaac Sim 有硬门槛** —— 6GB 笔电跑不了，别再往 Isaac Sim 上投入。
4. **go2_gazebo_sim 已不是 Classic 项目** —— 它现在依赖 `ros_gz_sim` + `gz_ros2_control`（Fortress）。照旧文档装 Classic 会在编译/launch 阶段直接对不上。
5. **仓库里的 `go2_slam_launch.py` / `go2_nav_launch.py` 不能直接用** —— 它们引用 `go2_sdk` 包和 `unitree_go2_launch.py`，两者都不在归档仓库里（原本属于已不可访问的 unitree-sdk）。用自包含的 `go2_launch.py` + `experiment/bringup/`。
6. **没有 `base_footprint`** —— CHAMP 发的是 `odom → base_link`。slam_toolbox 默认等 `base_footprint`，不改会刷 `Failed to compute odom pose`；AMCL 同理。
7. **`ros-humble-navigation2` 不含 `nav2_bringup`** —— 但本仓库逐个起 Nav2 节点，不需要它。
8. **近目标处 Nav2 会反复 `Failed to make progress`** —— 足式低速 + 15s 进度检查 + 0.25m 目标容差。目前靠 recovery 能成功，但慢；后续专门调。

---

## 给下一个窗口的第一句话

> 读 `AGENTS.md` 和本文件。去 `legged-ovon/` 目录。环境已就绪：Ubuntu 22.04 + ROS2 Humble + Gazebo Fortress + Nav2 + slam_toolbox，工作区 `~/ros2_ws`，可运行配置在 `experiment/bringup/`，复现报告在 `复现/go2_gazebo_sim/README.md`。下一步**不要**重装环境，直接做：先建一张覆盖更大的地图 + 多目标到点测试并调稳参数，然后接 go2-semantic-nav 的语义层（检测 → 3D 场景图 → grounding → `/navigate_to_pose`）。**不要**先写新方法，先复现。写完更新本文件。
