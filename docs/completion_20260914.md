# PRMS 审稿修改交付记录（2026-09-14）

## 当前可用结果

- 原归档：`demo/`，13 帧、68 条观测，保持原样，59 个文件的清单验证通过。
- 修复后推理：`outputs/reviewer_fixed_final/index.html`，13 帧、85 条观测。
- 类别统计：成熟 9、转色 9、绿熟 34、未熟 33；仍是旧模型的类别。
- `outputs/reviewer_fixed_final/comparison.json` 保存逐框匹配结果：原 68 条均有匹配、匹配类别不变，新增 17 条、移除 0 条。
- 九条成熟预测与 `maturity` 标签映射修复相符；其余差异不能仅归因于该修复。原归档未记录全部推理设置。

## 本轮收尾

1. 分类数据准备在写入输出前验证全部来源、划分、类别、可判读性和边界框。裁剪使用与推理一致的取整方式。无效标注不会留下部分训练图片。
2. `split_manifest.json` 保存输入元数据、来源哈希和每张裁剪的哈希。训练入口检查真实文件集合，拒绝更改或新增的未登记裁剪。
3. 端到端评估增加逐视图匹配、漏检、额外检测和错类统计，并记录未纳入评估的预测数量、输入文件哈希。
4. 操作窗口支持分类分辨率设置；留空使用权重配置。任务启动立即锁定，失败任务不会替换已成功结果的记录。首次打开结果时优先尝试修复后的完整结果。

## 重现命令

下列命令在仓库根目录运行。完整推理需要已安装 optional-requirements.txt。重跑请使用新的输出目录。

```powershell
python -m unittest discover -s tests -v
python scripts/verify_dataset.py
python scripts/replay_observations.py --source demo --output outputs/archive_replay
python demo.py --input data/panoramas --map assets/farm_map.jpg --output outputs/corrected_reproduction --detector two-stage --detector-weights models/tomato_detector.pt --classifier-weights models/tomato_ripeness_classifier.pt --confidence 0.25 --classifier-imgsz 64 --detector-imgsz 1280 --face-size 1440 --max-frames 0 --export-six-faces
python scripts/compare_runs.py --old demo/detections.csv --new outputs/corrected_reproduction/detections.csv --output outputs/corrected_reproduction/comparison.json
node tests/check_report_runtime.cjs outputs/corrected_reproduction/index.html
```

现有修复后运行的分类分辨率实际为 **64**，记录于 `run_config.json`。旧分模块评估使用 **96**，建议的绿宝石新训练为 **224**。这是不同设置，不能直接把指标合并。模型哈希和运行参数以对应结果目录为准；不同硬件和依赖可能影响精确输出，85 不是通用精度断言。

## 检查结果

32 项 Python 测试通过；59 个归档文件完整性校验通过；生成报告的 JavaScript 运行检查通过，确认筛选不改变已有观测位置、坐标模式保留 x/y/z。

本轮未重新训练模型，未改写论文实验数值，也未向远端推送。上轮完整推理输出继续有效，本轮改动集中在数据准备、评估报告及桌面任务管理。

## 仍需要真实数据的工作

- 确认绿宝石四分类边界样本和黄晕判读规范；对遮挡不可判读果实单独标记。
- 双人独立标注并复核分歧，按真实日期、路线与植株来源组织独立测试集。
- 用独立标注运行端到端评估，才能报告可采果召回率和误报率。
- 用标定、同步的位姿/距离和独立测量，才能验证空间误差。

现有全景能够继续用于图片标注，但缺少这些真值时，不能从演示结果生成有效的绿宝石准确率或空间定位精度。
