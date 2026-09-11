"""Reproject saved detections without rerunning inference or inventing new labels."""
import argparse
import csv
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from PIL import Image
from ripeness_demo.detectors import Detection
from ripeness_demo.mapping import Pose, project_detection
from ripeness_demo.evidence import associate
from ripeness_demo.artifacts import build_evidence_manifest, write_evidence_manifest
from ripeness_demo.report import write_csv_files, write_summary, write_html_report, draw_map_overlay


def replay(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    with (source/"detections.csv").open(encoding="utf-8-sig",newline="") as f:
        rows=list(csv.DictReader(f))
    with (source/"trajectory.csv").open(encoding="utf-8-sig",newline="") as f:
        pose_rows=list(csv.DictReader(f))
    config=json.loads((source/"run_config.json").read_text(encoding="utf-8"))
    poses=[Pose(r["frame"],*[float(r[k]) for k in ("x","y","z","yaw","map_px","map_py")],r["source"],r["route"]) for r in pose_rows]
    lookup={p.frame:p for p in poses}
    # This replay has no measured depth and must retain that limitation.
    if any(p.source != "synthetic_map_path" for p in poses):
        raise ValueError("Replay expects the supplied synthetic demo trajectory; use demo.py for measured input")
    with Image.open(source/"map_base.png") as im:
        map_image=im.convert("RGB")
    detections=[]
    for r in rows:
        detection=Detection(r["class_name"],float(r["confidence"]),tuple(float(r[k]) for k in ("bbox_x1","bbox_y1","bbox_x2","bbox_y2")),r["detector"])
        detections.append(project_detection(detection,r["side"],lookup[r["frame"]],(int(r["view_width"]),int(r["view_height"])),map_image.size,
            map_width_m=config["map_width_m"],row_offset_m=config["row_offset_m"],camera_height_m=config["camera_height_m"],annotated_image=r["annotated_image"]))
    tracks,links=associate(detections,poses)
    output.mkdir(parents=True,exist_ok=True)
    if source != output:
        shutil.copytree(source/"annotated",output/"annotated",dirs_exist_ok=True)
    map_image.save(output/"map_base.png")
    draw_map_overlay(map_image,poses,detections,output/"map_overlay.png")
    write_csv_files(output,poses,detections,config["row_offset_m"])
    detector_name=rows[0]["detector"] if rows else "saved_predictions"
    summary=write_summary(output,poses,detections,detector_name,"synthetic_map_path",len(poses))
    summary.update(processing_mode="saved_prediction_replay",range_source="assumed_row_plane",nearest_row_filter="not_verified_no_depth",
                   association_status="disabled_no_measured_geometry",candidate_tracks=len(tracks),rejected_observations=0)
    evidence=build_evidence_manifest(summary,poses,processing_mode=summary["processing_mode"],range_source=summary["range_source"])
    gallery=[]
    for pose in poses:
        for side in ("left","right"):
            gallery.append(dict(frame=pose.frame,side=side,count=sum(d.frame==pose.frame and d.side==side for d in detections),path=f"annotated/{Path(pose.frame).stem}_{side}_det.jpg"))
    write_html_report(output,summary,poses,detections,gallery,config["map_width_m"],config["map_width_m"]*map_image.height/map_image.width,map_image.size,config["row_offset_m"],evidence=evidence)
    config["revision_processing"]="saved_prediction_replay; no new inference or measured depth"
    for name,data in (("summary.json",summary),("tracks.json",tracks),("association_links.json",links),("run_config.json",config),("rejected_observations.json",[])):
        (output/name).write_text(json.dumps(data,indent=2),encoding="utf-8",newline="\n")
    write_evidence_manifest(output,evidence)
    print(f"Replayed {len(detections)} observations from {len(poses)} frames")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source",default=str(ROOT/"demo"))
    parser.add_argument("--output",default=str(ROOT/"outputs/revision_replay"))
    args=parser.parse_args()
    replay(args.source,args.output)
