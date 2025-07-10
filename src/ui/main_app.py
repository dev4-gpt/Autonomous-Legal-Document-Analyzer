"""
Main Streamlit application for the Legal Document Analyzer.
Enhanced UI with modern design, comprehensive analytics, and real-time monitoring.
"""

import streamlit as st
import time
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timedelta

# Configure Streamlit page
st.set_page_config(
    page_title="Legal Document Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import application modules
from src.config import config
from src.utils import logger, log_startup
from src.database import (
    init_database, get_db, Document, Analysis, get_document_stats, 
    get_recent_activity, db_manager
)
from src.core import (
    parse_and_store_document, analyze_and_store_document, 
    get_llm_status, llm_manager
)
from .components import (
    UITheme, render_header, render_metric_card, render_status_indicator,
    render_risk_card, render_document_summary_card, render_risk_distribution_chart,
    render_processing_timeline, render_system_health_panel, render_file_upload_area,
    render_search_and_filter_panel
)


class LegalAnalyzerApp:
    """Main application class for the Legal Document Analyzer."""
    
    def __init__(self):
        self.initialize_app()
    
    def initialize_app(self):
        """Initialize the application."""
        try:
            # Initialize database
            init_database()
            
            # Initialize session state
            if 'initialized' not in st.session_state:
                st.session_state.initialized = True
                st.session_state.selected_document = None
                st.session_state.processing_queue = []
                log_startup()
            
            logger.info("Application initialized successfully")
            
        except Exception as e:
            st.error(f"Failed to initialize application: {e}")
            logger.error("Application initialization failed", exception=e)
            st.stop()
    
    def run(self):
        """Run the main application."""
        render_header()
        
        # Sidebar navigation
        with st.sidebar:
            self.render_sidebar()
        
        # Main content area
        page = st.session_state.get('current_page', 'dashboard')
        
        if page == 'dashboard':
            self.render_dashboard()
        elif page == 'upload':
            self.render_upload_page()
        elif page == 'documents':
            self.render_documents_page()
        elif page == 'analytics':
            self.render_analytics_page()
        elif page == 'settings':
            self.render_settings_page()
    
    def render_sidebar(self):
        """Render the sidebar navigation."""
        st.markdown("## 📋 Navigation")
        
        # Navigation buttons
        pages = {
            'dashboard': '📊 Dashboard',
            'upload': '📁 Upload Documents',
            'documents': '📄 Document Library',
            'analytics': '📈 Analytics',
            'settings': '⚙️ Settings'
        }
        
        for page_key, page_name in pages.items():
            if st.button(page_name, key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # System status
        st.markdown("## 🔧 System Status")
        self.render_sidebar_status()
        
        st.markdown("---")
        
        # Quick stats
        st.markdown("## 📊 Quick Stats")
        self.render_sidebar_stats()
    
    def render_sidebar_status(self):
        """Render system status in sidebar."""
        try:
            # Database status
            db_healthy = db_manager.health_check()
            db_status = "success" if db_healthy else "danger"
            render_status_indicator(db_status, f"Database")
            
            # LLM status
            llm_status_data = get_llm_status()
            llm_available = any(provider["available"] for provider in llm_status_data.values())
            llm_status = "success" if llm_available else "danger"
            render_status_indicator(llm_status, f"LLM ({llm_manager.current_provider})")
            
            # Storage status
            storage_accessible = config.DATA_DIR.exists() and os.access(config.DATA_DIR, os.W_OK)
            storage_status = "success" if storage_accessible else "danger"
            render_status_indicator(storage_status, "Storage")
            
        except Exception as e:
            st.error(f"Status check failed: {e}")
    
    def render_sidebar_stats(self):
        """Render quick statistics in sidebar."""
        try:
            with next(get_db()) as db:
                stats = get_document_stats(db)
                
                st.metric("Total Documents", stats["total_documents"])
                st.metric("Success Rate", f"{stats['success_rate']:.1f}%")
                st.metric("Avg Processing", f"{stats['average_processing_time']:.1f}s")
                
        except Exception as e:
            st.error(f"Failed to load stats: {e}")
    
    def render_dashboard(self):
        """Render the main dashboard."""
        st.markdown("# 📊 Dashboard")
        
        try:
            with next(get_db()) as db:
                stats = get_document_stats(db)
                recent_docs = get_recent_activity(db, limit=5)
            
            # Key metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                render_metric_card("Total Documents", str(stats["total_documents"]))
            
            with col2:
                render_metric_card("Processed", str(stats["processed_documents"]))
            
            with col3:
                render_metric_card("Success Rate", f"{stats['success_rate']:.1f}%")
            
            with col4:
                render_metric_card("Avg Time", f"{stats['average_processing_time']:.1f}s")
            
            # Charts row
            col1, col2 = st.columns(2)
            
            with col1:
                if stats["risk_distribution"]:
                    render_risk_distribution_chart(stats["risk_distribution"])
                else:
                    st.info("No risk data available yet")
            
            with col2:
                if recent_docs:
                    doc_data = [
                        {
                            "processed_timestamp": doc.processed_timestamp,
                            "processing_status": doc.processing_status
                        }
                        for doc in recent_docs
                    ]
                    render_processing_timeline(doc_data)
                else:
                    st.info("No processing history available")
            
            # Recent activity
            st.markdown("## 📋 Recent Activity")
            if recent_docs:
                for doc in recent_docs:
                    with st.expander(f"📄 {doc.filename}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Status:** {doc.processing_status}")
                        with col2:
                            st.write(f"**Size:** {doc.file_size / 1024:.1f} KB")
                        with col3:
                            if doc.processed_timestamp:
                                st.write(f"**Processed:** {doc.processed_timestamp.strftime('%Y-%m-%d %H:%M')}")
            else:
                st.info("No recent activity")
                
        except Exception as e:
            st.error(f"Failed to load dashboard: {e}")
            logger.error("Dashboard loading failed", exception=e)
    
    def render_upload_page(self):
        """Render the document upload page."""
        st.markdown("# 📁 Upload Documents")
        
        # File upload area
        uploaded_files = render_file_upload_area()
        
        if uploaded_files:
            if st.button("🚀 Process Documents", type="primary", use_container_width=True):
                self.process_uploaded_files(uploaded_files)
    
    def process_uploaded_files(self, uploaded_files):
        """Process uploaded files."""
        progress_bar = st.progress(0)
        status_text = st.empty()
        results_container = st.container()
        
        total_files = len(uploaded_files)
        processed_files = 0
        
        for i, uploaded_file in enumerate(uploaded_files):
            try:
                status_text.text(f"Processing {uploaded_file.name}...")
                
                # Save uploaded file
                file_path = config.UPLOADS_DIR / uploaded_file.name
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Parse document
                with st.spinner(f"Parsing {uploaded_file.name}..."):
                    parse_success, doc_id = parse_and_store_document(str(file_path))
                
                if parse_success:
                    # Analyze document
                    with st.spinner(f"Analyzing {uploaded_file.name}..."):
                        with next(get_db()) as db:
                            document = db.query(Document).filter(Document.doc_id == doc_id).first()
                            if document:
                                # Get document text for analysis
                                from src.core.parser import parse_document
                                parse_result = parse_document(str(file_path))
                                if parse_result.success:
                                    analysis_result = analyze_and_store_document(parse_result.text, doc_id)
                                    
                                    with results_container:
                                        if analysis_result.success:
                                            st.success(f"✅ {uploaded_file.name} processed successfully")
                                        else:
                                            st.error(f"❌ Analysis failed for {uploaded_file.name}: {analysis_result.error_message}")
                                else:
                                    st.error(f"❌ Failed to parse {uploaded_file.name}")
                            else:
                                st.error(f"❌ Document record not found for {uploaded_file.name}")
                else:
                    with results_container:
                        st.error(f"❌ Failed to process {uploaded_file.name}: {doc_id}")
                
                processed_files += 1
                progress_bar.progress(processed_files / total_files)
                
            except Exception as e:
                with results_container:
                    st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                logger.error(f"File processing error: {e}", exception=e)
        
        status_text.text("Processing complete!")
        st.balloons()
    
    def render_documents_page(self):
        """Render the documents library page."""
        st.markdown("# 📄 Document Library")
        
        # Search and filter panel
        filters = render_search_and_filter_panel()
        
        try:
            with next(get_db()) as db:
                # Get documents with analysis
                query = db.query(Document).join(Analysis, Document.id == Analysis.document_id, isouter=True)
                
                # Apply filters
                if filters["search_query"]:
                    query = query.filter(Document.filename.contains(filters["search_query"]))
                
                if filters["contract_types"]:
                    query = query.filter(Analysis.contract_type.in_(filters["contract_types"]))
                
                documents = query.order_by(Document.processed_timestamp.desc()).all()
                
                if documents:
                    # Document grid
                    for doc in documents:
                        with st.expander(f"📄 {doc.filename}", expanded=False):
                            if doc.analysis:
                                render_document_summary_card({
                                    'contract_type': doc.analysis.contract_type,
                                    'overall_risk_level': doc.analysis.overall_risk_level,
                                    'summary': doc.analysis.summary
                                })
                                
                                # Show clauses and risks
                                if doc.clauses:
                                    st.markdown("### 📋 Clauses & Risk Assessment")
                                    for clause in doc.clauses:
                                        risk_assessment = next(
                                            (r for r in doc.risks if r.clause_id == clause.id), 
                                            None
                                        )
                                        if risk_assessment:
                                            render_risk_card(
                                                clause.clause_type,
                                                clause.clause_text,
                                                risk_assessment.risk_level,
                                                risk_assessment.rationale
                                            )
                            else:
                                st.info("Document analysis not available")
                else:
                    st.info("No documents found matching your criteria")
                    
        except Exception as e:
            st.error(f"Failed to load documents: {e}")
            logger.error("Documents page loading failed", exception=e)
    
    def render_analytics_page(self):
        """Render the analytics page."""
        st.markdown("# 📈 Analytics")
        
        try:
            with next(get_db()) as db:
                stats = get_document_stats(db)
                
                # Analytics overview
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📊 Risk Distribution")
                    if stats["risk_distribution"]:
                        render_risk_distribution_chart(stats["risk_distribution"])
                    else:
                        st.info("No risk data available")
                
                with col2:
                    st.markdown("### 📋 Contract Types")
                    if stats["contract_types"]:
                        # Create contract types chart
                        import plotly.express as px
                        df = pd.DataFrame(
                            list(stats["contract_types"].items()),
                            columns=['Contract Type', 'Count']
                        )
                        fig = px.bar(df, x='Contract Type', y='Count', 
                                   title='Contract Type Distribution')
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No contract type data available")
                
                # Performance metrics
                st.markdown("### ⚡ Performance Metrics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    render_metric_card("Avg Processing Time", f"{stats['average_processing_time']:.2f}s")
                
                with col2:
                    render_metric_card("Success Rate", f"{stats['success_rate']:.1f}%")
                
                with col3:
                    render_metric_card("Total Processed", str(stats["processed_documents"]))
                    
        except Exception as e:
            st.error(f"Failed to load analytics: {e}")
            logger.error("Analytics page loading failed", exception=e)
    
    def render_settings_page(self):
        """Render the settings page."""
        st.markdown("# ⚙️ Settings")
        
        # LLM Configuration
        st.markdown("## 🤖 LLM Configuration")
        
        try:
            llm_status = get_llm_status()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Available Providers")
                for provider, status in llm_status.items():
                    status_icon = "✅" if status["available"] else "❌"
                    current_icon = "🔄" if status["current"] else ""
                    st.write(f"{status_icon} {provider} ({status['model']}) {current_icon}")
            
            with col2:
                st.markdown("### System Health")
                render_system_health_panel({
                    "database": {"healthy": db_manager.health_check()},
                    "llm": {"available": any(s["available"] for s in llm_status.values())},
                    "storage": {"accessible": config.DATA_DIR.exists()}
                })
            
            # Configuration options
            st.markdown("## 🔧 Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info(f"**Data Directory:** {config.DATA_DIR}")
                st.info(f"**Max File Size:** {config.MAX_FILE_SIZE_MB} MB")
                st.info(f"**Supported Formats:** {', '.join(config.SUPPORTED_EXTENSIONS)}")
            
            with col2:
                st.info(f"**Current LLM:** {llm_manager.current_provider}")
                st.info(f"**Vector DB:** {config.VECTOR_DB_TYPE}")
                st.info(f"**Chunk Size:** {config.CHUNK_SIZE}")
                
        except Exception as e:
            st.error(f"Failed to load settings: {e}")
            logger.error("Settings page loading failed", exception=e)


def main():
    """Main application entry point."""
    app = LegalAnalyzerApp()
    app.run()


if __name__ == "__main__":
    main()
