



import streamlit as st
import os
import pandas as pd
from PIL import Image
from dotenv import load_dotenv
from agent import analyze_claim

# 1. Page Configuration
st.set_page_config(
    page_title="Multi-Modal Damage Claim Verification",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# 2. Inject Custom CSS for Premium Styling
custom_css = """
<style>
    /* Main body background & font family */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=Outfit:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Sleek Title Gradient */
    .title-gradient {
        background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 50%, #f472b6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #94a3b8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* Styled container for metrics */
    div[data-testid="metric-container"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        border-color: #475569;
    }
    
    div[data-testid="stMetricValue"] > div {
        font-size: 1.8rem;
        font-weight: 700;
        color: #f8fafc;
    }
    
    div[data-testid="stMetricLabel"] > label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }
    
    /* Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
        color: #ffffff;
        font-weight: 600;
        font-size: 1rem;
        padding: 10px 24px;
        border: None;
        border-radius: 8px;
        box-shadow: 0 4px 14px 0 rgba(79, 70, 229, 0.4);
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #3b82f6 0%, #6366f1 100%);
        box-shadow: 0 6px 20px 0 rgba(99, 102, 241, 0.5);
        transform: translateY(-1px);
        color: #ffffff;
    }
    
    div.stButton > button:active {
        transform: translateY(1px);
    }
    
    /* Image Preview Container */
    .img-preview-box {
        border: 1px solid #334155;
        background-color: #0f172a;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 10px;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# 3. Sidebar setup
st.sidebar.markdown("### ⚙️ System Configuration")

# API Key input
sidebar_key = st.sidebar.text_input("Gemini API Key", type="password", placeholder="Enter Gemini API Key...")
api_key = sidebar_key if sidebar_key else os.getenv("GEMINI_API_KEY", "")

if not api_key or api_key == "your_api_key_here":
    st.sidebar.warning("⚠️ API Key is missing. Please enter it here or define it in your .env file.")
else:
    st.sidebar.success("🔑 API Key configured successfully.")

# CSV User History Uploader
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 User History Database")
history_file = st.sidebar.file_uploader("Upload user_history.csv", type=["csv"])

if history_file is not None:
    try:
        df = pd.read_csv(history_file)
        st.session_state["history_df"] = df
        st.sidebar.success(f"✅ Uploaded history: {len(df)} records found.")
    except Exception as e:
        st.sidebar.error(f"Error loading CSV: {e}")
else:
    # Try to load default from data/user_history.csv
    default_csv = "data/user_history.csv"
    if "history_df" not in st.session_state:
        if os.path.exists(default_csv):
            try:
                st.session_state["history_df"] = pd.read_csv(default_csv)
                st.sidebar.info("ℹ️ Loaded default history (5 records).")
            except Exception as e:
                st.session_state["history_df"] = None
        else:
            st.session_state["history_df"] = None

# Sidebar Info Box
st.sidebar.info("""
**Expected CSV Columns:**
- `user_id` (str)
- `past_claim_count` (int)
- `accept_claim` (int)
- `manual_review_claim` (int)
- `rejected_claim` (int)
- `last_90_days_claim_count` (int)
- `history_flags` (str)
- `history_summary` (str)
""")


# 4. Main Area Header
st.markdown("<div class='title-gradient'>Multi-Modal Damage Claim Verification</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Automated visual claim verification and risk flagging using Google Gemini 3.1 Flash Lite</div>", unsafe_allow_html=True)

# Main columns
col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.markdown("### 📝 Enter Claim Details")
    
    user_id = st.text_input("User ID", value="user_001")
    claim_object = st.selectbox("Claim Object", options=["car", "laptop", "package"])
    user_claim = st.text_area("Damage Description", placeholder="e.g. There is a deep dent on the driver door panel...", height=120)
    
    uploaded_files = st.file_uploader("Upload Damage Images", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True)

with col_right:
    st.markdown("### 🖼️ Uploaded Images Preview")
    if uploaded_files:
        for file in uploaded_files:
            try:
                img = Image.open(file)
                # Image ID is the file name without extension
                image_id = os.path.splitext(file.name)[0]
                
                # Show image with styled container
                st.markdown(f"<div class='img-preview-box'>", unsafe_allow_html=True)
                st.image(img, caption=f"ID: {image_id}", width="stretch")
                st.markdown("</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error loading {file.name}: {e}")
    else:
        st.info("No images uploaded yet. Previews will appear here.")

# Large centered button
st.markdown("<br>", unsafe_allow_html=True)
c_left, c_center, c_right = st.columns([2, 2, 2])
with c_center:
    analyze_btn = st.button("Analyze Claim", width="stretch")

# 5. Analysis Trigger
if analyze_btn:
    if not api_key or api_key == "your_api_key_here":
        st.error("❌ Error: Gemini API Key is missing. Provide it in the sidebar or check your `.env` configuration.")
    elif not user_claim.strip():
        st.error("❌ Error: Damage Description cannot be empty.")
    elif not uploaded_files:
        st.error("❌ Error: Please upload at least one image of the damage.")
    else:
        # User history lookup
        user_history_row = None
        if "history_df" in st.session_state and st.session_state["history_df"] is not None:
            history_df = st.session_state["history_df"]
            matching_rows = history_df[history_df["user_id"] == user_id]
            if not matching_rows.empty:
                user_history_row = matching_rows.iloc[0]
        
        # Load image details
        pil_images = []
        image_ids_list = []
        for file in uploaded_files:
            try:
                img = Image.open(file)
                pil_images.append(img)
                image_ids_list.append(os.path.splitext(file.name)[0])
            except Exception as e:
                st.error(f"Error parsing image {file.name}: {e}")
        
        image_ids_str = ";".join(image_ids_list)
        
        # Call agent
        if pil_images:
            with st.spinner("Analyzing with Gemini 3.1 Flash Lite..."):
                result = analyze_claim(
                    api_key=api_key,
                    pil_images=pil_images,
                    image_ids=image_ids_str,
                    user_claim=user_claim,
                    claim_object=claim_object,
                    user_history_row=user_history_row
                )
                st.session_state["last_result"] = result
                st.success("✅ Analysis completed successfully!")

# 6. Results Display
if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    
    st.markdown("---")
    st.markdown("### 📊 Verification Analysis Results")
    
    # 1. Verdict Banner
    status = result.claim_status
    if status == "supported":
        st.success(f"### Claim Verdict: SUPPORTED", icon="✅")
    elif status == "contradicted":
        st.error(f"### Claim Verdict: CONTRADICTED", icon="❌")
    else:
        st.warning(f"### Claim Verdict: NOT ENOUGH INFORMATION", icon="⚠️")
        
    # 2. Metric Cards Row
    st.markdown("<br>", unsafe_allow_html=True)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.metric("Severity", result.severity.upper())
    with m_col2:
        st.metric("Valid Image", "YES" if result.valid_image else "NO")
    with m_col3:
        st.metric("Evidence Standard Met", "MET" if result.evidence_standard_met else "NOT MET")
    with m_col4:
        st.metric("Issue Type", result.issue_type.replace("_", " ").upper())
        
    # 3. Two columns for detailed verification
    st.markdown("<br>", unsafe_allow_html=True)
    res_col_left, res_col_right = st.columns(2, gap="medium")
    
    with res_col_left:
        st.markdown("#### Detail Indicators")
        st.markdown(f"**Object Part Detected:** `{result.object_part}`")
        st.markdown(f"**Supporting Image IDs:** `{result.supporting_image_ids}`")
        
        st.markdown("**Risk Assessment:**")
        if result.risk_flags != "none":
            st.warning(f"⚠️ **Risk Flags:** {result.risk_flags}")
        else:
            st.success("✅ **Risk Flags:** None")
            
    with res_col_right:
        st.markdown("#### Justification & Context")
        st.info(f"**Justification:**\n{result.claim_status_justification}")
        st.caption(f"**Evidence Assessment Reason:** {result.evidence_standard_met_reason}")
        
    # 4. Raw JSON Expander
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("Raw Analysis JSON"):
        result_dict = result.model_dump() if hasattr(result, "model_dump") else result.dict()
        st.json(result_dict)
