#!/bin/bash

# Run script for Instructional Design RAG System

echo "🚀 Starting Instructional Design RAG System..."

# Check if virtual environment exists
if [ ! -d "rag_env" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source rag_env/bin/activate

# Create log directory
mkdir -p logs

# Function to cleanup background processes
cleanup() {
    echo "🛑 Shutting down services..."
    kill $API_PID 2>/dev/null
    kill $STREAMLIT_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on exit
trap cleanup SIGINT SIGTERM

echo "🌐 Starting API server..."
python api_server.py > logs/api.log 2>&1 &
API_PID=$!

# Wait a moment for API to start
sleep 3

echo "🎨 Starting Streamlit frontend..."
HOME="$(pwd)" \
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
python -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 \
    > logs/streamlit.log 2>&1 < /dev/null &
STREAMLIT_PID=$!

echo "✅ System started successfully!"
echo ""
echo "🌐 Access your system at:"
echo "   📊 Web Interface: http://localhost:8501"
echo "   🔧 API Documentation: http://localhost:8000/docs"
echo "   🏠 API Main Page: http://localhost:8000"
echo ""
echo "📝 Logs are available in the logs/ directory"
echo "🛑 Press Ctrl+C to stop the system"

# Wait for background processes
wait
