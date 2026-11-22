# ROS2 基础笔记 01：看懂节点与话题

> 日期：2026-11-22 / 2026-11-23
> 场景：Gazebo Fortress + Go2（CHAMP）+ teleop 已跑通，可随时 `ros2 node list` / `ros2 topic list -t`。
> 目的：不是背概念，而是能从「节点表 + 话题表」还原出整个系统的数据流。

---

## 0. 看任何 ROS2 系统，只问四个问题

不要从「这个包是干嘛的」开始，从数据流开始：

1. **谁发指令？**（通常是 `/cmd_vel`）
2. **谁执行指令？**（控制器、执行器）
3. **谁提供状态？**（传感器、里程计）
4. **谁把它们统一到同一个坐标系？**（TF）

剩下的节点，绝大多数都是这四件事的某一环。当前这套系统正好可以完整走一遍这四问。

---

## 1. 13 个节点，其实是 5 组

| 组 | 节点 | 一句话职责 | 要不要管 |
|---|---|---|---|
| **A. 仿真底座** | `/gz_ros2_control`、`/controller_manager` | `gz_ros2_control` 是跑在 Gazebo 进程里的插件，它提供 `controller_manager`；后者负责加载/启动/停止控制器 | 基本不用管，但要会 `ros2 control list_controllers` |
| **B. 控制器** | `/joint_states_controller`、`/joint_group_effort_controller` | 前者把 Gazebo 的关节状态读出来发成 `/joint_states`；后者接收「关节轨迹」并转成**力矩**指令写给 Gazebo | 要懂它俩的输入输出 |
| **C. 步态层（CHAMP）** | `/quadruped_controller_node`、`/state_estimation_node` | 前者把 `/cmd_vel` 变成 12 条腿的关节轨迹（trot 步态）；后者想用 IMU + 足端接触估计机体位姿 | 前者是核心，后者目前半残（见第 5 节） |
| **D. 模型与坐标系** | `/robot_state_publisher`、`/map_to_odom_tf_node`、`/base_footprint_to_base_link_tf_node` | 第一个把 URDF 的固定连接 + 关节角算成 TF；后两个就是两个 `static_transform_publisher`，各发一条固定变换 | **TF 是重点** |
| **E. 桥和人机接口** | `/gazebo_bridge`、`/teleop_twist_keyboard`、`/rviz2` | 桥负责 Gazebo ↔ ROS2 的翻译；键盘发 Twist；RViz 只看不控 | 桥的规则要懂 |

> `/transform_listener_impl_57047f673230` **不是节点**，是某个节点（多半是 RViz）内部创建的 TF 监听器，被 `node list` 顺带列出来了。看到这种名字直接忽略。

### 顺带记住：`controller_manager` 的生命周期

`controller_manager` 不产生数据，它只做生命周期管理：

```
unconfigured → inactive → active
```

只有 `active` 的控制器才会真的收发数据。启动后头 20~30 秒控制器「没上线」是正常的，不是坏了。

---

## 2. 主线：按一个 `w`，机器为什么会走

```
teleop_twist_keyboard
      │ /cmd_vel            geometry_msgs/msg/Twist  (linear.x, angular.z)
      ▼
quadruped_controller_node  ── 查步态表，算出 12 个关节在接下来一小段时间里的角度
      │ /joint_group_effort_controller/joint_trajectory   trajectory_msgs/msg/JointTrajectory
      ▼
joint_group_effort_controller  ── 按时间点插值，算成力矩
      │ （ros2_control 内部接口，不是话题）
      ▼
gz_ros2_control  →  Gazebo 里 12 个关节施加力矩  →  腿动，身体动
      │
      ▼
gazebo_bridge 把 Gazebo 的真实状态翻译回 ROS2：
    /odom（位姿+速度）  /joint_states（关节角）  /clock（仿真时间）
```

三个关键理解点：

- **Twist 只有两个有效字段**：`linear.x`（前进速度）和 `angular.z`（转向角速度）。四足不用 `linear.y/z`，因为 CHAMP 不做横移、不做爬升。
- **为什么中间要绕一层「轨迹」而不是直接给速度？** 腿是位置/力矩控制的，没有「轮子转速」这个东西。`/cmd_vel` 是**意图**，`JointTrajectory` 是**具体动作**，中间必须有步态生成器翻译。
- **CHAMP 的输入输出**（用 `ros2 node info` 验证过）：
  - `quadruped_controller_node` 订阅 `/cmd_vel`、`/body_pose`、`/clock`，发布 `/joint_group_effort_controller/joint_trajectory`。
  - `joint_group_effort_controller` 订阅这条轨迹话题，发布 `controller_state` / `state`。

---

## 3. TF：这条链最重要的一节

TF 回答一个问题：**「A 坐标系里的一个点，在 B 坐标系里是哪儿？」**

系统里有 4 层坐标系，各管一段：

