from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED = [
    "README.md",
    "docs/system_architecture.md",
    "docs/interfaces.md",
    "docs/navigation_integration.md",
    "docs/setup_status.md",
    "docs/reproducibility_plan.md",
    "docs/handoff_5_6_terra.md",
    "docs/reference_map.md",
    "docs/系统实现思路.md",
    "config/system.yaml",
    "config/topology.yaml",
    "config/perception.yaml",
    "config/navigation_external.yaml",
    "examples/maps/greenhouse_reference.yaml",
    "examples/maps/greenhouse_reference.pgm",
    "examples/nav_smoke/README.md",
    "examples/nav_smoke/index.html",
    "examples/nav_smoke/greenhouse_reference.png",
    "examples/nav_smoke/trace_sample.json",
    "scripts/run_wsl_smoke.ps1",
    "scripts/run_smoke.sh",
    "scripts/run_wsl_map_smoke.ps1",
    "scripts/run_map_smoke.sh",
    "scripts/run_wsl_closed_loop_nav_smoke.ps1",
    "scripts/run_closed_loop_nav_smoke.sh",
    "launch/prms_system.launch",
    "src/prms_bringup/config/system.yaml",
    "src/prms_bringup/config/topology.yaml",
    "src/prms_bringup/config/perception.yaml",
    "src/prms_bringup/config/navigation_external.yaml",
    "src/prms_bringup/maps/greenhouse_reference.yaml",
    "src/prms_bringup/maps/greenhouse_reference.pgm",
    "src/prms_bringup/launch/prms_system.launch",
    "src/prms_bringup/launch/simulation_smoke.launch",
    "src/prms_bringup/launch/simulation_map_smoke.launch",
    "src/prms_bringup/launch/closed_loop_nav_smoke.launch",
    "src/prms_msgs/msg/MaturityDetection.msg",
    "src/prms_msgs/msg/MaturityObservationArray.msg",
    "src/prms_topology/scripts/topology_path_publisher.py",
    "src/prms_perception_bridge/scripts/prms_csv_bridge.py",
    "src/prms_fusion/scripts/maturity_fusion_node.py",
    "src/prms_sim/scripts/simulated_localization_node.py",
    "src/prms_sim/scripts/cmd_vel_odom_simulator.py",
    "src/prms_sim/scripts/simple_path_follower.py",
    "src/prms_sim/scripts/route_smoke_validator.py",
    "src/prms_sim/scripts/map_smoke_validator.py",
    "src/prms_sim/scripts/closed_loop_nav_validator.py",
]


def main() -> int:
    missing = [path for path in REQUIRED if not (ROOT / path).exists()]
    if missing:
        for path in missing:
            print(f"missing: {path}")
        return 1
    print(f"framework check ok: {len(REQUIRED)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
