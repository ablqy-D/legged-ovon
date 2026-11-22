"""Go2 + Gazebo Fortress + Nav2 bringup.

归档仓库里的 go2_nav_launch.py 依赖不存在的 go2_sdk 包，这里用
go2_launch.py + 自写 nav2_params.yaml 组一个能跑的 Nav2 闭环。

用法:
  ros2 launch ~/ros2_ws/launch/go2_nav2.launch.py map:=.../maps/maze.yaml

默认的 map / nav2_params 取本文件上一级的 config/ 和 maps/，所以无论从
~/ros2_ws/launch/（软链）还是从仓库里直接 launch 都能找到。
"""

import os

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    TimerAction,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

BUNDLE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MAP = os.path.join(BUNDLE, "maps", "maze.yaml")
DEFAULT_PARAMS = os.path.join(BUNDLE, "config", "nav2_params.yaml")


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time")
    map_file = LaunchConfiguration("map")
    params_file = LaunchConfiguration("nav2_params")
    gui = LaunchConfiguration("gui")

    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("go2_gazebo_sim"), "launch", "go2_launch.py"]
            )
        ),
        launch_arguments={
            "use_sim_time": use_sim_time,
            "rviz": "false",
            "gui": gui,
            "publish_map_tf": "false",
        }.items(),
    )

    common = [params_file, {"use_sim_time": use_sim_time}]

    nav2_nodes = [
        Node(
            package="nav2_map_server",
            executable="map_server",
            name="map_server",
            output="screen",
            parameters=[{"use_sim_time": use_sim_time}, {"yaml_filename": map_file}],
        ),
        Node(
            package="nav2_amcl",
            executable="amcl",
            name="amcl",
            output="screen",
            parameters=common,
        ),
        Node(
            package="nav2_controller",
            executable="controller_server",
            output="screen",
            parameters=common,
            remappings=[("/cmd_vel", "/cmd_vel_nav")],
        ),
        Node(
            package="nav2_smoother",
            executable="smoother_server",
            name="smoother_server",
            output="screen",
            parameters=common,
        ),
        Node(
            package="nav2_planner",
            executable="planner_server",
            name="planner_server",
            output="screen",
            parameters=common,
        ),
        Node(
            package="nav2_behaviors",
            executable="behavior_server",
            name="behavior_server",
            output="screen",
            parameters=common,
        ),
        Node(
            package="nav2_bt_navigator",
            executable="bt_navigator",
            name="bt_navigator",
            output="screen",
            parameters=common,
        ),
        Node(
            package="nav2_waypoint_follower",
            executable="waypoint_follower",
            name="waypoint_follower",
            output="screen",
            parameters=common,
        ),
        Node(
            package="nav2_velocity_smoother",
            executable="velocity_smoother",
            name="velocity_smoother",
            output="screen",
            parameters=common,
            remappings=[
                ("/cmd_vel", "/cmd_vel_nav"),
                ("/cmd_vel_smoothed", "/cmd_vel"),
            ],
        ),
        Node(
            package="nav2_lifecycle_manager",
            executable="lifecycle_manager",
            name="lifecycle_manager_navigation",
            output="screen",
            parameters=[
                {"use_sim_time": use_sim_time},
                {"autostart": True},
                {
                    "node_names": [
                        "map_server",
                        "amcl",
                        "controller_server",
                        "smoother_server",
                        "planner_server",
                        "behavior_server",
                        "bt_navigator",
                        "waypoint_follower",
                        "velocity_smoother",
                    ]
                },
            ],
        ),
    ]

    # Gazebo 和 CHAMP 需要几秒初始化，Nav2 晚 10 秒起，避免生命周期管理器
    # 在 TF / action server 还没就绪时反复重试。
    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("map", default_value=DEFAULT_MAP),
            DeclareLaunchArgument("nav2_params", default_value=DEFAULT_PARAMS),
            DeclareLaunchArgument("gui", default_value="true"),
            sim,
            TimerAction(period=10.0, actions=nav2_nodes),
        ]
    )