| 坐标系 | 谁维护 | 特点 |
|---|---|---|
| `map` | SLAM 或 AMCL | 全局固定，不漂，但**会跳**（重定位时整体修正） |
| `odom` | 里程计 | 连续平滑，但**会漂**（走久了累积误差） |
| `base_link` | 机器人本体 | 原点在机身 |
| `trunk` / `camera_link` / `velodyne` … | `robot_state_publisher` | 传感器装在哪，由 URDF 决定 |

**为什么非要拆成 map → odom → base_link 三段？**
「不漂」和「连续」不能同时保证。里程计连续，所以能算速度，但会漂；地图不漂，但修正时只能整体跳一下。拆开之后，跳变只发生在 `map→odom` 这一段，`odom→base_link` 始终保持连续——控制器就不会因为一次重定位而算出疯狂的速度。这是导航系统的通用设计，不是 Go2 特有。

### 实际 TF 树（`ros2 run tf2_tools view_frames` 生成）

```
map ──(static, 单位阵)── odom ──(50Hz, Gazebo 真值)── base_link
                                                        ├── trunk ── 12 条腿 / camera_link / imu_link
                                                        ├── lidar_l1_link
                                                        └── velodyne_base_link ── velodyne
```

两个必须记住的点：

1. **`map→odom` 现在是写死的单位阵**，来自 `map_to_odom_tf_node`（默认 `publish_map_tf:=true`）。它只是占位符。一旦起 SLAM 或 AMCL，**必须**关掉它（`publish_map_tf:=false`），否则两个节点抢着发 `map→odom`，机器人在图上会抖。
   → 规矩：**一个变换只能有一个发布者。**
2. **`base_footprint` 不在树里**，尽管 `/base_footprint_to_base_link_tf_node` 确实在发它。原因：TF 规定**一个坐标系只能有一个父节点**。`gazebo_bridge` 说「我是 `base_link` 的父节点（odom）」，`base_footprint_to_base_link_tf_node` 也说「我是 `base_link` 的父节点」，TF2 只认了一个，`base_footprint` 就成了孤儿。
   → 这正是当初 slam_toolbox 报 `Failed to compute odom pose` 的根本原因——它要找 `base_footprint`，而那个坐标系根本没进树。
   → 记住：**TF 是一棵树，不是一张图。一个 frame 只能有一个 parent。**

---

## 4. 31 个话题，按数据流分 7 类

| 类别 | 话题 | 说明 |
|---|---|---|
| **时间** | `/clock` | Gazebo 的仿真时间。所有节点设 `use_sim_time:=true` 后都听它，这是让 Nav2/CHAMP 时间一致的唯一办法 |
| **指令** | `/cmd_vel`、`/joint_group_effort_controller/joint_trajectory` | 意图 → 具体动作 |
| **关节状态** | `/joint_states`、`/dynamic_joint_states`、`/joint_group_effort_controller/{state,controller_state}` | 12 个关节的角度/速度/力矩 |
| **位姿/里程计** | `/odom`、`/odom/raw`、`/body_pose`、`/foot_contacts`、`/base_to_footprint_pose`、`/foot` | 见第 5 节的三个怪现象 |
| **传感器** | `/scan`（2D 激光）、`/unitree_lidar/points`、`/velodyne_points/points`、`/rgb_image`、`/imu/data` | 语义层以后主要吃 `/rgb_image`，导航吃 `/scan` |
| **坐标系** | `/tf`（动态）、`/tf_static`（静态） | 动态的每帧都变（关节、odom），静态的发一次就锁存 |
| **RViz 按钮 / 系统** | `/goal_pose`、`/initialpose`、`/clicked_point`、`/robot_description`、`/rosout`、`/parameter_events`、controller 的 `transition_event` | 前三个是「在 RViz 里点一下」产生的话题，现在没人订阅；`/initialpose` 以后给 AMCL 设初始位姿用 |

### 现在就该认识的 4 个消息类型

```bash
ros2 interface show geometry_msgs/msg/Twist       # 速度指令
ros2 interface show sensor_msgs/msg/JointState    # 关节状态
ros2 interface show nav_msgs/msg/Odometry         # 里程计
ros2 interface show sensor_msgs/msg/LaserScan     # 2D 激光
```

其余用到再查。

---

## 5. 三个「看着奇怪但其实正常」的现象

这三个现象最能检验有没有真看懂：

### ① `/odom/raw` 有发布者，没订阅者

`state_estimation_node` 自己算了一份里程计，但没人用。因为这套仿真里 `/odom` 直接取自 Gazebo 的**真值**（`gazebo_bridge` 发的）。真值不漂，谁还要估的？所以 CHAMP 的估计算法在这套配置里被架空了。
→ **提醒：仿真里的「完美里程计」是免费午餐，真机上没有。**

### ② `/body_pose` 和 `/foot_contacts` 有订阅者，没发布者

