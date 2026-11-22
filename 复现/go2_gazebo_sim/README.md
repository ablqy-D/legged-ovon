# go2_gazebo_sim 复现报告

## 1. 复现的是什么

- 仓库：[OpenMind/go2_gazebo_sim](https://github.com/OpenMind/go2_gazebo_sim)
- commit：`f490369de120a65a8b046c4bb6fcb17a4add1797`（2025-12-01，仓库已归档）
- 内容：Unitree Go2 的 Gazebo Fortress 仿真（CHAMP 步态 + gz_ros2_control + Nav2 / slam_toolbox 配置）

## 2. 环境

| 项 | 值 |
|---|---|
| OS | Ubuntu 22.04.5 |
| ROS | Humble（desktop 已预装） |
| 仿真 | Gazebo Fortress / `ign gazebo` 6.18.0 |
| 关键包 | `ros-humble-ros-gz`、`ros-humble-gz-ros2-control`、`ros-humble-navigation2`、`ros-humble-slam-toolbox`、`ignition-fortress` |
| GPU | RTX 3060 Laptop 6GB（跑得动；日志有 `libEGL ... dri2 screen` 警告，但相机/激光都能出数） |

## 3. 复现步骤

```bash
# 1) 依赖
sudo apt-get install -y ros-humble-navigation2 ros-humble-slam-toolbox \
  ros-humble-ros-gz ros-humble-gz-ros2-control ros-humble-ros2-control \
  ros-humble-ros2-controllers ros-humble-effort-controllers \
  ros-humble-joint-state-publisher ros-humble-joint-state-publisher-gui \
  ros-humble-xacro ignition-fortress
sudo rosdep init && rosdep update

# 2) 工作区
mkdir -p ~/ros2_ws/src
git clone https://github.com/OpenMind/go2_gazebo_sim.git ~/ros2_ws/src/go2_gazebo_sim
rosdep install --from-paths ~/ros2_ws/src --ignore-src -r -y
cd ~/ros2_ws && colcon build --symlink-install

# 3) 启动仿真（rviz 由外部另开）
source install/setup.bash
ros2 launch go2_gazebo_sim go2_launch.py rviz:=false publish_map_tf:=false
```

验证点：

- `/scan`（LaserScan，frame `velodyne`）、`/unitree_lidar/points`、`/rgb_image`（640×480@10Hz）、`/odom`、`/joint_states` 都有数据
- `ros2 control list_controllers` 两个控制器均为 active：
  `joint_states_controller`、`joint_group_effort_controller`
- 发布 `/cmd_vel` 前进 2 秒，`/odom` x 从 ≈ -0.046 变到 ≈ +0.176

## 4. 结果

| 项 | 结果 |
|---|---|
| 仿真 + CHAMP 站立/行走 | ✅ |
| slam_toolbox 在线建图 | ✅（原地转一圈后 `/map` 168×169 @ 0.05m） |
| `map_saver_cli` 保存地图 | ✅ `experiment/bringup/maps/maze.{pgm,yaml}` |
| Nav2（AMCL + DWB + Navfn）到点 | ✅ 目标 `(1.0, -0.3)`，1 次 recovery 后 `SUCCEEDED`；近目标段很慢，第一次 180s 客户端超时 |

## 5. 和仓库 README 的差异（重要）

1. **`go2_slam_launch.py` / `go2_nav_launch.py` 不能直接用。**
   它们引用了 `go2_sdk` 包和 `unitree_go2_launch.py`，两者都不在仓库里——仓库原本是
   `unitree-sdk` 的子模块，而 `OpenMind/unitree-sdk` 现在不可访问。可用的自包含入口是
   `go2_launch.py`。
2. **SLAM 默认 `base_frame: base_footprint`，但这套 CHAMP 不发 `base_footprint`。**
   TF 树是 `map → odom → base_link → trunk/...`。不改参数会刷
   `Failed to compute odom pose`。改 `base_frame: base_link` 后正常。
   本仓库的改法：`~/ros2_ws/config/slam.yaml`。
3. **`ros-humble-navigation2` 不会装 `nav2_bringup`**，但这个仓库自己逐个起 Nav2 节点，不需要它。
4. 话题名：相机是 `/rgb_image`，不是 `/camera/color/image_raw`；激光 2D 是 `/scan`，3D 是 `/unitree_lidar/points`。
   后面接 go2-semantic-nav 时要做话题映射。
5. `ign gazebo` 启动时会出现 `libEGL warning: egl: failed to create dri2 screen`，但传感器仍正常出数；不要被这条警告误导。

## 6. 自写配置和运行方式

原仓库的 `go2_slam_launch.py` / `go2_nav_launch.py` 不能用，我们补的配置在
[`experiment/bringup/`](../../experiment/bringup/README.md)：

```bash
source /opt/ros/humble/setup.bash && source ~/ros2_ws/install/setup.bash
ros2 launch ~/ros2_ws/launch/go2_nav2.launch.py
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 1.0, y: -0.3, z: 0.0}, orientation: {w: 1.0}}}}" --feedback
```

`~/ros2_ws/{config,launch,maps}` 已软链到 `experiment/bringup/` 对应目录，避免两份配置漂移。

## 7. 下一步

- 建一张覆盖更大区域的地图（沿走廊走一圈），再做多目标到点测试
- 调 progress checker / 目标容差，减少近目标处的 recovery
- 接语义层：RGB-D → 开放词汇检测 → 3D 场景图 → grounding → Nav2 goal
