# Dog Factory ROS 2

A validated learning project for building and simulating a quadruped dog robot in ROS 2 Humble with Gazebo. The project separates the robot description, factory environment, control, bringup, and navigation concerns so that each package can be built and tested independently.

> **Scope.** This is an educational simulation. The example controller is not a production quadruped controller: a real robot would also require state estimation, complete inverse kinematics, trajectory generation, actuator interfaces, safety limits, and a dynamics-aware controller.

## 1. Prerequisites

The commands below assume Ubuntu with ROS 2 Humble installed. Confirm that ROS 2 is available before creating the workspace:

```bash
source /opt/ros/humble/setup.bash
ros2 --version
xacro --version
```

If `source` reports that the file does not exist, ROS 2 Humble is not installed at `/opt/ros/humble`, or a different ROS 2 distribution is installed. Do not remove or rename system directories to work around that error.

## 2. Create the workspace

Use the following commands exactly. A space is required between `source` and the path.

```bash
mkdir -p ~/dog_factory_ws/src
cd ~/dog_factory_ws
source /opt/ros/humble/setup.bash
```

The workspace root should contain source code in `src/`; `build/`, `install/`, and `log/` are generated later by `colcon` and should not be committed.

## 3. Package layout

The recommended package set is:

| Package | Responsibility | Important paths |
|---|---|---|
| `dog_robot_description` | URDF/Xacro robot model, links, joints, and sensors | `urdf/dog_robot.urdf.xacro`, `urdf/dog_robot_core.xacro` |
| `dog_factory_environment` | Gazebo world and environment assets | `worlds/factory.world`, `models/` |
| `dog_factory_control` | Python teleoperation, autonomy, and optional C++ nodes | `dog_factory_control/`, `src/`, `config/` |
| `dog_factory_bringup` | Main launch files and controller configuration | `launch/`, `config/` |
| `dog_factory_navigation` | Nav2 launch files, parameters, and maps | `launch/`, `config/`, `maps/` |

Create packages only inside `src/`:

```bash
cd ~/dog_factory_ws/src
ros2 pkg create --build-type ament_cmake dog_robot_description
ros2 pkg create --build-type ament_cmake dog_factory_environment
ros2 pkg create --build-type ament_cmake dog_factory_control
ros2 pkg create --build-type ament_cmake dog_factory_bringup
ros2 pkg create --build-type ament_cmake dog_factory_navigation
```

Create the required directories:

```bash
mkdir -p ~/dog_factory_ws/src/dog_robot_description/urdf
mkdir -p ~/dog_factory_ws/src/dog_factory_environment/{worlds,models,launch}
mkdir -p ~/dog_factory_ws/src/dog_factory_control/{dog_factory_control,src,config,tests}
mkdir -p ~/dog_factory_ws/src/dog_factory_bringup/{launch,config}
mkdir -p ~/dog_factory_ws/src/dog_factory_navigation/{launch,config,maps}
```

Check the layout before building:

```bash
find ~/dog_factory_ws/src -maxdepth 2 -name package.xml -print
```

Every ROS 2 package must have its own `package.xml` and `CMakeLists.txt`. Do not create packages at the workspace root.

## 4. Robot description: valid Xacro

Use one canonical entry filename throughout the project: `dog_robot.urdf.xacro`. Create it with:

```bash
nano ~/dog_factory_ws/src/dog_robot_description/urdf/dog_robot.urdf.xacro
```

Paste this minimal, well-formed entry file:

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="dog_robot">
  <xacro:include filename="$(find dog_robot_description)/urdf/dog_robot_core.xacro"/>
</robot>
```

The included core file can begin with a valid robot root and reusable materials:

```bash
nano ~/dog_factory_ws/src/dog_robot_description/urdf/dog_robot_core.xacro
```

```xml
<?xml version="1.0"?>
<robot xmlns:xacro="http://www.ros.org/wiki/xacro" name="dog_robot">
  <material name="dog_grey">
    <color rgba="0.35 0.35 0.35 1.0"/>
  </material>
  <material name="dog_orange">
    <color rgba="0.9 0.4 0.05 1.0"/>
  </material>

  <link name="base_link">
    <visual>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.5 0.25 0.12"/>
      </geometry>
      <material name="dog_grey"/>
    </visual>
    <collision>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <geometry>
        <box size="0.5 0.25 0.12"/>
      </geometry>
    </collision>
    <inertial>
      <mass value="8.0"/>
      <origin xyz="0 0 0" rpy="0 0 0"/>
      <inertia ixx="0.05" ixy="0.0" ixz="0.0" iyy="0.08" iyz="0.0" izz="0.09"/>
    </inertial>
  </link>

  <link name="body_shell">
    <visual>
      <origin xyz="0 0 0.09" rpy="0 0 0"/>
      <geometry>
        <box size="0.46 0.22 0.06"/>
      </geometry>
      <material name="dog_orange"/>
    </visual>
  </link>

  <joint name="body_shell_fixed" type="fixed">
    <parent link="base_link"/>
    <child link="body_shell"/>
    <origin xyz="0 0 0" rpy="0 0 0"/>
  </joint>
