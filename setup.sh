#!/bin/bash

# Setup script for Instructional Design RAG System

echo "🚀 Setting up Instructional Design RAG System..."

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv rag_env
source rag_env/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p storage/uploads
mkdir -p storage/vector_db
mkdir -p storage/outputs
mkdir -p sample_documents
mkdir -p static
mkdir -p logs

# Set permissions
chmod +x setup.sh
chmod +x run_system.sh

echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Activate the virtual environment: source rag_env/bin/activate"
echo "2. Start the system: ./run_system.sh"
echo "3. Open your browser to:"
echo "   - API: http://localhost:8000"
echo "   - Web Interface: http://localhost:8501"
echo ""
echo "📖 Or follow the instructions in README.md"