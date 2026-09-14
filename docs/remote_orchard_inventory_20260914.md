# Ubuntu orchard_project 只读盘点（2026-09-14）

范围：用户指定的远程 `orchard_project` 工作区（路径已脱敏）。通过 SSH 读取目录、核心脚本、训练配置、模型 SHA-256、ROS bag 元数据及一个深度数组。未运行原项目程序、训练或 bag 播放；未移动、删除远端文件；未批量下载。图片数量属于文件统计，不代表独立样本；尚未逐张目视审查或去重。

## 资产清单

目录总占用约 87 GiB（du 四舍五入）。

| 路径 | 内容与规模 | 用途与限制 |
| --- | --- | --- |
| datasets/test.bag | 20,039,777,125 字节；37 分 28 秒；657,316 消息 | 多传感器原始记录；是否与论文实验同源待确认 |
| datasets/数据集 | 约 41 GiB；15,533 JPG、2,608 PNG、1,483 NPY | 多日期采集与派生图；目录中有 5 个 downloading 文件，不应当作完整数据 |
| images | 约 13 GiB，19,820 JPG，left/right/usb | 相机导出图；需恢复时间戳对应关系 |
| 检测图片 | 约 12 GiB，1,142 JPG、13 MP4、1 MOV | 鱼眼、左右图、入田视频等 |
| share | 224 JPG，约 1.3 GiB | 图像子集，尚未验证与 images 的重复关系 |
| go2picture / go2vedio | 677 JPG / 4 MP4 | 机器人采集候选数据 |
| yolo-v8 | 两阶段识别、交互修正、热力图、检测和分类数据 | 旧原型，不宜直接覆盖 PRMS |
| runs | 检测与多个分类训练记录、best/last 权重 | 可追溯旧模型配置，指标未独立复验 |
| scripts | 全景投影、抽帧、YOLO、合成数据生成 | 散落脚本与硬编码路径较多 |
| src/bagtrans | Catkin 包和 bag2image.launch | 提取相机图像；launch 仍使用旧的绝对工作区路径 |
| 最终图片 | 37 JPG、3 PNG、175 TXT | 图示及成熟度计数/布局文件；不能直接当三维真值 |
| 典型地形 / 典型番茄 | 场景及典型样例 | 候选论文配图；采集授权、品种待核实 |
| build / devel / .venv | 构建及环境产物 | 与源代码分离管理；本次不删除 |
| models/bert-base-uncased | 约 423 MiB | 与当前两阶段 YOLO 路线关系待核实 |

## 新发现：bag 与深度数据

rosbag info 报告时间为 2025-11-23 10:19:04 至 10:56:33（远端显示时区未核实）。

- 左右压缩相机各 1,121 消息；USB 压缩图像 44,718 消息。
- Livox 雷达 22,370 消息，IMU 447,455 消息。
- NavSatFix 与同步版本各 22,484 消息；另有 RTK PVTSLN、触发和同步话题。
- 未列出标准 /tf、/odom、CameraInfo 话题。现有信息不足以证明有已标定相机位姿和果实深度。
- 自定义消息包括 Livox、RTK、相机触发等；进一步解码需要检查消息定义与标定来源。
- 崇明视觉数据包含多个 2025-12-28/29 命名的 color/depth 目录。抽查 `data_20251229_113514/depth/depth_0335.npy`：480×640、uint16、数值范围 0–65535。不能据此认定单位为毫米；零值/65535 的含义、对齐方式、内参和时间戳必须核实。
- 崇明视觉数据子树本次未找到 .txt/.json/.yaml/.py 元数据；并不排除标定存在其他位置或嵌入其他文件。

因此应将“用户尚未提供 bag”更新为“远端已发现候选 bag，但尚未建立与论文实验的对应和可用几何证据”。不能直接声称空间定位已验证。

## 模型与代码问题