</robot>
```

### XML rules that prevent the common failures

Every XML attribute requires `name="value"` syntax. For example, use `name="dog_grey"`, not `name=dog_grey"`. The `rpy` attribute requires an equals sign: `rpy="0 0 0"`. Color tags must close their attribute quote before `/>`, and the attribute is `rgba`, not `rbga`. Every link needs a unique name, and the robot must have exactly one root link.

Use an editor or a quoted heredoc; do not paste a command prompt into the XML file. After editing, inspect the actual file on disk:

```bash
nl -ba ~/dog_factory_ws/src/dog_robot_description/urdf/dog_robot_core.xacro | sed -n '1,100p'
xacro ~/dog_factory_ws/src/dog_robot_description/urdf/dog_robot.urdf.xacro > /tmp/dog_robot.urdf
```

The `xacro` command must finish without an XML parsing error before attempting RViz or Gazebo.

## 5. Install the description package correctly

`colcon` does not automatically install arbitrary folders. The complete `CMakeLists.txt` must retain its required CMake and ament lines:

```cmake
cmake_minimum_required(VERSION 3.8)
project(dog_robot_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
```

A matching minimal `package.xml` is:

```xml
<?xml version="1.0"?>
<package format="3">
  <name>dog_robot_description</name>
  <version>0.1.0</version>
  <description>URDF and Xacro description of a quadruped dog robot.</description>
  <maintainer email="replace-with-your-email@example.com">Adam BENJABBAR</maintainer>
  <license>Apache-2.0</license>
  <buildtool_depend>ament_cmake</buildtool_depend>
  <exec_depend>xacro</exec_depend>
  <exec_depend>robot_state_publisher</exec_depend>
  <exec_depend>joint_state_publisher_gui</exec_depend>
  <exec_depend>urdf_launch</exec_depend>
  <exec_depend>rviz2</exec_depend>
  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Do not replace `CMakeLists.txt` with only an `install()` block. The `cmake_minimum_required`, `project`, `find_package`, and `ament_package` lines are all required.

## 6. Build and display the robot

Always build from the workspace root and source the generated workspace afterward:

```bash
cd ~/dog_factory_ws
source /opt/ros/humble/setup.bash
colcon build --packages-select dog_robot_description --symlink-install
source install/setup.bash
```

Validate the installed file:

```bash
ros2 pkg prefix dog_robot_description
ls "$(ros2 pkg prefix dog_robot_description)/share/dog_robot_description/urdf/"
```

Launch RViz with both launch arguments on the same command. A backslash at the end of a line means the command continues; the second argument must not become a standalone Bash command:

```bash
ros2 launch urdf_launch display.launch.py \
  urdf_package:=dog_robot_description \
  urdf_package_path:=urdf/dog_robot.urdf.xacro
```

The equivalent one-line command is:

```bash
ros2 launch urdf_launch display.launch.py urdf_package:=dog_robot_description urdf_package_path:=urdf/dog_robot.urdf.xacro
```

## 7. Reusable quadruped leg macro

Four nearly identical legs should be generated with a Xacro macro rather than copied manually. A production-quality version must give every generated link and joint a unique prefix:

```xml
<xacro:macro name="leg" params="prefix x y">
  <link name="${prefix}_hip">
    <visual>
      <geometry><cylinder radius="0.055" length="0.12"/></geometry>
      <material name="dog_orange"/>
    </visual>
  </link>

  <joint name="${prefix}_hip_joint" type="revolute">
    <parent link="base_link"/>
    <child link="${prefix}_hip"/>
    <origin xyz="${x} ${y} 0" rpy="1.5708 0 0"/>
    <axis xyz="0 0 1"/>
    <limit lower="-1.1" upper="1.1" effort="60" velocity="5"/>
  </joint>
