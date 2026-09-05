from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


REQUIRED = [
    "README.md",
    "docs/system_architecture.md",
    "docs/interfaces.md",
    "config/system.yaml",
    "config/topology.yaml",
    "config/perception.yaml",
    "launch/prms_system.launch",
    "src/prms_msgs/msg/MaturityDetection.msg",
    "src/prms_msgs/msg/MaturityObservationArray.msg",
    "src/prms_topology/scripts/topology_path_publisher.py",
    "src/prms_perception_bridge/scripts/prms_csv_bridge.py",
    "src/prms_fusion/scripts/maturity_fusion_node.py",
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

