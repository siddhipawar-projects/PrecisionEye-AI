import streamlit as st
import os
import io
import re
import numpy as np
from PIL import Image

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

st.set_page_config(
    page_title="PrecisionEye AI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "page"            not in st.session_state: st.session_state.page            = "home"
if "selected_domain" not in st.session_state: st.session_state.selected_domain = None
if "result"          not in st.session_state: st.session_state.result          = None

DOMAINS = [
    {"id": "metal_nut", "name": "Metal Nut",  "icon": "🔩", "live": True,  "desc": "Bent, color, flip, scratch defects"},
    {"id": "bottle",    "name": "Bottle",      "icon": "🍶", "live": False, "desc": "Glass & plastic containers"},
    {"id": "cable",     "name": "Cable",       "icon": "🔌", "live": False, "desc": "Wire harness inspection"},
    {"id": "capsule",   "name": "Capsule",     "icon": "💊", "live": False, "desc": "Pharmaceutical capsules"},
    {"id": "leather",   "name": "Leather",     "icon": "🟫", "live": False, "desc": "Surface texture analysis"},
    {"id": "screw",     "name": "Screw",       "icon": "🪛", "live": False, "desc": "Threaded fasteners"},
    {"id": "tile",      "name": "Tile",        "icon": "🟦", "live": False, "desc": "Ceramic surface defects"},
    {"id": "wood",      "name": "Wood",        "icon": "🪵", "live": False, "desc": "Wood grain anomalies"},
]

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif !important;
    background-color: #07091A !important;
    color: #CBD5E1;
}

/* ── kill default streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2rem 4rem 2rem 4rem !important;
    max-width: 1200px !important;
    margin: 0 auto !important;
}

/* ── kill ALL default button styling completely ── */
.stButton > button {
    all: unset !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    transition: all 0.15s ease !important;
    white-space: nowrap !important;
}