</xacro:macro>

<xacro:leg prefix="front_left" x="0.25" y="0.20"/>
<xacro:leg prefix="front_right" x="0.25" y="-0.20"/>
<xacro:leg prefix="rear_left" x="-0.25" y="0.20"/>
<xacro:leg prefix="rear_right" x="-0.25" y="-0.20"/>
```

If a macro parameter is not used, remove it rather than leaving misleading configuration. Keep the XML opening tag, namespace, quotes, self-closing tags, and final `</robot>` balanced.

## 8. Factory environment package

The robot is described in URDF/Xacro; the Gazebo world is described in SDF. Create the world file:

```bash
nano ~/dog_factory_ws/src/dog_factory_environment/worlds/factory.world
```

A minimal valid world is:

```xml
<?xml version="1.0"?>
<sdf version="1.7">
  <world name="factory_world">
    <include><uri>model://sun</uri></include>
    <include><uri>model://ground_plane</uri></include>

    <physics type="ode">
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1.0</real_time_factor>
      <real_time_update_rate>1000</real_time_update_rate>
    </physics>

    <model name="wall_north">
      <static>true</static>
      <pose>0 5 1 0 0 0</pose>
      <link name="link">
        <collision name="collision">
          <geometry><box><size>10 0.2 2</size></box></geometry>
        </collision>
        <visual name="visual">
          <geometry><box><size>10 0.2 2</size></box></geometry>
        </visual>
      </link>
    </model>
  </world>
</sdf>
```

Use this complete environment `CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(dog_factory_environment)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  worlds
  models
  launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
