# DataSet

> 每个数据集下完立刻补一段。**Agent 靠这份判断能不能直接用，别让它自己猜目录结构。**
> 本项目的数据主要是**仿真场景资产 + 目标导航 episode 集**，不是训练集。

## 总览

| 数据集 | 用途 | 状态 | 大小 |
|---|---|---|---|
| Gazebo Fortress 室内场景资产（`.sdf` world + 模型） | 仿真环境 | ⬜ 待用 go2_gazebo_sim 自带 world 验证 | |
| RGB-D 相机话题（Gazebo 传感器 → ROS） | 开放词汇检测输入 | ⬜ 未接 | |
| 目标导航 episode 集（场景 + 目标类别 + 起止位姿） | 评测用 | ⬜ 未定 | |

## Gazebo Fortress 场景

**目录结构**：`go2_gazebo_sim` 自带 `go2_description/worlds/{default,maze_world,walled_world}.sdf`，先用 `maze_world.sdf` 验证链路；后续自建室内场景放 `DataSet/worlds/`。

**处理过程**：待定。world 是 SDF 文本，体积小的话可以进 Git。

**⚠️ 坑**：Gazebo Classic 的 `.world` 与 Fortress 的 `.sdf` 不通用，资产必须是 Fortress 格式；模型库（Fuel）首次运行会联网下载，离线环境要提前拉。

## 目标导航 episode 集

（下完/生成后填：场景、目标类别词表、起始位姿、目标位姿、成功阈值）

## split

```
train: （若走 ObjectNav 惯例：训练场景 / 可见场景）
test:  （评测场景 / 未见场景）
```

**按 scene 分，不按 episode 分。**理由：ObjectNav 的核心泛化目标是「没见过的场景」，按 episode/样本分会泄漏——同一个场景的不同 episode 混进测试，等于让模型见过这间屋子了。

## 下数据的两个命令

```bash
caffeinate -i          # Mac 不休眠，否则合盖/息屏就断连（本机下文献用）
```

```
/loop 下载 {{X}} 到 {{Y}}，停止条件是校验通过，断了自动续传
```
