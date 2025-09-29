"""
FastAPI Backend for Instructional Design RAG System
Provides REST API endpoints for document upload and content generation
"""

import os
import tempfile
import shutil
from typing import List, Optional
from pathlib import Path
import logging

from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Form
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_pipeline import InstructionalDesignRAG

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Instructional Design RAG System",
    description="API for generating training materials using RAG technology",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag_system = InstructionalDesignRAG()

# Mount static files
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Pydantic models for request/response
class GenerateContentRequest(BaseModel):
    prompt: str
    output_format: str = "ppt"  # 'ppt', 'pdf', or 'both'
    duration_minutes: int = 15
    learning_level: str = "intermediate"  # 'beginner', 'intermediate', 'advanced'

class SearchRequest(BaseModel):
    query: str
    n_results: int = 5

class UploadResponse(BaseModel):
    success: bool
    message: str
    document_id: Optional[str] = None
    filename: Optional[str] = None
    file_type: Optional[str] = None
    chunks_created: Optional[int] = None

class GenerateResponse(BaseModel):
    success: bool
    message: str
    topic: Optional[str] = None
    duration_minutes: Optional[int] = None
    learning_level: Optional[str] = None
    output_files: Optional[List[dict]] = None
    sources_used: Optional[int] = None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with basic UI"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Instructional Design RAG System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; text-align: center; }
            .section { margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            .endpoint { margin: 15px 0; padding: 10px; background: #e9ecef; border-left: 4px solid #007bff; }
            .method { font-weight: bold; color: #007bff; }
            code { background: #e9ecef; padding: 2px 5px; border-radius: 3px; }
            .status { text-align: center; padding: 20px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 5px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 Instructional Design RAG System</h1>
            
            <div class="status">
                <strong>✅ System is running and ready to serve!</strong>
            </div>
            
            <div class="section">
                <h2>🎯 What this system does:</h2>
                <ul>
                    <li>Upload instructional design documents (PDF, DOCX, TXT, etc.)</li>
                    <li>Generate training materials based on your content</li>
                    <li>Create PowerPoint presentations and PDF manuals</li>
                    <li>Use AI to curate content from your knowledge base</li>
                </ul>
            </div>
            
            <div class="section">
                <h2>🔧 API Endpoints:</h2>
                
                <div class="endpoint">
                    <span class="method">POST</span> <code>/upload</code><br>
                    Upload documents to build your knowledge base
                </div>
                
                <div class="endpoint">
                    <span class="method">POST</span> <code>/generate</code><br>
                    Generate training content based on your prompt
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <code>/documents</code><br>
                    List all uploaded documents
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <code>/search</code><br>
                    Search through your knowledge base
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <code>/files</code><br>
                    List generated training files
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <code>/stats</code><br>
                    Get knowledge base statistics
                </div>
                
                <div class="endpoint">
                    <span class="method">GET</span> <code>/docs</code><br>
                    Interactive API documentation (Swagger UI)
                </div>
            </div>
            
            <div class="section">
                <h2>🚀 Quick Start:</h2>
                <ol>
                    <li>Upload your instructional design documents using <code>POST /upload</code></li>
                    <li>Generate training content with <code>POST /generate</code></li>
                    <li>Download the generated PPT/PDF files</li>
                </ol>
            </div>
            
            <div class="section">
                <h2>💡 Example Request:</h2>
                <pre style="background: #2d3748; color: #e2e8f0; padding: 15px; border-radius: 5px; overflow-x: auto;">
POST /generate
{
    "prompt": "Create a 15-minute training module on adult learning principles",
    "output_format": "both",
    "duration_minutes": 15,
    "learning_level": "intermediate"
}</pre>
            </div>
            
            <p style="text-align: center; margin-top: 40px; color: #6c757d;">
                Visit <a href="/docs">/docs</a> for interactive API documentation
            </p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload one or more documents to the knowledge base
    Supports: PDF, DOCX, TXT, MD, XLSX, CSV
    """
    results = []
    
    for file in files:
        try:
            # Check file type
            allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.md', '.xlsx', '.xls', '.csv'}
            file_extension = Path(file.filename).suffix.lower()
            
            if file_extension not in allowed_extensions:
                results.append(UploadResponse(
                    success=False,
                    message=f"Unsupported file type: {file_extension}",
                    filename=file.filename
                ))
                continue
            
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                content = await file.read()
                tmp_file.write(content)
                tmp_file_path = tmp_file.name
            
            # Process document
            result = rag_system.upload_document(tmp_file_path, file.filename)
            
            # Clean up temporary file
            os.unlink(tmp_file_path)
            
            # Convert to response model
            if result['success']:
                results.append(UploadResponse(
                    success=True,
                    message=result['message'],
                    document_id=result['document_id'],
                    filename=result['filename'],
                    file_type=result['file_type'],
                    chunks_created=result['chunks_created']
                ))
            else:
                results.append(UploadResponse(
                    success=False,
                    message=result['message'],
                    filename=file.filename
                ))
                
        except Exception as e:
            logger.error(f"Error uploading {file.filename}: {str(e)}")
            results.append(UploadResponse(
                success=False,
                message=f"Error processing {file.filename}: {str(e)}",
                filename=file.filename
            ))
    
    # Return single result if only one file, otherwise return the first result but log all
    if len(files) == 1:
        return results[0]
    else:
        # For multiple files, return summary
        successful_uploads = sum(1 for r in results if r.success)
        return UploadResponse(
            success=successful_uploads > 0,
            message=f"Processed {len(files)} files: {successful_uploads} successful, {len(files) - successful_uploads} failed"
        )


@app.post("/generate", response_model=GenerateResponse)
async def generate_training_content(request: GenerateContentRequest):
    """
    Generate training content based on prompt
    
    Example prompt: "Create a 15-minute training module on project management"
    """
    try:
        result = rag_system.generate_training_content(
            prompt=request.prompt,
            output_format=request.output_format,
            duration_minutes=request.duration_minutes,
            learning_level=request.learning_level
        )
        
        if result['success']:
            return GenerateResponse(
                success=True,
                message=result['message'],
                topic=result['topic'],
                duration_minutes=result['duration_minutes'],
                learning_level=result['learning_level'],
                output_files=result['output_files'],
                sources_used=result['sources_used']
            )
        else:
            return GenerateResponse(
                success=False,
                message=result['message']
            )
            
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
async def search_content(
    query: str = Query(..., description="Search query"),
    n_results: int = Query(5, description="Number of results to return")
):
    """Search for content in the knowledge base"""
    try:
        result = rag_system.search_content(query, n_results)
        return result
    except Exception as e:
        logger.error(f"Error searching content: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
async def list_documents():
    """List all documents in the knowledge base"""
    try:
        result = rag_system.list_documents()
        return result
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document from the knowledge base"""
    try:
        result = rag_system.delete_document(document_id)
        return result
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get knowledge base statistics"""
    try:
        result = rag_system.get_knowledge_base_stats()
        return result
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files")
async def list_generated_files():
    """List all generated training files"""
    try:
        files = rag_system.get_generated_files()
        return {
            'success': True,
            'files': files,
            'total_files': len(files)
        }
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download a generated training file"""
    try:
        file_path = Path(rag_system.outputs_dir) / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        # Determine media type
        media_type = "application/octet-stream"
        if filename.endswith('.pptx'):
            media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
        elif filename.endswith('.pdf'):
            media_type = "application/pdf"
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type=media_type
        )
        
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/setup-demo")
async def setup_demo_data():
    """Setup demo data with sample documents"""
    try:
        # Create sample documents if they don't exist
        from rag_pipeline import create_sample_rag_system
        
        # This will create and upload sample documents
        sample_rag = create_sample_rag_system()
        
        stats = rag_system.get_knowledge_base_stats()
        
        return {
            'success': True,
            'message': 'Demo data setup completed',
            'stats': stats['stats'] if stats['success'] else None
        }
        
    except Exception as e:
        logger.error(f"Error setting up demo data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        stats = rag_system.get_knowledge_base_stats()
        return {
            'status': 'healthy',
            'system': 'Instructional Design RAG',
            'version': '1.0.0',
            'knowledge_base_status': 'connected' if stats['success'] else 'error'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "message": "The requested endpoint does not exist"}


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "message": "An unexpected error occurred"}


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Instructional Design RAG System API...")
    print("📚 Upload documents and generate training materials!")
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("🏠 Main Interface: http://localhost:8000")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )