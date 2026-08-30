cmake_minimum_required(VERSION 3.8)
project(aerocue_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/MissionWaypoint.msg"
  "msg/DroneStatus.msg"
  "msg/SyncCommand.msg"
  "msg/Mission.msg"
  "msg/SurvivorDetection.msg"
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()
