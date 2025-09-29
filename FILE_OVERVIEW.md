# 🎯 Instructional Design RAG System - File Overview

This document provides a complete overview of all files in the Instructional Design RAG System.

## 📁 File Structure

```
📦 Instructional Design RAG System/
├── 🧠 Core System Files
│   ├── document_processor.py       # Document parsing and text extraction
│   ├── vector_store.py            # Vector embeddings and similarity search
│   ├── content_generator.py       # AI-powered content generation
│   ├── file_generators.py         # PowerPoint and PDF creation
│   └── rag_pipeline.py           # Main RAG orchestration
│
├── 🌐 Interface Files
│   ├── api_server.py              # FastAPI REST API server
│   └── streamlit_app.py           # Web interface
│
├── 🔧 Configuration & Setup
│   ├── requirements.txt           # Python dependencies
│   ├── config.py                 # System configuration
│   ├── setup.sh                  # Setup script
│   └── run_system.sh            # System startup script
│
├── 🧪 Testing & Demo
│   ├── test_system.py            # Comprehensive test suite
│   └── demo.py                   # System demonstration
│
└── 📖 Documentation
    ├── README.md                 # Complete system documentation
    └── FILE_OVERVIEW.md          # This file
```

## 🧠 Core System Components

### `document_processor.py`
**Purpose**: Handles document upload and text extraction
**Key Features**:
- Multi-format support (PDF, DOCX, TXT, Excel, CSV)
- Intelligent text chunking with overlap
- Metadata extraction and processing
- Batch processing capabilities

**Main Classes**:
- `DocumentProcessor`: Core document processing functionality

### `vector_store.py`
**Purpose**: Manages vector embeddings and similarity search
**Key Features**:
- ChromaDB integration for persistent storage
- Sentence transformer embeddings
- Semantic search capabilities
- Document management (add/delete/update)

**Main Classes**:
- `VectorStoreManager`: Vector database operations and search

### `content_generator.py`
**Purpose**: Generates structured instructional content
**Key Features**:
- Training module generation with proper ID structure
- Learning objectives creation
- Activity and assessment generation
- Multiple learning levels support

**Main Classes**:
- `InstructionalContentGenerator`: Content synthesis and generation

### `file_generators.py`
**Purpose**: Creates professional output files
**Key Features**:
- PowerPoint presentation generation
- PDF training manual creation
- Professional formatting and styling
- Multiple slide types and layouts

**Main Classes**:
- `PowerPointGenerator`: PPT file creation
- `PDFGenerator`: PDF document creation

### `rag_pipeline.py`
**Purpose**: Orchestrates the entire RAG workflow
**Key Features**:
- End-to-end pipeline management
- Document upload and processing
- Content generation coordination
- File output management

**Main Classes**:
- `InstructionalDesignRAG`: Main system orchestrator

## 🌐 Interface Components

### `api_server.py`
**Purpose**: Provides REST API access to the system
**Key Features**:
- FastAPI-based REST endpoints
- File upload handling
- Content generation API
- System management endpoints

**Key Endpoints**:
- `POST /upload` - Upload documents
- `POST /generate` - Generate training content
- `GET /search` - Search knowledge base
- `GET /download/{filename}` - Download generated files

### `streamlit_app.py`
**Purpose**: User-friendly web interface
**Key Features**:
- Intuitive document upload interface
- Interactive content generation
- Real-time search capabilities
- File management and download

**Key Pages**:
- Upload Documents
- Generate Content
- Search Knowledge Base
- View Statistics
- Manage Generated Files

## 🔧 Setup and Configuration

### `requirements.txt`
**Purpose**: Python package dependencies
**Key Dependencies**:
- FastAPI & Uvicorn (API server)
- Streamlit (web interface)
- ChromaDB (vector database)
- Sentence Transformers (embeddings)
- Python-PPTX (PowerPoint generation)
- ReportLab (PDF generation)
- Document processing libraries

