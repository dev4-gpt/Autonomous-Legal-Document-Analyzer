import streamlit as st
st.set_page_config(page_title="Legal Analyzer", layout="wide", initial_sidebar_state="expanded")
import os
import json
from collections import Counter
import shutil
import time
from pathlib import Path

# --- Constants and Config ---
ANALYSIS_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'analysis')
RISK_COLORS = {
    "Low": ("#A8E6CF", "🟢"),
    "Medium": ("#FFF9B0", "🟡"),
    "High": ("#FF8C94", "🔴"),
    "Unknown": ("#B0BEC5", "⚪")
}
DARK_BG = "#121212"
TEXT_COLOR = "#EAEAEA"
FONT_FAMILY = "'Inter', 'Roboto', 'Segoe UI', 'Arial', sans-serif"
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), '..', 'data', 'uploads')

# --- Custom CSS for dark theme and font ---
st.markdown(f"""
    <style>
    body, .stApp {{
        background-color: {DARK_BG} !important;
        color: {TEXT_COLOR} !important;
        font-family: {FONT_FAMILY} !important;
    }}
    .sidebar .sidebar-content {{
        background: {DARK_BG};
    }}
    .metric-label, .metric-value {{
        color: {TEXT_COLOR} !important;
    }}
    .css-1v0mbdj, .css-1d391kg, .css-1cpxqw2 {{
        color: {TEXT_COLOR} !important;
    }}
    .stExpanderHeader {{
        font-size: 1.1rem;
        font-weight: 600;
    }}
    .stCheckbox > label {{
        color: {TEXT_COLOR} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Helper Functions ---
def list_contracts():
    """List all analyzed contracts (JSON files) in the analysis directory."""
    if not os.path.exists(ANALYSIS_DIR):
        return []
    return sorted([f for f in os.listdir(ANALYSIS_DIR) if f.endswith('.json')], reverse=True)

def load_analysis(filename):
    """Load analysis JSON for a contract."""
    with open(os.path.join(ANALYSIS_DIR, filename), 'r') as f:
        return json.load(f)

def get_risk_color(risk):
    risk_level = risk.split()[0].capitalize() if risk else "Unknown"
    return RISK_COLORS.get(risk_level, RISK_COLORS["Unknown"])

def render_clause_card(clause, text, risk, marked_for_revision):
    color, emoji = get_risk_color(risk)
    with st.expander(f"{emoji} {clause}  ", expanded=False):
        st.markdown(f"<div style='background-color:{color};padding:10px;border-radius:8px;color:#222;'>"
                    f"<b>Risk:</b> <span style='font-weight:600'>{risk}</span>"
                    f"</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-top:10px;white-space:pre-wrap'>{text}</div>", unsafe_allow_html=True)
        st.checkbox("Mark for Revision", key=f"revise_{clause}", value=marked_for_revision)

def compute_overall_risk(risks):
    # Simple logic: highest risk present determines overall
    if "High" in risks:
        return "High"
    elif "Medium" in risks:
        return "Medium"
    elif "Low" in risks:
        return "Low"
    return "Unknown"

def filter_clauses(clauses, risks, search, risk_filters):
    filtered = []
    for clause, text in clauses.items():
        risk = risks.get(clause, "Unknown")
        if search and search.lower() not in clause.lower() and search.lower() not in text.lower():
            continue
        if risk_filters and risk.split()[0] not in risk_filters:
            continue
        filtered.append((clause, text, risk))
    return filtered

def run_pipeline_on_upload(uploaded_file_path):
    """
    Run the full pipeline (parser, embedder, agent) on the uploaded file.
    This assumes watcher.py logic is available as import or function.
    """
    # Import pipeline modules
    from src import parser, embedder, agent
    # 1. Parse
    text, doc_id = parser.parse_file(uploaded_file_path)
    # 2. Embed
    embedder.chunk_and_embed(text, doc_id)
    # 3. Analyze
    result = agent.analyze_contract(text, doc_id)
    # 4. Save analysis JSON
    analysis_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'analysis')
    Path(analysis_dir).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(analysis_dir, doc_id + '.json'), 'w') as f:
        json.dump(result, f, indent=2)
    return doc_id + '.json'

# --- Main App ---
def main():
    contracts = list_contracts()
    if not contracts:
        st.info("No analyzed contracts found.")
        return

    # --- Sidebar ---
    with st.sidebar:
        st.title("📄 Contracts")
        selected = st.selectbox("Select a contract to view analysis:", contracts)
        data = load_analysis(selected)
        st.markdown("---")
        st.subheader("Contract Overview")
        st.metric("Type", data.get("contract_type", "Unknown"))
        st.markdown(f"<div style='color:{TEXT_COLOR};margin-bottom:8px'><b>Summary:</b><br>{data.get('summary', '')}</div>", unsafe_allow_html=True)
        st.markdown("---")
        st.caption("Upload new contracts to /data/uploads/ and re-run analysis.")
        # --- Batch File Upload ---
        uploaded_files = st.file_uploader(
            "Upload contracts (PDF, DOCX, TXT, HTML)",
            type=["pdf", "docx", "txt", "html"],
            help="Upload one or more contracts for analysis.",
            accept_multiple_files=True
        )
        if uploaded_files:
            progress = st.progress(0, text="Starting batch analysis...")
            status_msgs = []
            for idx, uploaded_file in enumerate(uploaded_files):
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                try:
                    with st.spinner(f"Analyzing {uploaded_file.name}..."):
                        new_json = run_pipeline_on_upload(file_path)
                    status_msgs.append(f"✅ {uploaded_file.name} analyzed successfully.")
                except Exception as e:
                    status_msgs.append(f"❌ {uploaded_file.name} failed: {e}")
                progress.progress((idx + 1) / len(uploaded_files), text=f"Processed {idx + 1} of {len(uploaded_files)} files...")
            progress.empty()
            for msg in status_msgs:
                st.write(msg)
            st.success("Batch analysis complete! Reloading...")
            time.sleep(1)
            st.experimental_rerun()

    # --- Main Panel ---
    st.title("Autonomous Legal Document Analyzer")
    st.markdown("<hr style='border:1px solid #333'>", unsafe_allow_html=True)

    # --- Risk Summary Dashboard ---
    clause_risks = [data["risks"].get(clause, "Unknown").split()[0] for clause in data["clauses"]]
    risk_counts = Counter(clause_risks)
    total_clauses = len(data["clauses"])
    overall_risk = compute_overall_risk(clause_risks)
    col1, col2, col3, col4 = st.columns([1,1,1,2])
    col1.metric("Total Clauses", total_clauses)
    col2.metric("High Risk", risk_counts.get("High", 0), delta_color="inverse")
    col3.metric("Medium Risk", risk_counts.get("Medium", 0))
    col4.metric("Low Risk", risk_counts.get("Low", 0))
    st.markdown(f"<div style='margin-top:10px;font-size:1.2rem'><b>Overall Contract Risk:</b> <span style='background-color:{get_risk_color(overall_risk)[0]};padding:4px 12px;border-radius:6px;color:#222'>{overall_risk}</span></div>", unsafe_allow_html=True)
    st.markdown("---")

    # --- Clause Navigation & Filtering ---
    st.subheader("Key Clauses & Risks")
    search = st.text_input("Search clauses by keyword", "")
    risk_filter_opts = st.multiselect("Filter by risk level", ["Low", "Medium", "High"], default=["Low", "Medium", "High"])
    filtered_clauses = filter_clauses(data["clauses"], data["risks"], search, risk_filter_opts)
    if not filtered_clauses:
        st.info("No clauses match your filters.")
        return
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # --- Clause Cards ---
    for clause, text, risk in filtered_clauses:
        render_clause_card(clause, text, risk, marked_for_revision=False)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 