cmake_minimum_required(VERSION 3.8)
project(dog_factory_control)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_srvs REQUIRED)
find_package(nav_msgs REQUIRED)

ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  dog_factory_control/keyboard_teleop.py
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY config tests
  DESTINATION share/${PROJECT_NAME}
)

# Add C++ executables here when their source files are implemented.
# add_executable(sensor_fusion_node src/sensor_fusion_node.cpp)
# ament_target_dependencies(sensor_fusion_node rclcpp sensor_msgs nav_msgs)
# install(TARGETS sensor_fusion_node DESTINATION lib/${PROJECT_NAME})

ament_package()
