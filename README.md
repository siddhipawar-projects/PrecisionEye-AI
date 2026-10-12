# PrecisionEye AI 🔬

> AI-powered manufacturing defect detection using PatchCore + ResNet — no defect labels required.

---

## What it does

PrecisionEye AI detects surface defects in manufactured parts by learning what a **good part looks like** — without ever seeing a single defective example during training.

Upload an image of a part → get an instant **GOOD / DEFECT** verdict + an anomaly heatmap showing exactly where the defect is.

---

## Demo

| Input | Anomaly Map | Verdict |
|-------|------------|---------|
| Metal nut image | Heatmap highlights defective region | ✕ DEFECT — 74% confidence |

---

## How it works

### Algorithm: PatchCore (CVPR 2022)

1. **Feature extraction** — A pre-trained ResNet backbone extracts patch-level features from Layer 2 and Layer 3, producing 1536-dimensional vectors per spatial position
2. **Memory bank** — Features from all good training images are stored in a memory bank (coreset-subsampled to 10% for speed)
3. **Inference** — At test time, the query image's features are compared to the memory bank via nearest-neighbour search. The anomaly score = minimum Euclidean distance to any stored feature
4. **Verdict** — If the score exceeds a calibrated threshold, the part is flagged as defective
5. **Heatmap** — Per-patch distances are upsampled and smoothed to produce a spatial anomaly map

### Why no defect labels?
Traditional defect classifiers need thousands of labeled defect images for every defect type. PatchCore trains **only on good parts** — anything deviating from the learned normal distribution is flagged, including defect types never seen before.

---

## Results

| Metric | Value |
|--------|-------|
| AUROC (Metal Nut) | **87.9%** |
| Training images | 220 (good parts only) |
| Defect labels needed | 0 |
| Feature dimensions | 1536 |
| Memory bank sampling | 10% coreset |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| ML Framework | PyTorch 2.0 |
| Backbone | ResNet / Wide-ResNet-50 |
| Dataset | MVTec Anomaly Detection (MVTec AD) |
| Frontend | Streamlit |
| Feature layers | ResNet Layer2 + Layer3 |
| Distance metric | Euclidean (nearest neighbour) |

---

## Project Structure

```
PrecisionEye-AI/
├── app.py                  # Streamlit app (all pages + inference)
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Dark theme config
├── models/                 # ← not in repo (add your own)
│   ├── feature_extractor.pth
│   ├── metadata.pkl
│   └── reference_images/
└── README.md
```

---

## Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/siddhipawar-projects/PrecisionEye-AI.git
cd PrecisionEye-AI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your trained model files to models/
#    - models/feature_extractor.pth
#    - models/metadata.pkl
#    - models/reference_images/  (good training images)

# 4. Run the app
python -m streamlit run app.py
```

---

## Dataset

**MVTec Anomaly Detection (MVTec AD)** — industry-standard benchmark with 15 categories of manufactured objects and surface textures, pixel-precise defect annotations across 70+ defect types.

- Metal Nut category: bent, color, flip, scratch defects
- Published by MVTec Software GmbH, Munich
- Paper: [MVTec AD — A Comprehensive Real-World Dataset for Unsupervised Anomaly Detection](https://www.mvtec.com/company/research/datasets/mvtec-ad)

---

## Domains

| Domain | Status |
|--------|--------|
| 🔩 Metal Nut | ✅ Live |
| 🍶 Bottle | 🔜 Coming Soon |
| 🔌 Cable | 🔜 Coming Soon |
| 💊 Capsule | 🔜 Coming Soon |
| 🟫 Leather | 🔜 Coming Soon |
| 🪛 Screw | 🔜 Coming Soon |

---

## Built by

Siddhi Pawar — ML Engineer  


---

*Built with PyTorch · Streamlit · MVTec AD Dataset*
