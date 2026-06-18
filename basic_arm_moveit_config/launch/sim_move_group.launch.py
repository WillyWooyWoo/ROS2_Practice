import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():
    # 1. Load URDF, SRDF, and Kinematics from the builder
    moveit_config = (
        MoveItConfigsBuilder("basic_arm", package_name="basic_arm_moveit_config")
        .robot_description_kinematics(file_path="config/kinematics.yaml")
        .to_moveit_configs()
    )
    
    # Filter Nones to prevent launch crashes
    moveit_config_dict = {k: v for k, v in moveit_config.to_dict().items() if v is not None}
    
    # 2. THE CRUCIAL FIX: Destroy the corrupted empty namespaces
    moveit_config_dict.pop("ompl", None)
    moveit_config_dict.pop("planning_pipelines", None)
    moveit_config_dict.pop("default_planning_pipeline", None)

    # 3. Define the pristine OMPL parameters natively
    ompl_dict = {
        "planning_pipelines": {"pipeline_names": ["ompl"]},
        "default_planning_pipeline": "ompl",
        "ompl": {
            "planning_plugin": "ompl_interface/OMPLPlanner",
            "request_adapters": [
                "default_planner_request_adapters/AddTimeOptimalParameterization",
                "default_planner_request_adapters/ResolveConstraintFrames",
                "default_planner_request_adapters/FixWorkspaceBounds",
                "default_planner_request_adapters/FixStartStateBounds",
                "default_planner_request_adapters/FixStartStateCollision",
                "default_planner_request_adapters/FixStartStatePathConstraints"
            ],
            "start_state_max_bounds_error": 0.1,
            "planner_configs": {
                "RRTConnectkConfigDefault": {
                    "type": "geometric::RRTConnect",
                    "range": 0.0
                }
            },
            "arm": {
                "default_planner_config": "RRTConnectkConfigDefault",
                "planner_configs": ["RRTConnectkConfigDefault"]
            }
        },
        "use_sim_time": True
    }
    
    # 4. Safely merge the pristine dictionary into the configuration
    moveit_config_dict.update(ompl_dict)

    # 5. Launch the nodes
    run_move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[moveit_config_dict],
    )
    
    rviz_config_file = os.path.join(get_package_share_directory("william"), "config", "config.rviz")
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="log",
        arguments=["-d", rviz_config_file],
        parameters=[moveit_config_dict],
    )
    
    return LaunchDescription([run_move_group_node, rviz_node])
