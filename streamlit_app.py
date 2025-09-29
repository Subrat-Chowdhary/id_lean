"""
Streamlit Frontend for Instructional Design RAG System
Provides a user-friendly interface for document upload and content generation
"""

import streamlit as st
import requests
import json
import os
from pathlib import Path
import time
import tempfile
from typing import List, Dict, Any

# Page configuration
st.set_page_config(
    page_title="Instructional Design RAG System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #34495e;
        margin: 1rem 0;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .file-info {
        background-color: #f8f9fa;
        border-left: 4px solid #007bff;
        padding: 0.75rem;
        margin: 0.5rem 0;
        color: #2c3e50;        
    }
</style>
""", unsafe_allow_html=True)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Helper functions
def call_api(endpoint: str, method: str = "GET", data: dict = None, files: dict = None) -> dict:
    """Make API calls to the backend"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, params=data)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, data=data)
            else:
                response = requests.post(url, json=data)
        elif method == "DELETE":
            response = requests.delete(url)
        else:
            st.error(f"Unsupported HTTP method: {method}")
            return {"success": False, "error": "Unsupported method"}
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"success": False, "error": f"HTTP {response.status_code}: {response.text}"}
            
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Cannot connect to API server. Please ensure the server is running on http://localhost:8000"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def display_success(message: str):
    """Display success message"""
    st.markdown(f'<div class="success-box">✅ {message}</div>', unsafe_allow_html=True)

def display_error(message: str):
    """Display error message"""
    st.markdown(f'<div class="error-box">❌ {message}</div>', unsafe_allow_html=True)

def display_info(message: str):
    """Display info message"""
    st.markdown(f'<div class="info-box">ℹ️ {message}</div>', unsafe_allow_html=True)