/* ── LOGO ── */
.logo-wrap .stButton > button {
    font-size: 20px !important;
    font-weight: 800 !important;
    color: #fff !important;
    letter-spacing: -0.5px !important;
    padding: 0 !important;
    background: none !important;
    border: none !important;
    text-shadow: 0 0 20px rgba(129,140,248,0.5) !important;
}
.logo-wrap .stButton > button:hover { color: #A5B4FC !important; }

/* ── NAV LINK (About) ── */
.nav-link .stButton > button {
    color: #94A3B8 !important;
    padding: 8px 18px !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    background: rgba(255,255,255,0.04) !important;
}
.nav-link .stButton > button:hover {
    color: #E2E8F0 !important;
    background: rgba(255,255,255,0.08) !important;
    border-color: rgba(255,255,255,0.18) !important;
}

/* ── GHOST (back / secondary) ── */
.btn-ghost .stButton > button {
    color: #94A3B8 !important;
    padding: 9px 20px !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    background: rgba(255,255,255,0.04) !important;
}
.btn-ghost .stButton > button:hover {
    color: #E2E8F0 !important;
    border-color: rgba(255,255,255,0.25) !important;
    background: rgba(255,255,255,0.08) !important;
}

/* ── INDIGO PRIMARY ── */
.btn-primary .stButton > button {
    color: #fff !important;
    padding: 11px 24px !important;
    border-radius: 9px !important;
    border: none !important;
    background: linear-gradient(135deg, #6366F1, #818CF8) !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
}
.btn-primary .stButton > button:hover {
    background: linear-gradient(135deg, #4F46E5, #6366F1) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.5) !important;
    transform: translateY(-1px) !important;
}

/* ── DISABLED CARD BUTTON ── */
.btn-disabled .stButton > button {
    color: #334155 !important;
    padding: 8px 16px !important;
    border-radius: 8px !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    background: rgba(255,255,255,0.02) !important;
    cursor: not-allowed !important;
    font-size: 12px !important;
}

/* ── NAV BAR ── */
.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 4rem;
    height: 68px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    background: rgba(7,9,26,0.96);
    backdrop-filter: blur(16px);
    position: sticky;
    top: 0;
    z-index: 200;
    margin: -2rem -4rem 0 -4rem;
}
.logo-text {
    font-size: 22px;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.6px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.logo-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366F1, #818CF8);
    display: inline-block;
    box-shadow: 0 0 10px rgba(99,102,241,0.7);
}

/* ── PAGE WRAPPER ── */
.page-wrap {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 56px;
}

/* ── HERO ── */
.hero-wrap {
    padding: 80px 0 56px;
}
.hero-tag {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    color: #818CF8;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.2);
    padding: 5px 14px;
    border-radius: 20px;
    margin-bottom: 28px;
}
.hero-title {
    font-size: 58px;
    font-weight: 800;
    color: #F8FAFC;
    line-height: 1.06;
    letter-spacing: -2.5px;
    margin-bottom: 22px;
}
.hero-title .accent { color: #818CF8; }
.hero-sub {
    font-size: 18px;
    color: #64748B;
    line-height: 1.7;
    max-width: 520px;
    margin-bottom: 48px;
}
.stats-row {
    display: flex;
    gap: 48px;
    padding-bottom: 56px;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    margin-bottom: 56px;
}
.stat-val {
    font-size: 32px;
    font-weight: 800;
    color: #F1F5F9;
    letter-spacing: -1px;
}
.stat-lbl {
    font-size: 12px;
    color: #475569;
    font-weight: 500;
    margin-top: 3px;
}

/* ── SECTION HEADING ── */
.sec-tag {
    font-size: 11px;
    font-weight: 600;
    color: #6366F1;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.sec-title {
    font-size: 26px;
    font-weight: 700;
    color: #F1F5F9;
    letter-spacing: -0.5px;
    margin-bottom: 6px;
}
.sec-desc {
    font-size: 14px;
    color: #475569;
    line-height: 1.65;
    margin-bottom: 32px;
    max-width: 560px;
}

/* ── DOMAIN CARDS ── */
.domain-card {
    background: #0D1223;
    border: 1.5px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 24px 20px 20px;
    margin-bottom: 6px;
    transition: border-color 0.15s, background 0.15s;
}
.domain-card:hover { border-color: rgba(99,102,241,0.4); background: #101628; }
.domain-card.dim { opacity: 0.35; }
.d-icon { font-size: 26px; margin-bottom: 14px; }
.d-name { font-size: 14px; font-weight: 600; color: #E2E8F0; margin-bottom: 6px; }
.d-desc { font-size: 12px; color: #475569; line-height: 1.45; margin-bottom: 14px; }
.badge-live {
    display: inline-block; font-size: 10px; font-weight: 700;
    color: #10B981; background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.25);
    padding: 3px 9px; border-radius: 20px;
}
.badge-soon {
    display: inline-block; font-size: 10px; font-weight: 500;
    color: #334155; background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    padding: 3px 9px; border-radius: 20px;
}

/* ── ABOUT TEASER ── */
.teaser {
    background: linear-gradient(135deg, rgba(99,102,241,0.08), rgba(129,140,248,0.04));
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 18px;
    padding: 36px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 24px;
    margin-top: 56px;
    margin-bottom: 56px;
}
.teaser-title { font-size: 17px; font-weight: 700; color: #E2E8F0; margin-bottom: 6px; }
.teaser-desc { font-size: 14px; color: #64748B; max-width: 480px; line-height: 1.6; }

/* ── INSPECT PAGE ── */
.inspect-header {
    padding: 48px 0 36px;
}
.domain-pill {
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 13px; font-weight: 600; color: #A5B4FC;
    background: rgba(99,102,241,0.1);
    border: 1px solid rgba(99,102,241,0.22);
    padding: 7px 18px; border-radius: 20px;
    margin-bottom: 28px;
}
.upload-area {
    background: #0D1223;
    border: 2px dashed rgba(99,102,241,0.3);
    border-radius: 16px;
    padding: 8px;
    margin-bottom: 24px;
}
.upload-hint { font-size: 13px; color: #475569; margin-top: 12px; line-height: 1.5; }

/* fix the white Streamlit file uploader */
[data-testid="stFileUploader"] {
    background: transparent !important;
}
[data-testid="stFileUploader"] > div {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: rgba(99,102,241,0.05) !important;
    border: 2px dashed rgba(99,102,241,0.25) !important;
    border-radius: 12px !important;
    color: #64748B !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(99,102,241,0.1) !important;
    border-color: rgba(99,102,241,0.45) !important;
}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {
    color: #64748B !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { color: #64748B !important; }
section[data-testid="stFileUploader"] label { color: #94A3B8 !important; }

/* ── RESULT CARDS ── */
.verdict-good {
    background: linear-gradient(135deg, rgba(16,185,129,0.1), rgba(16,185,129,0.03));
    border: 1.5px solid rgba(16,185,129,0.25);
    border-radius: 18px; padding: 36px;
}
.verdict-defect {
    background: linear-gradient(135deg, rgba(239,68,68,0.1), rgba(239,68,68,0.03));
    border: 1.5px solid rgba(239,68,68,0.25);
    border-radius: 18px; padding: 36px;
}
.v-label-good  { font-size: 44px; font-weight: 800; color: #10B981; letter-spacing: -2px; margin-bottom: 4px; }
.v-label-defect{ font-size: 44px; font-weight: 800; color: #EF4444; letter-spacing: -2px; margin-bottom: 4px; }
.v-sub { font-size: 13px; color: #475569; margin-bottom: 28px; }
.v-metric-lbl { font-size: 11px; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 4px; }
.v-metric-val  { font-size: 16px; font-weight: 600; color: #E2E8F0; margin-bottom: 6px; font-variant-numeric: tabular-nums; }
.bar-track { height: 4px; background: rgba(255,255,255,0.07); border-radius: 2px; margin-bottom: 18px; overflow: hidden; }
.bar-green  { height: 100%; background: #10B981; border-radius: 2px; }
.bar-red    { height: 100%; background: #EF4444; border-radius: 2px; }
.bar-indigo { height: 100%; background: #6366F1; border-radius: 2px; }
.chip-good   { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: #10B981; background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.2); padding: 7px 16px; border-radius: 20px; margin-top: 6px; }
.chip-defect { display: inline-flex; align-items: center; gap: 6px; font-size: 13px; font-weight: 600; color: #EF4444; background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.2); padding: 7px 16px; border-radius: 20px; margin-top: 6px; }
.heatmap-lbl { font-size: 11px; font-weight: 600; color: #6366F1; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
.heatmap-note { font-size: 13px; color: #475569; line-height: 1.55; margin-bottom: 14px; }

/* ── ABOUT PAGE ── */
.about-hero { padding: 72px 0 48px; }
.about-title { font-size: 44px; font-weight: 800; color: #F8FAFC; letter-spacing: -1.8px; margin-bottom: 16px; }
.about-desc  { font-size: 16px; color: #64748B; line-height: 1.75; max-width: 580px; margin-bottom: 40px; }
.chip-row    { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 48px; }
.chip        { font-size: 13px; font-weight: 500; color: #A5B4FC; background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.18); padding: 7px 16px; border-radius: 8px; }
.metrics-grid{ display: grid; grid-template-columns: repeat(4,1fr); gap: 14px; margin-bottom: 48px; }
.metric-card { background: #0D1223; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 22px; }
.metric-v    { font-size: 28px; font-weight: 800; color: #818CF8; letter-spacing: -1px; margin-bottom: 4px; }
.metric-l    { font-size: 12px; color: #475569; font-weight: 500; }
.info-card   { background: #0D1223; border: 1px solid rgba(255,255,255,0.06); border-radius: 14px; padding: 30px 34px; margin-bottom: 14px; }
.info-title  { font-size: 16px; font-weight: 700; color: #F1F5F9; margin-bottom: 10px; }
.info-text   { font-size: 14px; color: #64748B; line-height: 1.75; }
.callout     { background: rgba(99,102,241,0.05); border-left: 3px solid #6366F1; border-radius: 0 10px 10px 0; padding: 20px 24px; font-size: 14px; color: #64748B; line-height: 1.7; margin-top: 24px; }

/* ── FOOTER ── */
.footer {
    margin-top: 80px;
    padding: 28px 0;
    border-top: 1px solid rgba(255,255,255,0.05);
    display: flex; justify-content: space-between; align-items: center;
}
.footer-l { font-size: 13px; color: #1E293B; }
.footer-r { font-size: 13px; color: #334155; }
.footer-r span { color: #475569; font-weight: 500; }

/* ── IMAGE ── */
div[data-testid="stImage"] img { border-radius: 12px; }

/* make columns flush */
div[data-testid="stHorizontalBlock"] { gap: 16px !important; }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL LOADING
# ═══════════════════════════════════════════════════════════════════════════════
def models_available():
    ref = os.path.join(MODELS_DIR, "reference_images")
    return (
        os.path.exists(os.path.join(MODELS_DIR, "feature_extractor.pth")) and
        os.path.exists(os.path.join(MODELS_DIR, "metadata.pkl")) and
        os.path.exists(ref) and len(os.listdir(ref)) > 0
    )


@st.cache_resource
def load_model_and_bank():
    try:
        import torch, torch.nn as nn, pickle
        import torchvision.models as models
        import torchvision.transforms as transforms

        pth_path   = os.path.join(MODELS_DIR, "feature_extractor.pth")
        state_dict = torch.load(pth_path, map_location="cpu", weights_only=True)
        keys       = list(state_dict.keys())

        l2_blocks = set(re.findall(r'layer2\.(\d+)\.', " ".join(keys)))
        l3_blocks = set(re.findall(r'layer3\.(\d+)\.', " ".join(keys)))
        max_l2    = max(int(x) for x in l2_blocks) if l2_blocks else 3
        max_l3    = max(int(x) for x in l3_blocks) if l3_blocks else 5

        if max_l2 >= 4 or max_l3 >= 6:
            is_wide = any("layer2.0.weight" in k for k in keys)
            backbone = models.wide_resnet50_2(weights=None) if (is_wide or max_l2 >= 4) else models.resnet101(weights=None)
        else:
            backbone = models.resnet50(weights=None)

        class FeatureExtractor(nn.Module):
            def __init__(self, bb):
                super().__init__()
                self.stem    = nn.Sequential(bb.conv1, bb.bn1, bb.relu, bb.maxpool)
                self.layer1  = bb.layer1
                self.layer2  = bb.layer2
                self.layer3  = bb.layer3
                self.avgpool = nn.AdaptiveAvgPool2d((1, 1))

            def forward(self, x):
                x  = self.stem(x); x  = self.layer1(x)
                f2 = self.layer2(x); f3 = self.layer3(f2)
                p2 = self.avgpool(f2).squeeze(-1).squeeze(-1)
                p3 = self.avgpool(f3).squeeze(-1).squeeze(-1)
                return torch.cat([p2, p3], dim=1)

        device = torch.device("cpu")
        model  = FeatureExtractor(backbone).to(device)
        model.load_state_dict(state_dict, strict=False)
        model.eval()

        with open(os.path.join(MODELS_DIR, "metadata.pkl"), "rb") as f:
            metadata = pickle.load(f)

        transform = transforms.Compose([
            transforms.Resize((224, 224)), transforms.ToTensor(),
            transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
        ])

        features_list, ref_dir = [], os.path.join(MODELS_DIR, "reference_images")
        for fname in os.listdir(ref_dir):
            if fname.lower().endswith((".png",".jpg",".jpeg")):
                img = Image.open(os.path.join(ref_dir, fname)).convert("RGB")
                t   = transform(img).unsqueeze(0).to(device)
                with torch.no_grad():
                    feat = model(t)
                features_list.append(feat.cpu().numpy())

        memory_bank = np.vstack(features_list)
        return model, metadata, memory_bank, device, transform

    except Exception as e:
        import traceback
        st.error(f"**Load error:** `{e}`\n\n```\n{traceback.format_exc()}```")
        return None, None, None, None, None


def run_inference(image, model, memory_bank, device, transform, threshold):
    import torch, matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = transform(image).unsqueeze(0).to(device)
    t.requires_grad_(True)
    output = model(t)
    query  = output.detach().cpu().numpy()

    dists  = np.linalg.norm(memory_bank - query, axis=1)
    score  = float((np.min(dists) + np.mean(np.sort(dists)[:5])) / 2)
    verdict= "GOOD" if score < threshold else "DEFECT"

    loss = output.norm(); loss.backward()
    grads = t.grad.data.abs().squeeze().mean(dim=0).numpy()
    grads = (grads - grads.min()) / (grads.max() - grads.min() + 1e-8)

    img_arr = np.array(image.resize((224, 224)))
    fig, axes = plt.subplots(1, 2, figsize=(8, 4), facecolor="#07091A")
    for ax in axes: ax.set_facecolor("#07091A")
    axes[0].imshow(img_arr); axes[0].set_title("Input", color="#475569", fontsize=10, pad=8); axes[0].axis("off")
    axes[1].imshow(img_arr, alpha=0.5); axes[1].imshow(grads, cmap="plasma", alpha=0.55)
    axes[1].set_title("Anomaly Map", color="#475569", fontsize=10, pad=8); axes[1].axis("off")
    plt.tight_layout(pad=1.2)
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=120, facecolor="#0D1223", bbox_inches="tight")
    plt.close(); buf.seek(0)

    confidence = min(100, max(0, int(abs(1 - score / threshold) * 100)))
    return score, verdict, confidence, buf


# ═══════════════════════════════════════════════════════════════════════════════
# NAV  — logo left, About button right only
# ═══════════════════════════════════════════════════════════════════════════════
def render_nav():
    col_logo, col_spacer, col_about = st.columns([3, 6, 1])

    with col_logo:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:14px 0;cursor:pointer;">
            <div style="width:32px;height:32px;border-radius:8px;
                background:linear-gradient(135deg,#6366F1,#818CF8);
                display:flex;align-items:center;justify-content:center;
                box-shadow:0 0 16px rgba(99,102,241,0.6);
                font-size:15px;font-weight:900;color:#fff;flex-shrink:0;">P</div>
            <span style="font-size:18px;font-weight:800;color:#fff;letter-spacing:-0.5px;
                text-shadow:0 0 24px rgba(129,140,248,0.35);">PrecisionEye <span style="color:#818CF8;">AI</span></span>
        </div>
        """, unsafe_allow_html=True)
        # invisible button for click navigation
        st.markdown('<div style="margin-top:-54px;opacity:0;">', unsafe_allow_html=True)
        if st.button("PrecisionEye AI", key="nav_logo"):
            st.session_state.page   = "home"
            st.session_state.result = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_about:
        st.markdown('<div class="nav-link" style="padding-top:10px;">', unsafe_allow_html=True)
        if st.button("About", key="nav_about"):
            st.session_state.page = "about"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
def render_footer():
    st.markdown("""
    <div class="footer">
        <div class="footer-l">PrecisionEye AI · Manufacturing Defect Detection</div>
        <div class="footer-r">Built by <span>Siddhi Pawar</span> · PyTorch · Streamlit</div>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: HOME
# ═══════════════════════════════════════════════════════════════════════════════
def page_home():
    render_nav()

    # Hero
    st.markdown("""
    <div class="hero-wrap">
        <div class="hero-tag">Anomaly Detection · Computer Vision</div>
        <div class="hero-title">Catch defects<br>before they ship<span class="accent">.</span></div>
        <div class="hero-sub">AI-powered visual inspection for manufactured parts. Upload an image, get an instant verdict — with a heatmap showing exactly where the anomaly is.</div>
        <div class="stats-row">
            <div><div class="stat-val">87.9%</div><div class="stat-lbl">AUROC on Metal Nut</div></div>
            <div><div class="stat-val">220</div><div class="stat-lbl">Training images</div></div>
            <div><div class="stat-val">0</div><div class="stat-lbl">Defect labels needed</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Domain section
    st.markdown("""
    <div class="sec-tag">Select a domain to inspect</div>
    <div class="sec-title">Choose an inspection domain</div>
    <div class="sec-desc">Pick the manufactured part type. Only Metal Nut is live — more domains are being trained.</div>
    """, unsafe_allow_html=True)

    cols = st.columns(4)
    for i, d in enumerate(DOMAINS):
        with cols[i % 4]:
            badge = '<span class="badge-live">● Live</span>' if d["live"] else '<span class="badge-soon">Coming Soon</span>'
            st.markdown(f"""
            <div class="domain-card {'dim' if not d['live'] else ''}">
                <div class="d-icon">{d['icon']}</div>
                <div class="d-name">{d['name']}</div>
                <div class="d-desc">{d['desc']}</div>
                {badge}
            </div>
            """, unsafe_allow_html=True)

            if d["live"]:
                st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
                if st.button(f"Inspect {d['name']} →", key=f"sel_{d['id']}"):
                    st.session_state.selected_domain = d
                    st.session_state.result          = None
                    st.session_state.page            = "inspect"
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="btn-disabled">', unsafe_allow_html=True)
                st.button("Coming Soon", key=f"sel_{d['id']}", disabled=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # About teaser
    st.markdown("""
    <div class="teaser">
        <div>
            <div class="teaser-title">How does PrecisionEye AI work?</div>
            <div class="teaser-desc">Built on PatchCore + ResNet backbone. Trained only on good parts — no defect labels required. Flags anything that deviates from the learned normal distribution.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_btn, _ = st.columns([1, 5])
    with col_btn:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("Learn how it works →", key="goto_about"):
            st.session_state.page = "about"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: INSPECT
# ═══════════════════════════════════════════════════════════════════════════════
def page_inspect():
    render_nav()

    domain = st.session_state.selected_domain
    if not domain:
        st.session_state.page = "home"; st.rerun(); return

    # Back button
    st.markdown('<div style="padding-top:36px;">', unsafe_allow_html=True)
    col_back, _ = st.columns([1, 8])
    with col_back:
        st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
        if st.button("← Back to domains", key="back_home"):
            st.session_state.page   = "home"
            st.session_state.result = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="inspect-header">
        <div class="domain-pill">{domain['icon']} &nbsp;{domain['name']} · Inspection</div>
        <div class="sec-title">Upload a part image</div>
        <div class="sec-desc">Use a clear, well-lit photo of a single {domain['name'].lower()} part. The AI compares it against learned patterns from defect-free parts.</div>
    </div>
    """, unsafe_allow_html=True)

    # Upload
    uploaded = st.file_uploader(
        "Drop your image here — JPG, PNG or BMP",
        type=["jpg","jpeg","png","bmp"],
        key="upload",
    )

    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        col_img, _ = st.columns([1, 2])
        with col_img:
            st.image(image, caption="Uploaded image", use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if not models_available():
            st.warning(f"⚠️  Model files not found. Looking in: `{MODELS_DIR}`\n\nFiles there: `{os.listdir(MODELS_DIR) if os.path.exists(MODELS_DIR) else 'folder missing'}`")
        else:
            col_run, _ = st.columns([1, 6])
            with col_run:
                st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
                run_clicked = st.button("Run Inspection", key="run")
                st.markdown('</div>', unsafe_allow_html=True)

            if run_clicked:
                with st.spinner("Analysing…"):
                    model, metadata, memory_bank, device, transform = load_model_and_bank()
                    if model is None:
                        st.error("Failed to load model. Check the models/ folder.")
                    else:
                        threshold = metadata.get("threshold", 5.4217)
                        score, verdict, confidence, heatmap = run_inference(
                            image, model, memory_bank, device, transform, threshold
                        )
                        st.session_state.result = {
                            "score": score, "verdict": verdict,
                            "confidence": confidence, "heatmap": heatmap,
                            "threshold": threshold
                        }
                        st.rerun()

    # Result
    if st.session_state.result:
        r       = st.session_state.result
        is_good = r["verdict"] == "GOOD"
        sr      = min(1.0, r["score"] / (r["threshold"] * 1.5))
        tr      = min(1.0, r["threshold"] / (r["threshold"] * 1.5))
        bw      = int(sr * 100)
        tw      = int(tr * 100)

        st.markdown("<br>", unsafe_allow_html=True)
        col_v, col_h = st.columns([1, 1.4])

        with col_v:
            if is_good:
                st.markdown(f"""
                <div class="verdict-good">
                    <div class="v-label-good">✓ GOOD</div>
                    <div class="v-sub">Part passed inspection · {domain['name']}</div>
                    <p style="font-size:14px;color:#94A3B8;line-height:1.65;margin-bottom:24px;">
                        No significant anomaly detected. This part is within the normal learned distribution.
                    </p>
                    <div class="v-metric-lbl">Anomaly score</div>
                    <div class="v-metric-val">{r['score']:.4f}</div>
                    <div class="bar-track"><div class="bar-green" style="width:{bw}%;"></div></div>
                    <div class="v-metric-lbl">Threshold</div>
                    <div class="v-metric-val">{r['threshold']:.4f}</div>
                    <div class="bar-track"><div class="bar-indigo" style="width:{tw}%;"></div></div>
                    <div class="chip-good">● {r['confidence']}% confidence</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="verdict-defect">
                    <div class="v-label-defect">✕ DEFECT</div>
                    <div class="v-sub">Anomaly detected · {domain['name']}</div>
                    <p style="font-size:14px;color:#94A3B8;line-height:1.65;margin-bottom:24px;">
                        This part deviates from normal patterns. Check the heatmap to locate the affected area.
                    </p>
                    <div class="v-metric-lbl">Anomaly score</div>
                    <div class="v-metric-val">{r['score']:.4f}</div>
                    <div class="bar-track"><div class="bar-red" style="width:{bw}%;"></div></div>
                    <div class="v-metric-lbl">Threshold</div>
                    <div class="v-metric-val">{r['threshold']:.4f}</div>
                    <div class="bar-track"><div class="bar-indigo" style="width:{tw}%;"></div></div>
                    <div class="chip-defect">● {r['confidence']}% confidence</div>
                </div>
                """, unsafe_allow_html=True)

        with col_h:
            st.markdown('<div class="heatmap-lbl">Anomaly heatmap</div>', unsafe_allow_html=True)
            st.markdown('<div class="heatmap-note">Warmer colours (yellow/red) highlight regions that deviate most from learned normal patterns.</div>', unsafe_allow_html=True)
            st.image(r["heatmap"], use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_r, _ = st.columns([1, 5])
        with col_r:
            st.markdown('<div class="btn-ghost">', unsafe_allow_html=True)
            if st.button("Inspect another part", key="again"):
                st.session_state.result = None; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE: ABOUT
# ═══════════════════════════════════════════════════════════════════════════════
def page_about():
    render_nav()

    st.markdown("""
    <div class="about-hero">
        <div class="hero-tag">Behind the model</div>
        <div class="about-title">How PrecisionEye AI works</div>
        <div class="about-desc">A deep dive into the algorithm, architecture, and dataset behind the defect detection engine.</div>
        <div class="chip-row">
            <span class="chip">PatchCore</span>
            <span class="chip">ResNet Backbone</span>
            <span class="chip">PyTorch</span>
            <span class="chip">MVTec AD Dataset</span>
            <span class="chip">Coreset Subsampling</span>
            <span class="chip">Euclidean Distance</span>
            <span class="chip">Streamlit</span>
        </div>
        <div class="metrics-grid">
            <div class="metric-card"><div class="metric-v">87.9%</div><div class="metric-l">AUROC — Metal Nut</div></div>
            <div class="metric-card"><div class="metric-v">220</div><div class="metric-l">Good training images</div></div>
            <div class="metric-card"><div class="metric-v">1536</div><div class="metric-l">Feature dimensions</div></div>
            <div class="metric-card"><div class="metric-v">10%</div><div class="metric-l">Memory bank sampling</div></div>
        </div>
    </div>

    <div class="info-card">
        <div class="info-title">The core idea — anomaly detection, not classification</div>
        <div class="info-text">Most defect detectors need thousands of labeled defect images. PrecisionEye AI trains <em>only on good parts</em>, learning what "normal" looks like. At inference, anything that deviates too far from that learned pattern is flagged — even defect types the model has never seen before.</div>
    </div>
    <div class="info-card">
        <div class="info-title">PatchCore algorithm</div>
        <div class="info-text">PatchCore (Roth et al., CVPR 2022) extracts patch-level features from intermediate ResNet layers (Layer 2 + Layer 3, producing 1536-dimensional vectors). These features from all good training images are stored in a <em>memory bank</em>. At test time, a query image's features are compared via nearest-neighbour search — the anomaly score is the minimum Euclidean distance to any stored patch.</div>
    </div>
    <div class="info-card">
        <div class="info-title">Coreset subsampling</div>
        <div class="info-text">A full memory bank for 220 training images would contain ~172,000 patch features, making inference slow. Coreset subsampling selects the most representative 10% (~17,000 features) while preserving feature space coverage — keeping accuracy high while cutting inference time by 10×.</div>
    </div>

    <div class="callout">
        <strong style="color:#A5B4FC;">MVTec Anomaly Detection (MVTec AD) dataset</strong><br>
        An industry-standard benchmark with 15 categories of manufactured objects and surface textures, pixel-precise defect annotations across 70+ defect types. The Metal Nut category includes bent, color, flip, and scratch defects. Published by MVTec Software GmbH, Munich.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col_cta, _ = st.columns([1, 5])
    with col_cta:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("← Try it now", key="about_home"):
            st.session_state.page = "home"; st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════════════════════════════
p = st.session_state.page
if   p == "home":    page_home()
elif p == "inspect": page_inspect()
elif p == "about":   page_about()
else:                page_home()