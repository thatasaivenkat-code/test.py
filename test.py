# ==============================================================================
# APP: VAYU VEGA SMART MERGE - ULTIMATE CUSTOM EDITION (v21.0)
# THEME: PURE BLACK & NEON GOLD (INDIVIDUAL DATA CONTROL)
# ==============================================================================

import streamlit as st
import fitz  # PyMuPDF
import os
import io
import gc
from datetime import datetime
from PIL import Image
from io import BytesIO

# ------------------------------------------------------------------------------
# 1. SYSTEM COORDINATES
# ------------------------------------------------------------------------------
CONFIG = {
    "DTDC": {
        "notif": {"x": 20, "y": 444, "w": 278, "h": 82},
        "logo": {"x": 371, "y": 22, "w": 100, "h": 33},
        "data": {"x": 150, "y": 631, "w": 200, "h": 42},
        "f_msg": 8.5, "f_data": 10
    },
    "Delhivery": {
        "notif": {"x": 24, "y": 302, "w": 249, "h": 82},
        "logo": {"x": 189, "y": 17, "w": 81, "h": 30},
        "data": {"x": 24, "y": 270, "w": 249, "h": 40},
        "f_msg": 8, "f_data": 10
    }
}

# ------------------------------------------------------------------------------
# 2. ULTRA BLACK & GOLD UI STYLING
# ------------------------------------------------------------------------------
def apply_ultra_black_theme():
    st.markdown("""
        <style>
        /* Pure Black Background */
        .stApp {
            background-color: #000000;
            color: #FFFFFF;
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #0A0A0A;
            border-right: 1px solid #1A1A1A;
        }
        
        /* Title with Neon Glow */
        .main-title {
            color: #FFD700;
            font-size: 45px;
            font-weight: 900;
            text-align: center;
            text-shadow: 0 0 20px rgba(255, 215, 0, 0.4);
            margin-bottom: 5px;
        }

        /* Glassmorphism Label Cards */
        .label-card {
            background: #0D0D0D;
            border: 1px solid #222;
            border-radius: 18px;
            padding: 20px;
            margin-bottom: 25px;
            transition: all 0.3s ease;
        }
        .label-card:hover {
            border-color: #FFD700;
            box-shadow: 0 0 25px rgba(255, 215, 0, 0.15);
            transform: scale(1.01);
        }

        /* Bold Labels */
        div[data-testid="stCheckbox"] label p {
            color: #FFD700 !important;
            font-weight: 800 !important;
            font-size: 15px !important;
        }
        
        .stTextInput>div>div>input {
            background-color: #111 !important;
            color: #FFD700 !important;
            border: 1px solid #333 !important;
        }

        /* Gold Action Button */
        .stButton>button {
            background: linear-gradient(45deg, #FFD700, #B8860B);
            color: #000 !important;
            border: none;
            border-radius: 12px;
            height: 3.8rem;
            font-weight: 900;
            font-size: 18px;
            letter-spacing: 1px;
            width: 100%;
        }
        .stButton>button:hover {
            box-shadow: 0 0 30px rgba(255, 215, 0, 0.5);
            transform: translateY(-2px);
        }
        
        /* Badges */
        .badge {
            background: rgba(255, 215, 0, 0.1);
            color: #FFD700;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            border: 1px solid #FFD700;
        }
        </style>
    """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# 3. PDF CORE ENGINE
# ------------------------------------------------------------------------------
def clear_memory():
    gc.collect()

@st.cache_data
def render_page_preview(pdf_data, p_idx):
    doc = fitz.open(stream=pdf_data, filetype="pdf")
    page = doc[p_idx]
    pix = page.get_pixmap(matrix=fitz.Matrix(0.75, 0.75))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    doc.close()
    return img

def process_labels_engine(pdf_bytes, page_configs, logos_dict, courier, notif_msg, toggles):
    try:
        src_pdf = fitz.open(stream=pdf_bytes, filetype="pdf")
        out_pdf = fitz.open()
        cfg = CONFIG[courier]
        
        prog = st.progress(0)
        
        for idx, (p_idx, p_set) in enumerate(page_configs.items()):
            # Single page isolation
            temp_doc = fitz.open()
            temp_doc.insert_pdf(src_pdf, from_page=p_idx, to_page=p_idx)
            page = temp_doc[0]

            # 1. Global Notification Box
            if toggles['notif'] and notif_msg:
                n = cfg['notif']
                n_rect = fitz.Rect(n['x'], n['y'], n['x'] + n['w'], n['y'] + n['h'])
                page.draw_rect(n_rect, color=(0,0,0), fill=(1,1,1), width=0.8)
                page.insert_textbox(
                    fitz.Rect(n_rect.x0+4, n_rect.y0+4, n_rect.x1-4, n_rect.y1-4),
                    notif_msg, fontsize=cfg['f_msg']
                )

            # 2. Individual Branding
            if p_set['is_branded']:
                # Logo Logic
                l_data = logos_dict.get(p_set['logo_name'])
                if l_data:
                    l = cfg['logo']
                    l_rect = fitz.Rect(l['x'], l['y'], l['x'] + l['w'], l['y'] + l['h'])
                    page.draw_rect(l_rect, color=(1,1,1), fill=(1,1,1))
                    page.insert_image(l_rect, stream=l_data)
                
                # Custom Data Logic (WT & RS)
                if p_set['show_wt'] or p_set['show_rs']:
                    d = cfg['data']
                    d_rect = fitz.Rect(d['x'], d['y'], d['x'] + d['w'], d['y'] + d['h'])
                    page.draw_rect(d_rect, color=(0,0,0), fill=(1,1,1), width=1)
                    
                    parts = []
                    if p_set['show_wt']: parts.append(f"WT: {p_set['wt_val']} KG")
                    if p_set['show_rs']: parts.append(f"RS: {p_set['rs_val']}/-")
                    
                    page.insert_text(
                        (d_rect.x0 + 15, d_rect.y0 + 26),
                        " | ".join(parts),
                        fontsize=cfg['f_data'], color=(0,0,0)
                    )

            out_pdf.insert_pdf(temp_doc)
            temp_doc.close()
            prog.progress((idx + 1) / len(page_configs))

        final_out = out_pdf.tobytes()
        src_pdf.close(); out_pdf.close()
        clear_memory()
        return final_out
    except Exception as e:
        st.error(f"Engine Crash: {e}")
        return None

# ------------------------------------------------------------------------------
# 4. MAIN INTERFACE
# ------------------------------------------------------------------------------
def main():
    apply_ultra_black_theme()
    
    # Sidebar Setup
    with st.sidebar:
        st.markdown("<h1 style='color:#FFD700;'>ADMIN PANEL</h1>", unsafe_allow_html=True)
        partner = st.selectbox("Partner:", ["DTDC", "Delhivery"])
        
        st.divider()
        st.subheader("🖼️ Branding Assets")
        uploaded_logos = st.file_uploader("Upload Logos:", type=['png','jpg','jpeg'], accept_multiple_files=True)
        
        logos_map = {}
        if uploaded_logos:
            for f in uploaded_logos:
                b = f.read()
                logos_map[f.name] = b
                st.image(b, caption=f.name, width=60)
        
        default_logo = None
        if logos_map:
            default_logo = st.selectbox("Global Default Logo:", options=list(logos_map.keys()))

        st.divider()
        notif_on = st.toggle("Enable Note Box", value=True)
        notif_msg = st.text_area("Note Content:", "Vayu Vega Logistics \nIMPORTANT: Take unboxing video. No claim without video proof.", height=100)

    # Main UI Header
    st.markdown("<h1 class='main-title'>VAYU VEGA SMART MERGE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#888;'>Premium Enterprise Label Branding System</p>", unsafe_allow_html=True)
    
    # Global Defaults (Used for Autofill)
    st.subheader("⚡ Quick Batch Settings")
    c1, c2 = st.columns(2)
    def_wt = c1.text_input("Global Default WT:", "0.500")
    def_rs = c2.text_input("Global Default Price:", "150")

    st.divider()

    # File Input
    main_pdf_file = st.file_uploader("📂 Drop Multi-Page PDF Label", type=['pdf'])

    if main_pdf_file:
        pdf_raw = main_pdf_file.read()
        doc = fitz.open(stream=pdf_raw, filetype="pdf")
        p_count = len(doc)
        
        st.markdown(f"<span class='badge'>FILE STATUS: {p_count} LABELS DETECTED</span>", unsafe_allow_html=True)
        
        # Selection Logic Grid
        page_configs = {}
        
        # Grid Display (3 cols)
        for r in range(0, p_count, 3):
            cols = st.columns(3)
            for c in range(3):
                idx = r + c
                if idx < p_count:
                    with cols[c]:
                        st.markdown('<div class="label-card">', unsafe_allow_html=True)
                        
                        # Preview
                        prev = render_page_preview(pdf_raw, idx)
                        st.image(prev, use_container_width=True)
                        
                        # BRANDING TOGGLE
                        brand_on = st.checkbox(f"BRAND LABEL #{idx+1}", value=True, key=f"b_{idx}")
                        
                        # SELECTIVE LOGO
                        l_sel = st.selectbox(f"Logo {idx+1}:", options=list(logos_map.keys()), 
                                            index=list(logos_map.keys()).index(default_logo) if default_logo else 0,
                                            key=f"ls_{idx}")
                        
                        # SELECTIVE DATA (NEW FEATURE)
                        st.divider()
                        sc1, sc2 = st.columns(2)
                        p_wt_on = sc1.checkbox("WT", value=True, key=f"w_on_{idx}")
                        p_rs_on = sc2.checkbox("RS", value=True, key=f"r_on_{idx}")
                        
                        p_wt_val = st.text_input(f"WT {idx+1}:", def_wt, key=f"wv_{idx}")
                        p_rs_val = st.text_input(f"RS {idx+1}:", def_rs, key=f"rv_{idx}")
                        
                        page_configs[idx] = {
                            "is_branded": brand_on,
                            "logo_name": l_sel,
                            "show_wt": p_wt_on,
                            "show_rs": p_rs_on,
                            "wt_val": p_wt_val,
                            "rs_val": p_rs_val
                        }
                        st.markdown('</div>', unsafe_allow_html=True)
        doc.close()

        # Generate Button
        st.divider()
        if st.button("🔥 START GENERATING BRANDED LABELS"):
            if not logos_map:
                st.error("Error: Please upload at least one logo in the Sidebar library.")
            else:
                with st.spinner("Executing batch merge..."):
                    toggles = {'notif': notif_on}
                    final_pdf = process_labels_engine(pdf_raw, page_configs, logos_map, partner, notif_msg, toggles)
                    
                    if final_pdf:
                        st.balloons()
                        st.download_button(
                            label="📥 DOWNLOAD FINAL PRO PDF",
                            data=final_pdf,
                            file_name=f"VayuVega_Pro_{datetime.now().strftime('%H%M%S')}.pdf",
                            mime="application/pdf"
                        )

# ------------------------------------------------------------------------------
# 5. RUN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"Fatal System Error: {e}")

# ==============================================================================
# END OF CODE - v21.0
# ==============================================================================