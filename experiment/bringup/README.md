# bringup：Go2 + Gazebo Fortress + Nav2 的可运行配置

归档仓库 `go2_gazebo_sim` 的 `go2_slam_launch.py` / `go2_nav_launch.py` 依赖不存在的
`go2_sdk` 包，无法直接运行。这里放我们自己补齐、验证过的配置。

```
bringup/
├── config/
│   ├── slam.yaml          # slam_toolbox，base_frame 改成 base_link
│   └── nav2_params.yaml   # Nav2（AMCL + DWB + Navfn），按 Go2 的尺寸/速度改过
├── launch/
│   └── go2_nav2.launch.py # 仿真 + Nav2 一键起
└── maps/
    └── maze.{pgm,yaml}    # maze_world.sdf 里 SLAM 建出来的地图（原地转一圈）
```

## 接入 ~/ros2_ws

```bash
ln -sfn <repo>/experiment/bringup/config ~/ros2_ws/config
ln -sfn <repo>/experiment/bringup/launch ~/ros2_ws/launch
ln -sfn <repo>/experiment/bringup/maps   ~/ros2_ws/maps
```

## 跑

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch ~/ros2_ws/launch/go2_nav2.launch.py
```

然后发目标：

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 1.0, y: -0.3, z: 0.0}, orientation: {w: 1.0}}}}" --feedback
```

## 和原仓库的差异（为什么不能直接用）

| 问题 | 处理 |
|---|---|
| `go2_slam_launch.py` / `go2_nav_launch.py` 引用 `go2_sdk`、`unitree_go2_launch.py`，两者都不在仓库里 | 用自包含的 `go2_launch.py` + 本目录 launch |
| CHAMP 只发 `odom → base_link`，没有 `base_footprint` | `slam.yaml` 与 `nav2_params.yaml` 的 `base_frame` 全部用 `base_link` |
| 原参数按轮式机器人给的速度/半径 | DWB 限速 0.2 m/s、0.8 rad/s；footprint 0.66×0.32m |
| `ros-humble-navigation2` 不含 `nav2_bringup` | 本目录 launch 逐个起 Nav2 节点，不依赖 bringup |

## 已知问题

- 接近目标时容易触发 `Failed to make progress`（CHAMP 低速 + 15s 进度检查），会走 recovery；
  第二次目标实测 `SUCCEEDED`，但近目标段拖得久。后续要调 progress checker / 目标容差。
- 地图只覆盖原地一圈（未知区域约 65%）。要跑正式 episode，得先沿路径建更完整的地图。
