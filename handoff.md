# Handoff

> 每个窗口结束前更新这份。**下一个 Agent 只读 AGENTS.md + 这份就能接上。**
> 写给"完全不知道前情的人"看，不要用只有你懂的简称。
> 最后更新：2026-11-22 · 第 2 个窗口

---

## 一句话现状

**方向已定：仿真改用 Gazebo（不用 Isaac Sim），语义层参考 go2-semantic-nav。文献齐了（4 篇已有 + 6 篇补抓，理解见 brainstorm.md）。下一步在 3060 笔电上装 ROS2 Humble + Gazebo + Nav2，跑通 Go2 的 SLAM+Nav2 空场景闭环。**

---

## 已经确定不用再动的

- ✅ 项目方向：足式机器人 Open-Vocabulary Object Navigation 的 ROS2 仿真基线。
- ✅ **仿真栈（2026-11-22 重新评估后敲定）**：Gazebo Classic 11 + Nav2 + 开放词汇检测（YOLO-World/YOLOE，Grounding DINO 留作后续消融）+ ROS2 action，跑在 Ubuntu 22.04 / ROS2 Humble 上。
- ✅ 为什么不用 Isaac Sim：3060 笔电 6GB VRAM，Isaac Sim 官方最低要 RTX 4080 16GB，8GB 笔记本卡带传感器都会冻死。Gazebo+Nav2 在 6GB 没问题。
- ✅ 参考代码库：
  - [go2-semantic-nav](https://github.com/yusufdxb/go2-semantic-nav) = 语义层蓝图（Go2 + Nav2 + YOLO-World/YOLOE 检测 + 3D 物体场景图 + CLIP 语言 grounding + `/semantic/ground_and_navigate` action → Nav2 goal）。Phase 1 已过 workstation eval。
  - [go2_gazebo_sim](https://github.com/OpenMind/go2_gazebo_sim) = 仿真环境（Go2 模型 + Nav2 + SLAM + LiDAR，Gazebo Classic）。
- ✅ 4 篇已有论文定位 + 空白结论（详见 brainstorm.md「读文献的初步理解」）：目前没有「足式 + 开放词汇 + 标准 SR/SPL/DTG + Nav2」的现成组合，本项目补这个空。

## 正在做

- 🔄 装环境（下一步开始，在 3060 笔电上）
  - **下一步**：
    1. 3060 笔电装 ROS2 Humble + Gazebo Classic 11 + Nav2 + slam_toolbox
    2. clone go2_gazebo_sim，跑通 Go2 的建图 + Nav2 导航空场景闭环（验证链路，不叠语义）
    3. 再 clone go2-semantic-nav，把它的语义层（检测 + 场景图 + grounding + action）接进来

## 还没动

- ⬜ 环境搭建（下一步开始）
- ⬜ 复现 baseline（先跑通空场景闭环，再叠语义层）
- ⬜ 提假设 / 进 brainstorm（规矩：复现在提假设之前）

---

## 踩过的坑，别再踩

1. **VLFM 的 arXiv ID 容易记错** —— 正确是 2312.03275，不是 2312.07500。
2. **fetch-paper.sh 末尾 `[ "$NMACRO" -gt 80 ] && ...` 在宏数少时返回 1** —— 文件其实都下好了，别被 exit code 1 骗了。
3. **Isaac Sim 有硬门槛** —— 6GB 笔电跑不了，别再往 Isaac Sim 上投入。

---

## 给下一个窗口的第一句话

> 读 `AGENTS.md` 和本文件。去 `legged-ovon/` 目录。仿真用 Gazebo Classic 11 + Nav2（不是 Isaac Sim），语义层参考 go2-semantic-nav。下一步：在 3060 笔电（Ubuntu 22.04）装 ROS2 Humble + Gazebo + Nav2，clone go2_gazebo_sim 跑通 Go2 建图+导航空场景闭环，再叠 go2-semantic-nav 语义层。**不要**先写新方法，先复现。写完更新本文件。
