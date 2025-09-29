# Configuration file for Instructional Design RAG System

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True

# Streamlit Configuration  
STREAMLIT_HOST = "0.0.0.0"
STREAMLIT_PORT = 8501

# Storage Configuration
STORAGE_DIR = "storage"
UPLOADS_DIR = "storage/uploads"
OUTPUTS_DIR = "storage/outputs"
VECTOR_DB_DIR = "storage/vector_db"

# Vector Store Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "instructional_design_docs"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Content Generation Configuration
DEFAULT_DURATION = 15
DEFAULT_LEVEL = "intermediate"
DEFAULT_FORMAT = "ppt"
MAX_SEARCH_RESULTS = 10

# File Generation Configuration
PPT_THEME = "professional"
PDF_INCLUDE_CHARTS = True

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_DIR = "logs"

# Performance Configuration
MAX_FILE_SIZE_MB = 50
MAX_CONCURRENT_UPLOADS = 5
TIMEOUT_SECONDS = 30