```

The folders named in `install(DIRECTORY ...)` must exist. Build and test the installed world:

```bash
cd ~/dog_factory_ws
colcon build --packages-select dog_factory_environment --symlink-install
source install/setup.bash
ls "$(ros2 pkg prefix dog_factory_environment)/share/dog_factory_environment/worlds/"
gazebo "$(ros2 pkg prefix dog_factory_environment)/share/dog_factory_environment/worlds/factory.world"
```

## 9. Mixed Python and C++ control package

`dog_factory_control` uses `ament_cmake` because it can install Python nodes and compile C++ nodes in one package. The inner `dog_factory_control/` directory is the importable Python module directory; the outer directory is the ROS 2 package.

A Python teleoperation node can publish `geometry_msgs/msg/Twist` on `cmd_vel`. Restore terminal settings in a `finally` block whenever using `termios` and `tty`, so an interrupted node does not leave the terminal in raw mode. A C++ perception node should declare and link its ROS 2 dependencies explicitly in `CMakeLists.txt`; do not assume that building another package makes those dependencies available.

Build the control package separately while developing:

```bash
cd ~/dog_factory_ws
colcon build --packages-select dog_factory_control --symlink-install
source install/setup.bash
ros2 pkg executables dog_factory_control
```

## 10. Bringup and navigation

Keep launch files in the package’s `launch/` directory and configuration files in `config/`. A full bringup launch should start the world, spawn the robot, publish robot transforms, and start the relevant controllers. Navigation should be launched only after the robot publishes the required transforms and sensor topics.

Before using Nav2, inspect the graph instead of guessing topic names:

```bash
ros2 topic list
ros2 topic echo /scan --once
ros2 topic echo /tf --once
ros2 run tf2_tools view_frames
```

A navigation configuration must match the actual frame names and topics produced by the robot. If the robot publishes `lidar_link` but Nav2 expects `laser_frame`, change one side deliberately and document the decision; do not silently create inconsistent names.

## 11. Safe debugging workflow

When changing package names, install rules, or directory structure, remove only generated workspace artifacts and rebuild:

```bash
cd ~/dog_factory_ws
rm -rf -- build install log
source /opt/ros/humble/setup.bash
colcon build --symlink-install
source install/setup.bash
```

The `rm -rf -- build install log` command is safe here only because the preceding `cd` has been verified and the paths are disposable generated directories. Never run `rm -rf` with `/`, an empty variable, or an unverified path.

Useful checks are:

```bash
pwd
ls -la ~/dog_factory_ws
colcon list
ros2 pkg list | grep dog_
grep -n -- '----------' ~/dog_factory_ws/src/dog_robot_description/urdf/*.xacro
sed -n '1,120p' ~/dog_factory_ws/src/dog_robot_description/urdf/dog_robot_core.xacro
```

For an XML parser error, inspect the reported line and column first. Common causes are missing quotes, a missing `=`, misspelled attributes, an unclosed tag, or a command accidentally pasted into the XML file. Test the source file directly with `xacro` before rebuilding; this separates XML problems from installation problems.

## 12. Git version control

Create the ignore file before staging anything:

```bash
cd ~/dog_factory_ws
cat > .gitignore <<'EOF'
build/
install/
log/
__pycache__/
*.py[cod]
*.swp
*.swo
.vscode/
.idea/
*.tar.gz
EOF
```

Configure Git once, using an email associated with your GitHub account:

```bash
git config --global user.name "Adam BENJABBAR"
git config --global user.email "YOUR_GITHUB_EMAIL"
```

Review before committing:

```bash
git init
git branch -M main
git add .gitignore src/
git status
git commit -m "Initial validated dog factory ROS 2 workspace"
git log --oneline --decorate -1
git status
```

A clean status should show no untracked `build/`, `install/`, or `log/` directories. Never commit generated artifacts or credentials.

## 13. Common command mistakes

| Mistake | Correct form |
|---|---|
| `source/opt/ros/humble/setup.bash` | `source /opt/ros/humble/setup.bash` |
| `cd /~dog_factory_ws/src` | `cd ~/dog_factory_ws/src` |
| `ros2 launch ... urdf_package:=...` followed by a separate `urdf_package_path:=...` line | Keep both arguments in one command, using `\` for continuation |
| `rpy"0 0 0"` | `rpy="0 0 0"` |
| `name=dog_grey"` | `name="dog_grey"` |
| `rbga="..."` | `rgba="..."` |
| `<color rgba=".../>` | `<color rgba="..."/>` |
| `<link>` | `<link name="unique_link_name">` |
| Replacing all of `CMakeLists.txt` with only `install(...)` | Preserve `cmake_minimum_required`, `project`, `find_package`, and `ament_package` |
| `git add .gitignore` when the file was never created | Create `.gitignore`, then run `git add` |
| Committing without identity | Configure `user.name` and `user.email` first |

## 14. Final verification checklist

The project is ready for a first private backup when `xacro` succeeds, every package has valid metadata, the selected packages build successfully, the installed URDF and world files exist, and `git status` is clean. Confirm the exact commands and filenames used in this README rather than mixing `dog.urdf.xacro` with `dog_robot.urdf.xacro` or `dog_robot_description` with a different package name.

```bash
cd ~/dog_factory_ws
source /opt/ros/humble/setup.bash
xacro src/dog_robot_description/urdf/dog_robot.urdf.xacro > /tmp/dog_robot.urdf
colcon build --symlink-install
source install/setup.bash
ros2 pkg list | grep '^dog_'
git status
```

## License

Choose and declare a license before distributing the project. The examples above use Apache-2.0 metadata as a placeholder; replace the maintainer email and license declaration if your project uses different terms.


# Appendix A — Detailed explanations from the live-coding script

## A.1 Why the terminal comes first

ROS 2 tutorials often fail beginners before robotics even starts because the shell command is entered in the wrong directory, the environment was not sourced, or a multiline command was split incorrectly. The safest habit is to make the current directory visible with `pwd`, inspect the expected files with `ls -la`, and run one small verification command after each structural change.

`mkdir -p` means “make directories and create missing parents.” It is deliberately idempotent: running it again does not fail merely because the directory already exists. `cd` changes the current shell directory, while `source` executes a setup script in the current shell so that variables such as `AMENT_PREFIX_PATH`, `COLCON_PREFIX_PATH`, and `ROS_DISTRO` remain available to subsequent commands. The space in `source /opt/ros/humble/setup.bash` is mandatory because `source` is the command and the path is its argument.

Command chaining has a safety consequence. `command_a && command_b` runs the second command only when the first succeeds. This is useful for sequences such as `cd ~/dog_factory_ws && colcon build`, because it avoids building from an unintended directory. Separate lines are easier to read while teaching, but `&&` is preferable when a later command would be dangerous if an earlier command failed.

The expression `$(...)` is Bash command substitution. For example, `$(ros2 pkg prefix dog_factory_environment)` asks ROS 2 for the installed package directory and inserts the result into the surrounding command. This avoids hard-coded paths that would break for another user or another workspace location.

A heredoc writes multiple lines without opening an editor. The closing marker must appear alone on its own line, with no spaces before or after it:

```bash
cat > ~/dog_factory_ws/.gitignore <<'EOF'
build/
install/
log/
EOF
```

The quoted `EOF` prevents accidental expansion of variables inside the file content. This is particularly useful for `.gitignore`, YAML, and small configuration files.

## A.2 How a ROS 2 workspace is organized

A workspace is not itself a ROS 2 package. It is a container that normally has a `src/` directory containing one or more packages. A package is identified by `package.xml` and is built according to its declared build type. `colcon` discovers packages recursively under `src/`; placing an extra package at the workspace root can create confusing discovery errors or duplicate package names.

The `build/` directory contains intermediate build state, `install/` contains installed package resources and executables, and `log/` contains build and test logs. These directories are disposable. They should be removed only from a verified workspace directory and should never be edited manually or committed to Git.

The five-package architecture in this project is intentional. The description package answers “what is the robot?” The environment package answers “where is the robot?” The control package answers “how does it move?” The bringup package answers “how are all components started together?” The navigation package answers “how does it plan and follow routes?” Separating those questions makes failures easier to isolate.

## A.3 `ament_cmake` and `ament_python`

A pure Python ROS 2 package can use `ament_python`, which follows Python packaging conventions and is convenient for nodes written only in Python. This project uses `ament_cmake` for all packages so that the control package can contain both Python nodes and compiled C++ nodes. `ament_cmake_python` provides the Python installation helper inside an `ament_cmake` package.

The outer folder `dog_factory_control/` is the ROS 2 package. The inner folder `dog_factory_control/dog_factory_control/` is the importable Python module. Confusing those two levels is a common reason for an executable to build but fail at runtime with an import error.

## A.4 URDF, Xacro, and SDF are different layers

URDF is an XML representation of a single robot’s kinematic tree. It describes links, joints, visual geometry, collision geometry, inertial properties, and sensor frames. A valid URDF has one root link and no disconnected second tree. Each link and joint must have a unique name.

Xacro extends URDF with properties, macros, and includes. Xacro is still XML, so normal XML rules always apply. Every attribute must use `name="value"`; every opening tag must be closed; and self-closing tags must use the form `<tag .../>`. The `xmlns:xacro` declaration is required whenever `xacro:` elements appear.

SDF is Gazebo’s native world and simulation format. It can describe multiple independent models, lights, physics settings, and world-level resources. The practical distinction is simple: use URDF/Xacro for the dog and SDF for the factory world.

## A.5 Visual, collision, and inertial data

The `visual` element controls what RViz and Gazebo render. The `collision` element controls contact calculations. A detailed mesh can be used for the visual while a simpler box or cylinder is used for collision to reduce computation. The `inertial` element contains mass and an inertia tensor. Simulation quality depends on physically plausible values; zero or missing inertia can produce unstable motion, exploding joints, or links that pass through the floor.

The reusable `box_inertial` macro in this repository uses the standard rectangular-prism inertia equations. Its values are useful for an educational model, but they are not a substitute for measuring a real robot’s mass distribution. The same caution applies to joint effort, velocity, limits, and friction values.

## A.6 Why macros prevent quadruped mistakes

Four legs have the same logical structure but different positions and prefixes. Copying the complete XML four times makes it easy to leave one joint pointing to the wrong child, duplicate a name, or change one dimension accidentally. A Xacro macro centralizes the structure and changes only the prefix and mounting coordinates.

The prefix is not cosmetic. It makes names such as `front_left_hip`, `rear_right_hip_joint`, and their descendants unique. The generated TF tree depends on those names, so a duplicate name is both an XML/URDF problem and a runtime transform problem.

## A.7 Gazebo physics and the factory world

The example world includes a sun, a ground plane, two static walls, and a crate. Static models are appropriate for immovable scenery and allow Gazebo to optimize collision handling. The physics block uses a one-millisecond maximum step and a target update rate of 1000 Hz. A smaller step can improve contact accuracy but increases CPU cost; a larger step may run faster but can make legged contact and joints unstable.

The `real_time_factor` is a target, not a guarantee. If the computer cannot complete the physics calculations in time, Gazebo will run slower than real time. This is why a visually simple world can still become computationally expensive when high-frequency sensors and detailed collision geometry are added.

## A.8 Control architecture: Python and C++ together

Python is a good fit for keyboard teleoperation, state machines, and high-level orchestration because those components are easy to change and are usually not required to execute at hundreds of hertz. C++ is appropriate for high-frequency perception and control loops, large data processing, and latency-sensitive operations. Both languages communicate through ROS 2 topics, services, and actions rather than direct language coupling.

A teleoperation node commonly publishes `geometry_msgs/msg/Twist` to `cmd_vel`. The linear `x` component expresses forward and backward motion, while angular `z` expresses yaw. Raw terminal input requires `termios` and `tty`; the node must restore the terminal settings in a `finally` block even when interrupted with Ctrl-C.

Publishing a command is not the same as implementing a physical quadruped controller. The simulation skeleton demonstrates package boundaries and message flow. A full walking controller would need gait timing, support polygons, inverse kinematics, contact detection, joint feedback, trajectory limits, and safety behavior.

## A.9 Bringup and navigation dependencies

A bringup launch file is an orchestration layer. It should start the world, spawn the robot, publish the robot state, and start controllers in a deliberate order. Navigation should not be launched until the required TF frames and sensor topics exist.

Frame names and topic names must be treated as an interface contract. If a lidar publishes in `lidar_link` but a navigation configuration expects `laser_frame`, the mismatch must be corrected explicitly. Use the graph to inspect reality:

```bash
ros2 topic list
ros2 topic echo /scan --once
ros2 topic echo /tf --once
ros2 run tf2_tools view_frames
```

Nav2 parameters are not universal constants. They depend on the robot’s footprint, sensor frame, map resolution, planner, controller, and transform tree. Start with a minimal configuration, verify the TF and scan data, and only then tune planners and costmaps.

## A.10 A disciplined debugging loop

When `xacro` reports `line N, column M`, inspect that exact location in the source file rather than guessing:

```bash
nl -ba src/dog_robot_description/urdf/dog_robot_core.xacro | sed -n '1,120p'
```

Test the source directly:

```bash
xacro src/dog_robot_description/urdf/dog_robot.urdf.xacro > /tmp/dog_robot.urdf
```

If source validation succeeds but launch fails, inspect installation:

```bash
ros2 pkg prefix dog_robot_description
find "$(ros2 pkg prefix dog_robot_description)/share/dog_robot_description" -maxdepth 3 -type f
```

If the installed file is stale, rebuild after checking that the package’s CMake file installs the relevant directory. When the package structure or package name changes, remove only the generated directories and rebuild. Never “fix” a generated file under `install/`; the next build will overwrite it.

Common XML faults are visually small but exacting: `name=dog_grey"` is invalid because the opening quote is missing; `rpy"0 0 0"` is invalid because `=` is missing; `rbga` is not the URDF color attribute; and `<color rgba=".../>` is invalid because the attribute quote is not closed. The best defense is direct `xacro` validation before RViz.

## A.11 Git history and remote backups

Git has three relevant states: the working tree contains edits on disk, the index contains staged changes, and a commit records a permanent snapshot. `git status` is the primary inspection command. `git add` stages selected files, and `git commit -m "..."` records the staged snapshot.

A `.gitignore` prevents machine-generated artifacts from entering the index, but it does not remove files that were already committed. If `build/`, `install/`, or `log/` were committed by mistake, remove them from the index with `git rm -r --cached` after confirming that the ignore rules are correct.

When connecting a local repository to an existing GitHub repository, check the branch and remote before pushing:

```bash
git remote -v
git branch --show-current
git fetch origin
git log --oneline --all --decorate -10
```

Never use `git push --force` as a first fix for a history mismatch. A remote repository may contain commits that are not present locally. Merge deliberately, inspect conflicts, and push only after reviewing `git status` and `git diff`.

## A.12 Final teaching sequence

The most reliable learning order is incremental. First create and source the workspace. Then create one package and make its XML parse. Next install the URDF folder and display a single chassis in RViz. Add the shell, head, sensors, and legs one logical unit at a time. Test the environment world separately in Gazebo. Add control nodes only after the robot and world are independently valid. Finally combine everything in bringup and begin navigation.

This sequence is slower than pasting an entire project at once, but every milestone has a small failure surface. When something breaks, the last known-good milestone identifies where to look. That is the central debugging principle of the project: **change one layer, validate that layer, and only then add the next layer.**
