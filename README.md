# 📚 Instructional Design RAG System

A comprehensive Retrieval-Augmented Generation (RAG) pipeline for creating professional training materials from your instructional design documents.

## 🎯 What It Does

This system allows you to:

1. **📤 Upload Documents**: Upload various types of instructional design documents (PDFs, Word docs, Excel files, etc.)
2. **🧠 AI Processing**: The system processes your documents and creates a searchable knowledge base using advanced AI embeddings
3. **🎨 Generate Content**: Request training materials with natural language prompts
4. **📊 Professional Output**: Get professionally formatted PowerPoint presentations and PDF manuals
5. **🔍 Smart Search**: Search through your knowledge base to find relevant content

## 🌟 Key Features

- **Multi-format Support**: PDF, DOCX, TXT, MD, XLSX, CSV
- **AI-Powered Content Generation**: Uses semantic search and content synthesis
- **Professional Outputs**: Creates PowerPoint presentations and PDF training manuals
- **Flexible Training Durations**: 5 minutes to 90+ minutes
- **Multiple Learning Levels**: Beginner, Intermediate, Advanced
- **Web Interface**: User-friendly Streamlit frontend
- **REST API**: Full API access for integration
- **Real-time Search**: Search through your knowledge base instantly

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- 4GB+ RAM recommended
- [Ollama](https://ollama.com/) installed and running locally
  - Ensure the embedding model is available: `ollama pull nomic-embed-text`
  - (Optional) Pull a generation model such as `ollama pull id-pro`
- Internet connection for the initial Python dependency installation

### Installation

1. **Clone or download the system files**

2. **Verify Ollama is serving locally**:
   ```bash
   ollama serve  # skip if Ollama service is already running
   ollama list   # confirm required models are available
   ```

3. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

4. **Start the system**:
   ```bash
   chmod +x run_system.sh
   ./run_system.sh
   ```

5. **Access the interfaces**:
   - 🎨 **Web Interface**: http://localhost:8501
   - 🔧 **API Documentation**: http://localhost:8000/docs
   - 🏠 **API Main Page**: http://localhost:8000

## 💡 Usage Examples

### Example 1: Basic Training Module
**Prompt**: "Create a 15-minute training module on project management"
**Output**: Professional PowerPoint with slides covering project management basics, activities, and assessment

### Example 2: Advanced Workshop
**Prompt**: "Generate a 30-minute advanced training on instructional design principles with interactive activities"
**Output**: Comprehensive training materials with detailed content and hands-on exercises

### Example 3: Assessment-Focused Content
**Prompt**: "Make a 20-minute intermediate training on assessment strategies for adult learners"
**Output**: Training materials focused on assessment techniques with practical examples

## 📁 System Architecture

```
📦 Instructional Design RAG System
├── 🧠 Core Components
│   ├── document_processor.py    # Document parsing and processing
│   ├── vector_store.py         # Vector embeddings and search
│   ├── content_generator.py    # AI content generation
│   ├── file_generators.py     # PPT and PDF creation
│   └── rag_pipeline.py        # Main orchestration
├── 🌐 Interfaces
│   ├── api_server.py          # FastAPI REST server
│   └── streamlit_app.py       # Web interface
├── 📋 Configuration
│   ├── requirements.txt       # Python dependencies
│   ├── setup.sh              # Setup script
│   └── run_system.sh         # Run script
└── 📊 Storage
    ├── storage/uploads/       # Uploaded documents
    ├── storage/vector_db/     # Vector database
    └── storage/outputs/       # Generated files
```

## 🔧 API Endpoints

### Document Management
- `POST /upload` - Upload documents
- `GET /documents` - List uploaded documents
- `DELETE /documents/{id}` - Delete a document

### Content Generation
- `POST /generate` - Generate training content
- `GET /search` - Search knowledge base
- `GET /files` - List generated files
- `GET /download/{filename}` - Download generated files

### System Management
- `GET /stats` - Get system statistics
- `GET /health` - Health check
- `POST /setup-demo` - Setup demo data

## 📊 Supported File Types

| Format | Extensions | Use Case |
|--------|------------|----------|
| PDF | .pdf | Research papers, manuals, guides |
| Word | .docx, .doc | Training documents, curricula |
| Text | .txt, .md | Notes, guidelines, procedures |
| Excel | .xlsx, .xls | Templates, data, assessments |
| CSV | .csv | Structured data, survey results |

## 🎨 Generated Content Structure

### PowerPoint Presentations
- **Title Slide**: Course title, duration, level
- **Learning Objectives**: Clear, measurable objectives
- **Content Slides**: Structured content with examples
- **Activity Slides**: Interactive exercises
- **Assessment Slides**: Knowledge checks
- **Summary Slide**: Key takeaways and next steps

### PDF Training Manuals
- **Title Page**: Course metadata
- **Table of Contents**: Structured navigation
- **Learning Objectives**: Detailed objectives
- **Content Sections**: Comprehensive content with examples
- **Activities**: Detailed activity instructions
- **Assessment**: Question bank with answer keys
- **Resources**: Source materials and references

## ⚙️ Configuration Options

### Content Generation Parameters
- **Duration**: 5-90+ minutes
- **Learning Level**: Beginner, Intermediate, Advanced
- **Output Format**: PowerPoint, PDF, or both
- **Content Style**: Professional, Modern, Minimal

### Search Parameters
- **Results Count**: 1-20 results
- **Context Type**: Training, Assessment, Theory
- **Similarity Threshold**: Configurable relevance scoring

## 🛠️ Advanced Usage

### Custom API Integration

```python
import requests

# Upload a document
with open('training_manual.pdf', 'rb') as f:
    files = {'files': f}
    response = requests.post('http://localhost:8000/upload', files=files)

# Generate content
data = {
    "prompt": "Create a 20-minute training on leadership skills",
    "output_format": "both",
    "duration_minutes": 20,
    "learning_level": "intermediate"
}
response = requests.post('http://localhost:8000/generate', json=data)
```

### Batch Document Upload

```python
import requests
import os

# Upload multiple documents
files = []
for filename in os.listdir('documents/'):
    if filename.endswith(('.pdf', '.docx')):
        with open(f'documents/{filename}', 'rb') as f:
            files.append(('files', f.read()))

response = requests.post('http://localhost:8000/upload', files=files)
```

## 🔍 Troubleshooting

### Common Issues

1. **"Cannot connect to API server"**
   - Ensure the API server is running on port 8000
   - Check if another service is using port 8000
   - Wait a few seconds after starting the API before using the web interface

2. **"No relevant content found"**
   - Upload more documents to the knowledge base
   - Try different search terms or broader topics
   - Use the demo data setup for testing

3. **Empty generated content**
   - Ensure your uploaded documents contain relevant instructional content
   - Try more specific prompts
   - Check that documents were processed successfully

4. **File generation errors**
   - Check system permissions for the storage/outputs directory
   - Ensure sufficient disk space
   - Verify all dependencies are installed correctly

### Performance Optimization

- **Large Knowledge Base**: For 100+ documents, consider increasing system memory
- **Faster Generation**: Use shorter durations and simpler prompts for quicker results
- **Better Quality**: Upload higher-quality source documents for better output

## 📈 System Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 4GB
- **Storage**: 2GB free space
- **OS**: Linux, macOS, or Windows with WSL

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 5GB+ free space
- **Network**: Stable internet for model downloads

## 🔐 Security Considerations

- The system runs locally and doesn't send data to external services
- Uploaded documents are stored locally in the storage directory
- Generated content is based only on your uploaded materials
- API endpoints are designed for local use (localhost only)

## 🤝 Contributing

This system is designed to be extensible:

1. **Add new file formats**: Extend `document_processor.py`
2. **Custom output formats**: Modify `file_generators.py`
3. **Enhanced AI**: Integrate additional language models
4. **New interfaces**: Build additional frontends using the API

## 📄 License

This project is provided as-is for educational and commercial use. Please ensure you have appropriate licenses for any dependencies used in production environments.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the API documentation at http://localhost:8000/docs
3. Check the logs in the `logs/` directory
4. Ensure all dependencies are correctly installed

## 🚀 What's Next?

Potential enhancements:
- Integration with Learning Management Systems (LMS)
- Multi-language support
- Advanced assessment generation
- Real-time collaboration features
- Cloud deployment options
- Mobile-responsive interface

---

**Happy Training! 📚✨**