`quadruped_controller_node` 想根据机体姿态做地形适应，`state_estimation_node` 想根据足端接触判断哪条腿着地——但这套 Gazebo 配置**没接**这两个输入。所以步态是「开环」跑的，状态估计也基本没输出（这也是为什么 `/odom/raw` 和 `/tf` 上没有东西）。
→ 以后要上楼梯、走崎岖地形，这两个输入必须补。

### ③ `/scan`、`/rgb_image`、`/odom`、`/tf` 的发布者和订阅者都是 `gazebo_bridge` 自己

因为 `ros_gz_bridge` 用了 `@`（双向）配置。对传感器来说这是错的，应该用 `[`（只 GZ→ROS）。现在没炸，是因为 Gazebo 那头没人听 ROS 发回去的激光，但这是个**埋着的回环隐患**，接语义层时一定要改成单向。

`ros_gz_bridge` 的方向符号：

| 符号 | 方向 |
|---|---|
| `@` | 双向（ROS ↔ GZ） |
| `[` | GZ → ROS（传感器应该用这个） |
| `]` | ROS → GZ（`/cmd_vel` 应该用这个） |

---

## 6. 练习命令（仿真 + teleop 开着）

```bash
ros2 node info /quadruped_controller_node
ros2 interface show geometry_msgs/msg/Twist
ros2 interface show trajectory_msgs/msg/JointTrajectory
ros2 interface show sensor_msgs/msg/JointState
ros2 topic hz /joint_states /scan /odom      # 各看几秒，Ctrl-C 停
ros2 topic echo /joint_states --once
ros2 run tf2_tools view_frames               # 在当前目录生成 frames_*.pdf
```

---

## 7. 六个问题（自己回答，写在下面）

1. 按住 `w` 两秒，从 `/cmd_vel` 到 `/odom` 的数值变化，中间经过了哪 4 个节点、哪 2 个话题？

   **答：**

2. `/odom` 的 `header.frame_id` 和 `child_frame_id` 分别是什么？为什么必须是这两个，不能反过来？

   **答：**

3. `/scan` 的 `header.frame_id` 是 `velodyne`，但 Nav2 要的是机器人本体附近的障碍物。**TF 在这中间起了什么作用？**（提示：`/scan` 本身不带「机器人在哪」的信息）

   **答：**

4. `/joint_states` 里有几个关节？Go2 四条腿一共该有几个自由度？对得上吗？

   **答：**

5. `/clock` 是谁发的？如果某个节点忘了设 `use_sim_time:=true`，会出现什么现象？

   **答：**

6. `view_frames` 生成的树的**根节点**是哪个？为什么是它而不是 `base_link`？

   **答：**

---

## 附录 A：原始节点列表

```text
ros2 node list
/base_footprint_to_base_link_tf_node
/controller_manager
/gazebo_bridge
/gz_ros2_control
/joint_group_effort_controller
/joint_states_controller
/map_to_odom_tf_node
/quadruped_controller_node
/robot_state_publisher
/rviz2
/state_estimation_node
/teleop_twist_keyboard
/transform_listener_impl_57047f673230
```

## 附录 B：原始话题列表

```text
ros2 topic list -t
/base_to_footprint_pose [geometry_msgs/msg/PoseWithCovarianceStamped]
/body_pose [geometry_msgs/msg/Pose]
/clicked_point [geometry_msgs/msg/PointStamped]
/clock [rosgraph_msgs/msg/Clock]
/cmd_vel [geometry_msgs/msg/Twist]
/dynamic_joint_states [control_msgs/msg/DynamicJointState]
/foot [visualization_msgs/msg/MarkerArray]
/foot_contacts [champ_msgs/msg/ContactsStamped]
/goal_pose [geometry_msgs/msg/PoseStamped]
/imu/data [sensor_msgs/msg/Imu]
/initialpose [geometry_msgs/msg/PoseWithCovarianceStamped]
/joint_group_effort_controller/controller_state [control_msgs/msg/JointTrajectoryControllerState]
/joint_group_effort_controller/joint_trajectory [trajectory_msgs/msg/JointTrajectory]
/joint_group_effort_controller/state [control_msgs/msg/JointTrajectoryControllerState]
/joint_group_effort_controller/transition_event [lifecycle_msgs/msg/TransitionEvent]
/joint_states [sensor_msgs/msg/JointState]
/joint_states_controller/transition_event [lifecycle_msgs/msg/TransitionEvent]
/odom [nav_msgs/msg/Odometry]
/odom/raw [nav_msgs/msg/Odometry]
/parameter_events [rcl_interfaces/msg/ParameterEvent]
/rgb_image [sensor_msgs/msg/Image]
/robot_description [std_msgs/msg/String]
/rosout [rcl_interfaces/msg/Log]
/scan [sensor_msgs/msg/LaserScan]
/tf [tf2_msgs/msg/TFMessage]
/tf_static [tf2_msgs/msg/TFMessage]
/unitree_lidar/points [sensor_msgs/msg/PointCloud2]
/velodyne_points/points [sensor_msgs/msg/PointCloud2]
```
