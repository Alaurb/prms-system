# Grounding DINO → SAM 2 候选实例流程（远程 Ubuntu）

此流程的目的，是把未标注或漏标的温室图像转成**待人工复核的番茄实例候选**：Grounding DINO 用文字提示提出框，SAM 2 按框切出掩膜和透明背景果实裁剪图。它不输出成熟度结论，也不能作为论文检测精度的证据。

## 已部署的可复现实验环境

- 远程项目根目录：`$PRMS_REMOTE_ROOT`（在本机部署时自行设置；不要将主机地址、用户名或凭据提交到仓库）
- Conda 环境：`prms-sam2`（Python 3.10，PyTorch 2.5.1 + CUDA 12.1）
- GPU：NVIDIA RTX A4500 Laptop GPU（16 GB）
- Grounding DINO：官方仓库 `IDEA-Research/GroundingDINO`，提交 `856dde2`
- DINO 权重：`models/groundingdino/groundingdino_swint_ogc.pth`；下载文件 SHA-256 已核对为 `3b3ca2563c77c69f651d7bd133e97139c186df06231157a64c507099c52bc799`
- SAM 2：官方仓库提交 `2b90b9f`，权重 `models/sam2/sam2.1_hiera_small.pt`

模型载入固定为离线模式，避免运行时访问 Hugging Face：`TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1`。

## 一张图的运行命令

在远程机器执行：

```bash
cd "$PRMS_REMOTE_ROOT"
conda activate prms-sam2
TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1 python scripts/groundingdino_sam2_candidates.py \
  --image yolo-v8/tomato_seg/images/train/enhanced_11.6-323-right.jpg \
  --output outputs/dino_sam2_smoke_test \
  --dino-config tools/GroundingDINO/groundingdino/config/GroundingDINO_SwinT_OGC.py \
  --dino-checkpoint models/groundingdino/groundingdino_swint_ogc.pth \
  --sam-checkpoint models/sam2/sam2.1_hiera_small.pt \
  --caption 'tomato.' --box-threshold 0.20 --text-threshold 0.20
```

输出包括：

- `overlay.jpg`：红框为 DINO 候选框，绿色半透明区域为 SAM 2 掩膜；
- `crops/*.png`：带 alpha 通道的单果裁剪图；
- `masks/*.png`：二值实例掩膜；
- `manifest.jsonl`：候选分数、框、掩膜面积和人工复核字段。

`maturity_label` 始终为空，需由人工依据绿宝石番茄的黄晕等特征复核，并写入约定的四类标签：`immature`、`mature_green`、`harvest_ready`、`overripe_or_defective`。

## 当前烟雾测试结论

在 `enhanced_11.6-323-right.jpg` 上，以提示词 `tomato.`、框阈值 0.20 运行，Grounding DINO 给出 8 个候选；同图现有人工框为 15 个。该数量差表明零样本检测仍有漏检，尤其不应把低分候选直接纳入训练标签。下一步应由人工审核候选、补标漏检果实，再以审核后的实例训练专用检测模型并在独立测试集报告指标。
