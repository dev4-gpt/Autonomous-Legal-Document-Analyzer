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
        }
        
        .risk-card-low {
            border-left-color: #28a745;
        }
        
        .risk-card-medium {
            border-left-color: #ffc107;
        }
        
        .risk-card-high {
            border-left-color: #fd7e14;
        }
        
        .risk-card-critical {
            border-left-color: #dc3545;
        }
        
        /* Metric styling */
        .metric-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.375rem;
            text-align: center;
            margin-bottom: 1rem;
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #1f77b4;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: #6c757d;
            text-transform: uppercase;
            letter-spacing: 0.05em;
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
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        </style>
        """


def render_header():
    """Render the application header."""
    st.markdown(UITheme.get_custom_css(), unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #1f77b4; margin-bottom: 0.5rem;">⚖️ Legal Document Analyzer</h1>
            <p style="color: #6c757d; font-size: 1.1rem;">Enterprise AI-Powered Contract Analysis</p>
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
        <span>{text}</span>
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
        st.markdown(f"""
        <div class="custom-card {risk_class}">
            <div style="display: flex; justify-content: between; align-items: center; margin-bottom: 1rem;">
                <h4 style="margin: 0; color: #333;">{clause_type}</h4>
                <span style="background-color: {risk_color}; color: white; padding: 0.25rem 0.75rem; 
                           border-radius: 1rem; font-size: 0.875rem; font-weight: 500;">
                    {risk_level} Risk
                </span>
            </div>
            <div style="margin-bottom: 1rem;">
                <strong>Clause Content:</strong>
                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.375rem; 
                           margin-top: 0.5rem; font-family: monospace; white-space: pre-wrap;">
                    {display_text}
                </div>
            </div>
            <div>
                <strong>Risk Assessment:</strong>
                <p style="margin-top: 0.5rem; color: #555;">{rationale}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)


def render_document_summary_card(analysis_data: Dict[str, Any]) -> None:
    """Render document summary card."""
    st.markdown(f"""
    <div class="custom-card">
        <h3 style="color: #1f77b4; margin-bottom: 1rem;">📄 Document Summary</h3>
        <div style="margin-bottom: 1rem;">
            <strong>Contract Type:</strong> 
            <span style="background-color: #e9ecef; padding: 0.25rem 0.5rem; border-radius: 0.25rem;">
                {analysis_data.get('contract_type', 'Unknown')}
            </span>
        </div>
        <div style="margin-bottom: 1rem;">
            <strong>Overall Risk Level:</strong>
            <span style="background-color: {UITheme.RISK_COLORS.get(analysis_data.get('overall_risk_level', 'Unknown'), '#6c757d')}; 
                         color: white; padding: 0.25rem 0.75rem; border-radius: 1rem; font-weight: 500;">
                {analysis_data.get('overall_risk_level', 'Unknown')}
            </span>
        </div>
        <div>
            <strong>Summary:</strong>
            <p style="margin-top: 0.5rem; line-height: 1.6; color: #555;">
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
    st.markdown("### 🔧 System Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        db_status = "success" if health_data.get("database", {}).get("healthy", False) else "danger"
        render_status_indicator(db_status, f"Database: {'Healthy' if db_status == 'success' else 'Unhealthy'}")
    
    with col2:
        llm_status = "success" if health_data.get("llm", {}).get("available", False) else "danger"
        render_status_indicator(llm_status, f"LLM: {'Available' if llm_status == 'success' else 'Unavailable'}")
    
    with col3:
        storage_status = "success" if health_data.get("storage", {}).get("accessible", False) else "danger"
        render_status_indicator(storage_status, f"Storage: {'Accessible' if storage_status == 'success' else 'Inaccessible'}")


def render_file_upload_area() -> Optional[List]:
    """Render enhanced file upload area."""
    st.markdown("### 📁 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose legal documents to analyze",
        type=["pdf", "docx", "txt", "html"],
        accept_multiple_files=True,
        help=f"Supported formats: {', '.join(config.SUPPORTED_EXTENSIONS)}. Max size: {config.MAX_FILE_SIZE_MB}MB per file."
    )
    
    if uploaded_files:
        st.markdown("#### Selected Files:")
        for file in uploaded_files:
            file_size_mb = len(file.getvalue()) / (1024 * 1024)
            size_color = "green" if file_size_mb <= config.MAX_FILE_SIZE_MB else "red"
            
            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; 
                       padding: 0.5rem; background-color: #f8f9fa; border-radius: 0.375rem; margin-bottom: 0.5rem;">
                <span>📄 {file.name}</span>
                <span style="color: {size_color}; font-size: 0.875rem;">{file_size_mb:.1f} MB</span>
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
