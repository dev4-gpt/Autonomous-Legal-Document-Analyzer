"""
UI Components for the Legal Document Analyzer.
Reusable Streamlit components with consistent styling and functionality.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timedelta

from src.config import config


class UITheme:
    """UI theme configuration and styling."""
    
    # Color palette
    PRIMARY = "#1f77b4"
    SECONDARY = "#ff7f0e"
    SUCCESS = "#2ca02c"
    WARNING = "#ff7f0e"
    DANGER = "#d62728"
    INFO = "#17a2b8"
    
    # Risk colors
    RISK_COLORS = {
        "Low": "#28a745",
        "Medium": "#ffc107", 
        "High": "#fd7e14",
        "Critical": "#dc3545",
        "Unknown": "#6c757d"
    }
    
    # Background colors
    CARD_BG = "#f8f9fa"
    SIDEBAR_BG = "#343a40"
    
    @staticmethod
    def get_custom_css() -> str:
        """Get custom CSS for the application."""
        return """
        <style>
        /* Main app styling */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* Custom card styling */
        .custom-card {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            border-left: 4px solid #1f77b4;
            color: #333333;
        }

        .custom-card h3, .custom-card h4, .custom-card h5 {
            color: #1f77b4 !important;
            margin-bottom: 1rem;
        }

        .custom-card p, .custom-card div, .custom-card span {
            color: #333333 !important;
        }

        .custom-card strong {
            color: #2c3e50 !important;
            font-weight: 600;
        }

        .risk-card-low {
            border-left-color: #28a745;
            background-color: #f8fff9;
        }

        .risk-card-medium {
            border-left-color: #ffc107;
            background-color: #fffdf5;
        }

        .risk-card-high {
            border-left-color: #fd7e14;
            background-color: #fff8f5;
        }

        .risk-card-critical {
            border-left-color: #dc3545;
            background-color: #fff5f5;
        }
        
        /* Metric styling */
        .metric-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.375rem;
            text-align: center;
            margin-bottom: 1rem;
            border: 1px solid #e9ecef;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #1f77b4 !important;
            margin-bottom: 0.25rem;
        }

        .metric-label {
            font-size: 0.875rem;
            color: #495057 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 500;
        }
        
        /* Status indicators */
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        
        .status-success { background-color: #28a745; }
        .status-warning { background-color: #ffc107; }
        .status-danger { background-color: #dc3545; }
        .status-info { background-color: #17a2b8; }

        /* System status panel styling */
        .system-status-panel {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 0.5rem;
            border: 1px solid #e9ecef;
            margin-bottom: 1rem;
        }

        .system-status-panel h3 {
            color: #2c3e50 !important;
            font-weight: 600 !important;
            margin-bottom: 1rem !important;
        }

        .status-item {
            display: flex;
            align-items: center;
            margin: 0.75rem 0;
            padding: 0.5rem;
            background-color: #ffffff;
            border-radius: 0.375rem;
            border: 1px solid #e9ecef;
        }

        .status-item span {
            color: #2c3e50 !important;
            font-weight: 500 !important;
            margin-left: 0.5rem;
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 0.375rem;
            border: none;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        /* Sidebar styling */
        .css-1d391kg {
            background-color: #343a40;
        }

        /* Navigation and sidebar text improvements */
        .stSidebar .stMarkdown h1, .stSidebar .stMarkdown h2, .stSidebar .stMarkdown h3 {
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        .stSidebar .stMarkdown p, .stSidebar .stMarkdown div, .stSidebar .stMarkdown span {
            color: #f8f9fa !important;
            font-weight: 500 !important;
        }

        .stSidebar .stSelectbox label, .stSidebar .stRadio label {
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        /* Main page headers and titles */
        .main .stMarkdown h1 {
            color: #1f77b4 !important;
            font-weight: 700 !important;
            font-size: 2.5rem !important;
        }

        .main .stMarkdown h2 {
            color: #2c3e50 !important;
            font-weight: 600 !important;
            font-size: 1.8rem !important;
        }

        .main .stMarkdown h3 {
            color: #2c3e50 !important;
            font-weight: 600 !important;
            font-size: 1.4rem !important;
        }

        /* Page section headers */
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
            color: #2c3e50 !important;
            font-weight: 600 !important;
        }

        /* General text improvements */
        .stMarkdown p {
            color: #495057 !important;
            font-weight: 400 !important;
            line-height: 1.6 !important;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Improve text readability */
        .stExpander > div > div > div > div {
            color: #333333 !important;
        }

        .stExpander summary {
            color: #1f77b4 !important;
            font-weight: 600 !important;
        }

        .stMarkdown p, .stMarkdown div, .stMarkdown span {
            color: #333333 !important;
        }

        .stMarkdown strong {
            color: #2c3e50 !important;
            font-weight: 600 !important;
        }

        /* Risk badge styling */
        .risk-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.875rem;
            font-weight: 600;
            color: white !important;
            margin-left: 0.5rem;
        }

        .risk-badge-low { background-color: #28a745; }
        .risk-badge-medium { background-color: #ffc107; color: #212529 !important; }
        .risk-badge-high { background-color: #fd7e14; }
        .risk-badge-critical { background-color: #dc3545; }

        /* Clause content styling */
        .clause-content {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.375rem;
            margin-top: 0.5rem;
            font-family: 'Courier New', monospace;
            white-space: pre-wrap;
            color: #2c3e50 !important;
            border: 1px solid #e9ecef;
        }
        </style>
        """


def render_header():
    """Render the application header."""
    st.markdown(UITheme.get_custom_css(), unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #1f77b4 !important; margin-bottom: 0.5rem; font-weight: 700; font-size: 2.5rem;">⚖️ Legal Document Analyzer</h1>
            <p style="color: #2c3e50 !important; font-size: 1.2rem; font-weight: 500;">Enterprise AI-Powered Contract Analysis</p>
        </div>
        """, unsafe_allow_html=True)


def render_metric_card(title: str, value: str, delta: Optional[str] = None, 
                      delta_color: str = "normal") -> None:
    """Render a metric card with optional delta."""
    delta_html = ""
    if delta:
        color = "#28a745" if delta_color == "normal" else "#dc3545"
        delta_html = f'<div style="color: {color}; font-size: 0.875rem; margin-top: 0.25rem;">{delta}</div>'
    
    st.markdown(f"""
    <div class="metric-container">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_status_indicator(status: str, text: str) -> None:
    """Render a status indicator with text."""
    status_class = f"status-{status}"
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin: 0.5rem 0;">
        <span class="status-indicator {status_class}"></span>
        <span style="color: #2c3e50 !important; font-weight: 500; margin-left: 0.5rem;">{text}</span>
    </div>
    """, unsafe_allow_html=True)


def render_risk_card(clause_type: str, clause_text: str, risk_level: str, 
                    rationale: str, expanded: bool = False) -> None:
    """Render a risk assessment card for a clause."""
    risk_color = UITheme.RISK_COLORS.get(risk_level, UITheme.RISK_COLORS["Unknown"])
    risk_class = f"risk-card-{risk_level.lower()}"
    
    # Truncate clause text for display
    display_text = clause_text[:500] + "..." if len(clause_text) > 500 else clause_text
    
    with st.expander(f"🔍 {clause_type} - {risk_level} Risk", expanded=expanded):
        # Determine risk badge color
        badge_color = risk_color
        text_color = "white"
        if risk_level.lower() == "medium":
            text_color = "#212529"  # Dark text for yellow background

        st.markdown(f"""
        <div class="custom-card {risk_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #2c3e50 !important; font-weight: 600;">{clause_type}</h4>
                <span class="risk-badge risk-badge-{risk_level.lower()}"
                      style="background-color: {badge_color}; color: {text_color} !important;">
                    {risk_level} Risk
                </span>
            </div>
            <div style="margin-bottom: 1rem;">
                <strong style="color: #2c3e50 !important;">Clause Content:</strong>
                <div class="clause-content">
                    {display_text}
                </div>
            </div>
            <div>
                <strong style="color: #2c3e50 !important;">Risk Assessment:</strong>
                <p style="margin-top: 0.5rem; color: #495057 !important; line-height: 1.5;">{rationale}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_document_summary_card(analysis_data: Dict[str, Any]) -> None:
    """Render document summary card."""
    overall_risk = analysis_data.get('overall_risk_level', 'Unknown')
    risk_color = UITheme.RISK_COLORS.get(overall_risk, '#6c757d')
    risk_text_color = "white" if overall_risk.lower() != "medium" else "#212529"

    st.markdown(f"""
    <div class="custom-card">
        <h3 style="color: #1f77b4 !important; margin-bottom: 1rem; font-weight: 600;">📄 Document Summary</h3>
        <div style="margin-bottom: 1rem;">
            <strong style="color: #2c3e50 !important;">Contract Type:</strong>
            <span style="background-color: #e9ecef; padding: 0.25rem 0.5rem; border-radius: 0.25rem;
                         color: #2c3e50 !important; font-weight: 500;">
                {analysis_data.get('contract_type', 'Unknown')}
            </span>
        </div>
        <div style="margin-bottom: 1rem;">
            <strong style="color: #2c3e50 !important;">Overall Risk Level:</strong>
            <span class="risk-badge risk-badge-{overall_risk.lower()}"
                  style="background-color: {risk_color}; color: {risk_text_color} !important;">
                {overall_risk}
            </span>
        </div>
        <div>
            <strong style="color: #2c3e50 !important;">Summary:</strong>
            <p style="margin-top: 0.5rem; line-height: 1.6; color: #495057 !important;">
                {analysis_data.get('summary', 'No summary available')}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_risk_distribution_chart(risk_data: Dict[str, int]) -> None:
    """Render risk distribution pie chart."""
    if not risk_data:
        st.info("No risk data available")
        return
    
    # Prepare data for chart
    labels = list(risk_data.keys())
    values = list(risk_data.values())
    colors = [UITheme.RISK_COLORS.get(label, "#6c757d") for label in labels]
    
    # Create pie chart
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='inside',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Risk Distribution",
        showlegend=True,
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_processing_timeline(documents: List[Dict[str, Any]]) -> None:
    """Render document processing timeline."""
    if not documents:
        st.info("No processing history available")
        return
    
    # Prepare data
    df = pd.DataFrame(documents)
    df['processed_timestamp'] = pd.to_datetime(df['processed_timestamp'])
    df['date'] = df['processed_timestamp'].dt.date
    
    # Group by date and status
    timeline_data = df.groupby(['date', 'processing_status']).size().reset_index(name='count')
    
    # Create timeline chart
    fig = px.bar(
        timeline_data,
        x='date',
        y='count',
        color='processing_status',
        title='Document Processing Timeline',
        color_discrete_map={
            'completed': UITheme.SUCCESS,
            'failed': UITheme.DANGER,
            'processing': UITheme.WARNING
        }
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Number of Documents",
        height=400,
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def render_system_health_panel(health_data: Dict[str, Any]) -> None:
    """Render system health monitoring panel."""
    st.markdown("""
    <div class="system-status-panel">
        <h3>🔧 System Health</h3>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
    """, unsafe_allow_html=True)

    # Database status
    db_status = "success" if health_data.get("database", {}).get("healthy", False) else "danger"
    db_text = "Database: Healthy" if db_status == "success" else "Database: Unhealthy"

    # LLM status
    llm_status = "success" if health_data.get("llm", {}).get("available", False) else "danger"
    llm_text = "LLM: Available" if llm_status == "success" else "LLM: Unavailable"

    # Storage status
    storage_status = "success" if health_data.get("storage", {}).get("accessible", False) else "danger"
    storage_text = "Storage: Accessible" if storage_status == "success" else "Storage: Inaccessible"

    # Render status items
    for status, text in [(db_status, db_text), (llm_status, llm_text), (storage_status, storage_text)]:
        st.markdown(f"""
        <div class="status-item">
            <span class="status-indicator status-{status}"></span>
            <span>{text}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)


def render_file_upload_area() -> Optional[List]:
    """Render enhanced file upload area."""
    st.markdown('<h3 style="color: #2c3e50 !important; font-weight: 600;">📁 Upload Documents</h3>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Choose legal documents to analyze",
        type=["pdf", "docx", "txt", "html"],
        accept_multiple_files=True,
        help=f"Supported formats: {', '.join(config.SUPPORTED_EXTENSIONS)}. Max size: {config.MAX_FILE_SIZE_MB}MB per file."
    )

    if uploaded_files:
        st.markdown('<h4 style="color: #2c3e50 !important; font-weight: 600;">Selected Files:</h4>', unsafe_allow_html=True)
        for file in uploaded_files:
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            size_color = "#28a745" if file_size_mb <= config.MAX_FILE_SIZE_MB else "#dc3545"

            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center;
                       padding: 0.75rem; background-color: #f8f9fa; border-radius: 0.375rem;
                       margin-bottom: 0.5rem; border: 1px solid #e9ecef;">
                <span style="color: #2c3e50 !important; font-weight: 500;">📄 {file.name}</span>
                <span style="color: {size_color} !important; font-size: 0.875rem; font-weight: 600;">{file_size_mb:.1f} MB</span>
            </div>
            """, unsafe_allow_html=True)

    return uploaded_files


def render_search_and_filter_panel() -> Dict[str, Any]:
    """Render search and filter panel."""
    st.markdown("### 🔍 Search & Filter")
    
    col1, col2 = st.columns(2)
    
    with col1:
        search_query = st.text_input(
            "Search documents",
            placeholder="Enter keywords to search in documents..."
        )
    
    with col2:
        contract_type_filter = st.multiselect(
            "Filter by contract type",
            options=config.CONTRACT_TYPES,
            default=[]
        )
    
    col3, col4 = st.columns(2)
    
    with col3:
        risk_level_filter = st.multiselect(
            "Filter by risk level",
            options=config.RISK_LEVELS,
            default=[]
        )
    
    with col4:
        date_range = st.date_input(
            "Date range",
            value=[],
            help="Filter documents by processing date"
        )
    
    return {
        "search_query": search_query,
        "contract_types": contract_type_filter,
        "risk_levels": risk_level_filter,
        "date_range": date_range
    }