# Main App
def main():
    # Header
    st.markdown('<h1 class="main-header">Instructional Design RAG System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Navigation")
        page = st.selectbox(
            "Choose a page:",
            ["🏠 Home", "📤 Upload Documents", "🎨 Generate Content", "🔍 Search Knowledge", "📊 Statistics", "📁 Generated Files"]
        )
        
        st.markdown("---")
        
        # System status
        st.markdown("### 🔧 System Status")
        with st.spinner("Checking system status..."):
            health = call_api("/health")
            if health.get("status") == "healthy":
                st.success("✅ System Online")
                st.info(f"Knowledge Base: {health.get('knowledge_base_status', 'Unknown')}")
            else:
                st.error("❌ System Offline")
                st.error(health.get("error", "Unknown error"))
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🎲 Setup Demo Data"):
            with st.spinner("Setting up demo data..."):
                result = call_api("/setup-demo", "POST")
                if result.get("success"):
                    st.success("Demo data setup complete!")
                else:
                    st.error(f"Error: {result.get('error', 'Unknown error')}")

    # Main content area
    if page == "🏠 Home":
        show_home_page()
    elif page == "📤 Upload Documents":
        show_upload_page()
    elif page == "🎨 Generate Content":
        show_generate_page()
    elif page == "🔍 Search Knowledge":
        show_search_page()
    elif page == "📊 Statistics":
        show_stats_page()
    elif page == "📁 Generated Files":
        show_files_page()

def show_home_page():
    """Home page with system overview"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🎯 What is this system?")
        st.write("""
        The Instructional Design RAG (Retrieval-Augmented Generation) System helps you create 
        professional training materials by:
        
        1. **📤 Upload Knowledge**: Upload your instructional design documents (PDFs, Word docs, etc.)
        2. **🧠 AI Processing**: The system creates a searchable knowledge base using advanced AI
        3. **🎨 Generate Content**: Request training materials and get professionally formatted outputs
        4. **📊 Multiple Formats**: Generate PowerPoint presentations, PDF manuals, or both
        """)
        
        st.markdown("### 🚀 Quick Start Guide")
        st.write("""
        **Step 1**: Upload your instructional design documents using the "Upload Documents" page
        
        **Step 2**: Go to "Generate Content" and describe what you want:
        - *"Create a 15-minute training module on project management"*
        - *"Make a beginner-level presentation about adult learning principles"*
        - *"Generate a 30-minute advanced training on assessment strategies"*
        
        **Step 3**: Download your generated PowerPoint or PDF files!
        """)
    
    with col2:
        st.markdown("### 📈 System Features")
        st.success("✅ Multi-format document support")
        st.success("✅ AI-powered content generation")
        st.success("✅ Professional PowerPoint creation")
        st.success("✅ Comprehensive PDF manuals")
        st.success("✅ Smart content retrieval")
        st.success("✅ Multiple learning levels")
        
        # Quick stats
        stats_result = call_api("/stats")
        if stats_result.get("success"):
            stats = stats_result.get("stats", {})
            st.markdown("### 📊 Quick Stats")
            st.metric("Documents", stats.get("unique_documents", 0))
            st.metric("Content Chunks", stats.get("total_chunks", 0))
        
        # Example prompt
        st.markdown("### 💡 Example Prompt")
        st.code("""
Create a 20-minute intermediate 
training module on instructional 
design principles with practical 
examples and activities
        """)

def show_upload_page():
    """Document upload page"""
    st.markdown('<h2 class="section-header">📤 Upload Documents</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("Upload your instructional design documents to build the knowledge base.")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            type=['pdf', 'docx', 'doc', 'txt', 'md', 'xlsx', 'xls', 'csv'],
            accept_multiple_files=True,
            help="Supported formats: PDF, Word documents, text files, Excel, CSV"
        )
        
        if uploaded_files:
            st.write(f"Selected {len(uploaded_files)} file(s):")
            for file in uploaded_files:
                st.markdown(f'<div class="file-info">📄 {file.name} ({file.size:,} bytes)</div>', 
                           unsafe_allow_html=True)
            
            if st.button("🚀 Upload Files", type="primary"):
                upload_files(uploaded_files)
    
    with col2:
        st.markdown("### 📋 Supported Formats")
        st.write("""
        - **PDF** (.pdf) - Research papers, manuals
        - **Word** (.docx, .doc) - Training documents
        - **Text** (.txt, .md) - Notes, guidelines
        - **Excel** (.xlsx, .xls) - Data, templates
        - **CSV** (.csv) - Structured data
        """)
        
        st.markdown("### 💡 Tips")
        st.info("""
        - Upload documents with rich instructional content
        - Include various perspectives and approaches
        - Mix theoretical and practical materials
        - The more content you upload, the better the AI can generate materials
        """)

def upload_files(uploaded_files: List):
    """Handle file upload process"""
    progress_bar = st.progress(0)
    status_container = st.container()
    
    with status_container:
        for i, uploaded_file in enumerate(uploaded_files):
            progress = (i + 1) / len(uploaded_files)
            progress_bar.progress(progress)
            
            st.write(f"Uploading {uploaded_file.name}...")
            
            # Prepare file for API
            files = {"files": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            
            # Upload via API
            result = call_api("/upload", "POST", files=files)
            
            if result.get("success"):
                display_success(f"Successfully uploaded {uploaded_file.name}")
                st.write(f"  - Document ID: {result.get('document_id', 'N/A')}")
                st.write(f"  - Content chunks created: {result.get('chunks_created', 0)}")
            else:
                display_error(f"Failed to upload {uploaded_file.name}: {result.get('message', 'Unknown error')}")
    
    progress_bar.progress(1.0)
    st.balloons()

def show_generate_page():
    """Content generation page"""
    st.markdown('<h2 class="section-header">🎨 Generate Training Content</h2>', unsafe_allow_html=True)
    
    # Check if we have documents
    stats_result = call_api("/stats")
    if stats_result.get("success"):
        stats = stats_result.get("stats", {})
        if stats.get("total_chunks", 0) == 0:
            st.warning("⚠️ No documents found in knowledge base. Please upload some documents first!")
            return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Content generation form
        with st.form("generate_form"):
            st.markdown("### 📝 Describe Your Training Content")
            
            prompt = st.text_area(
                "What training content would you like to create?",
                placeholder="Example: Create a 15-minute training module on adult learning principles with interactive activities",
                height=100,
                help="Be specific about the topic, duration, and any special requirements"
            )
            
            col_dur, col_level, col_format = st.columns(3)
            
            with col_dur:
                duration = st.selectbox(
                    "Duration (minutes)",
                    [5, 10, 15, 20, 30, 45, 60, 90],
                    index=2,  # Default to 15 minutes
                    help="How long should the training be?"
                )
            
            with col_level:
                level = st.selectbox(
                    "Learning Level",
                    ["beginner", "intermediate", "advanced"],
                    index=1,  # Default to intermediate
                    help="Target audience level"
                )
            
            with col_format:
                output_format = st.selectbox(
                    "Output Format",
                    ["ppt", "pdf", "both"],
                    index=0,  # Default to PowerPoint
                    format_func=lambda x: {"ppt": "PowerPoint", "pdf": "PDF Manual", "both": "Both"}[x],
                    help="What format would you like?"
                )
            
            submit_button = st.form_submit_button("🚀 Generate Content", type="primary")
            
            if submit_button and prompt:
                generate_content(prompt, duration, level, output_format)
    
    with col2:
        st.markdown("### 💡 Example Prompts")
        examples = [
            "Create a 15-minute training on project management fundamentals",
            "Generate a beginner course on instructional design principles",
            "Make a 30-minute advanced training on assessment strategies",
            "Create a presentation about adult learning theories with examples",
            "Design a workshop on effective feedback techniques"
        ]
        
        for example in examples:
            if st.button(f"💡 {example}", key=f"example_{hash(example)}"):
                st.session_state.example_prompt = example
        
        st.markdown("### 🎯 Tips for Better Results")
        st.info("""
        - Be specific about the topic
        - Mention the target audience
        - Include desired activities or examples
        - Specify any particular focus areas
        """)

def generate_content(prompt: str, duration: int, level: str, output_format: str):
    """Generate training content"""
    with st.spinner("🤖 Generating your training content... This may take a few moments."):
        
        # Show progress steps
        progress_container = st.container()
        with progress_container:
            st.write("🔍 Searching knowledge base...")
            time.sleep(1)
            st.write("🧠 Generating content structure...")
            time.sleep(1)
            st.write(f"🎨 Creating {output_format.upper()} files...")
        
        # API request
        request_data = {
            "prompt": prompt,
            "output_format": output_format,
            "duration_minutes": duration,
            "learning_level": level
        }
        
        result = call_api("/generate", "POST", data=request_data)
        
        if result.get("success"):
            display_success("Training content generated successfully!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📊 Generation Summary")
                st.write(f"**Topic:** {result.get('topic', 'N/A')}")
                st.write(f"**Duration:** {result.get('duration_minutes', 0)} minutes")
                st.write(f"**Level:** {result.get('learning_level', 'N/A').title()}")
                st.write(f"**Sources Used:** {result.get('sources_used', 0)} documents")
            
            with col2:
                st.markdown("### 📁 Generated Files")
                for file_info in result.get('output_files', []):
                    file_type = file_info['type']
                    filename = file_info['filename']
                    
                    # Create download button
                    download_url = f"{API_BASE_URL}/download/{filename}"
                    st.markdown(
                        f"📄 **{filename}** ({file_type.upper()})"
                    )
                    st.markdown(
                        f'<a href="{download_url}" target="_blank" style="color: #007bff;">⬇️ Download {file_type.upper()}</a>',
                        unsafe_allow_html=True
                    )
            
            st.balloons()
            
        else:
            display_error(f"Failed to generate content: {result.get('message', 'Unknown error')}")

def show_search_page():
    """Knowledge base search page"""
    st.markdown('<h2 class="section-header">🔍 Search Knowledge Base</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "Search your knowledge base:",
            placeholder="Enter keywords to search for...",
            help="Search through all uploaded documents"
        )
        
        n_results = st.slider("Number of results", 1, 20, 5)
        
        if st.button("🔍 Search") and search_query:
            search_knowledge(search_query, n_results)
    
    with col2:
        st.markdown("### 🎯 Search Tips")
        st.info("""
        - Use specific keywords
        - Try different phrasings
        - Search for concepts, not just exact words
        - Results show relevant content chunks
        """)

def search_knowledge(query: str, n_results: int):
    """Perform knowledge base search"""
    with st.spinner("Searching knowledge base..."):
        params = {"query": query, "n_results": n_results}
        result = call_api("/search", "GET", data=params)
        
        if result.get("success"):
            results = result.get("results", [])
            
            if results:
                st.markdown(f"### 📊 Found {len(results)} results for '{query}'")
                
                for i, search_result in enumerate(results, 1):
                    with st.expander(f"Result {i}: {search_result['metadata']['filename']} (Score: {search_result['similarity_score']:.3f})"):
                        st.write("**Content:**")
                        st.write(search_result['text'][:500] + "..." if len(search_result['text']) > 500 else search_result['text'])
                        
                        st.write("**Metadata:**")
                        st.json(search_result['metadata'])
            else:
                st.warning("No results found for your query.")
        else:
            display_error(f"Search failed: {result.get('error', 'Unknown error')}")

def show_stats_page():
    """Statistics and analytics page"""
    st.markdown('<h2 class="section-header">📊 Knowledge Base Statistics</h2>', unsafe_allow_html=True)
    
    # Get stats
    stats_result = call_api("/stats")
    
    if stats_result.get("success"):
        stats = stats_result.get("stats", {})
        
        # Main metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📄 Documents", stats.get("unique_documents", 0))
        
        with col2:
            st.metric("🧩 Content Chunks", stats.get("total_chunks", 0))
        
        with col3:
            st.metric("📁 Collection", stats.get("collection_name", "N/A"))
        
        with col4:
            # Get generated files count
            files_result = call_api("/files")
            files_count = len(files_result.get("files", [])) if files_result.get("success") else 0
            st.metric("🎨 Generated Files", files_count)
        
        # File types breakdown
        if stats.get("file_types"):
            st.markdown("### 📊 File Types Distribution")
            file_types = stats["file_types"]
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Simple bar chart using Streamlit
                for file_type, count in file_types.items():
                    st.write(f"**{file_type}**: {count} files")
                    st.progress(count / max(file_types.values()) if file_types.values() else 0)
            
            with col2:
                st.write("**Total Files by Type:**")
                for file_type, count in file_types.items():
                    st.write(f"• {file_type}: {count}")
        
        # Documents list
        st.markdown("### 📋 Uploaded Documents")
        docs_result = call_api("/documents")
        
        if docs_result.get("success"):
            documents = docs_result.get("documents", {})
            
            for file_type, docs in documents.items():
                with st.expander(f"{file_type} files ({len(docs)} documents)"):
                    for doc in docs:
                        st.write(f"**{doc['filename']}** (ID: {doc['document_id']})")
                        st.write(f"  - Chunks: {len(doc['chunks'])}")
                        if st.button(f"🗑️ Delete", key=f"delete_{doc['document_id']}"):
                            delete_document(doc['document_id'])
        
    else:
        display_error(f"Failed to load statistics: {stats_result.get('error', 'Unknown error')}")

def delete_document(document_id: str):
    """Delete a document"""
    result = call_api(f"/documents/{document_id}", "DELETE")
    
    if result.get("success"):
        display_success(f"Document {document_id} deleted successfully!")
        st.experimental_rerun()
    else:
        display_error(f"Failed to delete document: {result.get('message', 'Unknown error')}")

def show_files_page():
    """Generated files management page"""
    st.markdown('<h2 class="section-header">📁 Generated Training Files</h2>', unsafe_allow_html=True)
    
    # Get generated files
    files_result = call_api("/files")
    
    if files_result.get("success"):
        files = files_result.get("files", [])
        
        if files:
            st.write(f"Found {len(files)} generated files:")
            
            for file_info in files:
                with st.expander(f"📄 {file_info['filename']} ({file_info['type'].upper()})"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.write(f"**Size:** {file_info['size']:,} bytes")
                        st.write(f"**Type:** {file_info['type'].upper()}")
                    
                    with col2:
                        created_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(file_info['created']))
                        st.write(f"**Created:** {created_time}")
                    
                    with col3:
                        download_url = f"{API_BASE_URL}/download/{file_info['filename']}"
                        st.markdown(
                            f'<a href="{download_url}" target="_blank" style="color: #007bff; text-decoration: none; background-color: #e7f3ff; padding: 8px 16px; border-radius: 4px; border: 1px solid #007bff;">⬇️ Download</a>',
                            unsafe_allow_html=True
                        )
        else:
            st.info("No generated files found. Generate some training content first!")
    
    else:
        display_error(f"Failed to load files: {files_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()