1. `yolo-v8/tomato-cls.pt` 与 `runs/classify/tomato_maturity_model14/weights/best.pt` SHA-256 相同：`d623cc087adb61793ebeca6cc42bdf42eff5b5c5b1a9e2e9005add0c8d2d3eee`，也与当前 PRMS 分类模型相同。训练配置为 yolov8n-cls、imgsz=64、epochs=50、batch=32。
2. `yolov8-seg-cls.py`、`yolov8-interact.py` 硬编码类别顺序为 immature/green/discoloration/maturity/other；同哈希模型在本地已核验的顺序是 discoloration/green/immature/maturity/other。索引 0 和 2 会错配。旧输出不宜未经复核作为论文证据。
3. 远端 `tomato-seg.pt` 与 detect/train6/best.pt 相同，SHA-256 为 `b783aac1e4a8608049a8238962c6b8e5bdac94487d518bc9232a9f3a13ea6c37`；与 PRMS 当前检测权重不同。仅凭文件名不能判断模型能力更强，也不能认定真实任务是分割。
4. 名为 yolov8-seg-train.py 的脚本实际从 yolov8n.pt 开始训练，数据配置只有 tomato 一类。需要以模型任务和标签格式判断，而非脚本名。
5. yolov8-hot.py 从文本计数、布局顺序和设置的间距生成堆叠柱体；Z 表示计数堆叠，不是果实物理高度。generate_synthetic_data.py 明确用随机扰动生成成熟度矩阵，必须保留 synthetic 标识。

## 训练数据现状

检测 JPG / TXT 文件数：train 192/131，val 26/24，test 24/21。数量不等，需要按文件主名逐一核实缺标和合法负样本，不能仅按差额判断错误。

分类各类别目录条目数（尚未全部校验图像）：

| 划分 | discoloration | green | immature | maturity | other |
| --- | ---: | ---: | ---: | ---: | ---: |
| train | 33 | 42 | 31 | 26 | 3 |
| val | 11 | 14 | 10 | 6 | 1 |

未见独立 test 分类目录；不能把这些旧标签直接改名为绿宝石四分类。远端数据与此前本地审计快照数量有差异，应建立新版本清单，不覆盖旧记录。

## 2026-09-14 补充审计：远端 yolo-v8 与 yolo_test

上述初步盘点中将 `yolo-v8/tomato_seg` 视为分割数据是不准确的；逐行检查后，它的每一行都是 5 列 YOLO **边界框**（`class cx cy w h`），并非分割多边形。

| 资产 | 实际情况 | 是否够用 |
| --- | --- | --- |
| `yolo-v8/tomato_seg` | train 下 296 图、174 个 txt（其中 `classes.txt` 不是标注）；173 个图文配对，1,366 个番茄框，单类 0；无 val/test 目录。123 张未带 txt 图可能是负样本，也可能是漏标，必须人工判定。 | 可作为单类检测原型的标注池；尚不是可报告的分割数据集，也不能做独立测评。 |
| `yolo-v8/tomato_ripeness` | train 135 张、val 42 张，共 177 张；五类：discoloration 44、green 56、immature 41、maturity 32、other 4。无 test。另有一张 exact duplicate：`tomato_025.jpg` 同时在 train/other 和 val/other。 | 可做旧五类概念验证；样本很少，other 极端稀缺，不能据此宣称绿宝石四类成熟度性能。 |
| `yolo_test/datasets` | 实际是另一份小型成熟度检测数据：13 train 图、4 val 图、2 test 图。val 的 5 个标签误放在 `labels/vel` 而训练 YAML 指向 `labels/val`；配置写 nc=4，但若干标注使用 class 4，实际至少五类。`classes.txt` 是类别清单，不应当按标注解析。 | 当前不能可靠训练或评估；整理后也仅 19 图级样本，远远不足以支持泛化结论。 |

远端同一份分类模型的类别应以 checkpoint 元数据为准，不能从目录顺序或旧脚本推断。Green Gem 的目标四类与该旧五类（immature/green/discoloration/maturity/other）不是一一等价标签，尤其 harvest-ready 的黄晕判据需要重新人工标注。

## 推荐整理顺序

1. 原始文件保持不动，建立相对路径、大小、哈希、采集日期/设备/授权的索引；先核实 bag 的采集场景与论文关系。
2. 抽取少量 RGB、深度和 bag 图像预览，人工确认番茄品种、黄晕可见性和有效深度；查找内外参、深度单位、时钟同步记录。
3. 按源图/采集批次去重，划分独立训练/验证/测试，明确哪些图是真实负样本。
4. 旧模型和脚本作为 legacy 归档，修正类别索引后才能用于对比实验；与 PRMS 现有模型在同一人工真值上比较。
5. 有标定和同步证据后再实现 RGB-D / bag 数据接口；在此之前继续标记空间布局为未验证。
6. 逻辑分类建议为 raw、annotations、models、legacy、derived、docs。落实物理移动前先生成迁移清单，处理硬编码路径与重复依赖；本次仅提供方案，不执行搬迁或清理。