### `config.py`
**Purpose**: System configuration settings
**Configurable Options**:
- API and Streamlit ports
- Storage directories
- Vector database settings
- Content generation defaults
- Performance parameters

### `setup.sh`
**Purpose**: Automated system setup
**Setup Tasks**:
- Creates Python virtual environment
- Installs all dependencies
- Creates necessary directories
- Sets up file permissions

### `run_system.sh`
**Purpose**: Start both API and web interface
**Startup Process**:
- Activates virtual environment
- Starts API server in background
- Launches Streamlit interface
- Manages logging and cleanup

## 🧪 Testing and Demo

### `test_system.py`
**Purpose**: Comprehensive system testing
**Test Categories**:
- Dependency verification
- Component initialization
- Document processing
- Content generation
- API endpoint testing
- File generation validation

### `demo.py`
**Purpose**: System demonstration and examples
**Demo Features**:
- Sample data creation
- Content generation examples
- Performance testing
- API usage examples

## 📖 Documentation

### `README.md`
**Purpose**: Complete system documentation
**Sections**:
- System overview and features
- Installation instructions
- Usage examples
- API documentation
- Troubleshooting guide
- Architecture details

### `FILE_OVERVIEW.md` (This File)
**Purpose**: File-by-file system breakdown
**Content**:
- Complete file structure
- Component descriptions
- Key features and classes
- Setup and usage guidance

## 🚀 Quick Start Guide

1. **Setup System**:
   ```bash
   ./setup.sh
   ```

2. **Start System**:
   ```bash
   ./run_system.sh
   ```

3. **Access Interfaces**:
   - Web Interface: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

4. **Test System**:
   ```bash
   python test_system.py
   ```

5. **Run Demo**:
   ```bash
   python demo.py
   ```

## 🎯 System Capabilities Summary

### Document Processing
- ✅ PDF text extraction
- ✅ Word document processing
- ✅ Excel and CSV data handling
- ✅ Markdown and text files
- ✅ Intelligent text chunking
- ✅ Metadata extraction

### Content Generation
- ✅ Training module structure
- ✅ Learning objectives creation
- ✅ Interactive activities
- ✅ Assessment questions
- ✅ Multiple learning levels
- ✅ Flexible duration options

### File Generation
- ✅ Professional PowerPoint presentations
- ✅ Comprehensive PDF manuals
- ✅ Custom formatting and styling
- ✅ Multiple slide/page layouts
- ✅ Charts and visualizations
- ✅ Resource references

### System Features
- ✅ Vector-based semantic search
- ✅ Real-time content retrieval
- ✅ Batch document processing
- ✅ Web and API interfaces
- ✅ Comprehensive testing
- ✅ Performance monitoring

## 🔄 Workflow Overview

1. **Document Upload** → `document_processor.py` → Extract and chunk text
2. **Vector Storage** → `vector_store.py` → Create embeddings and store
3. **Content Request** → `rag_pipeline.py` → Coordinate generation process
4. **Content Search** → `vector_store.py` → Find relevant content
5. **Content Generation** → `content_generator.py` → Create structured content
6. **File Creation** → `file_generators.py` → Generate PPT/PDF files
7. **File Delivery** → API/Web interface → Provide download links

## 🛠️ Customization Options

### Adding New Document Types
- Extend `DocumentProcessor` class
- Add new file extension handlers
- Implement text extraction methods

### Custom Content Templates
- Modify `content_generator.py` templates
- Add new training module structures
- Create custom slide layouts

### Enhanced File Formats
- Extend `file_generators.py`
- Add new output format generators
- Implement custom styling options

### API Extensions
- Add new endpoints in `api_server.py`
- Implement additional functionality
- Create custom integrations

---

**🎉 The Instructional Design RAG System is now ready for use!**

For detailed usage instructions, see the main README.md file.
For technical support, run the test suite and demo scripts first.