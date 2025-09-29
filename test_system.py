"""
Test script for Instructional Design RAG System
Tests all components and functionality
"""

import os
import sys
import tempfile
import time
import json
from pathlib import Path
import requests
import subprocess

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_TIMEOUT = 30

class TestResults:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.errors = []
    
    def add_test(self, test_name: str, passed: bool, error: str = None):
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            print(f"✅ {test_name}")
        else:
            self.failed_tests += 1
            print(f"❌ {test_name}")
            if error:
                print(f"   Error: {error}")
                self.errors.append(f"{test_name}: {error}")
    
    def print_summary(self):
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Success Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.errors:
            print("\n❌ ERRORS:")
            for error in self.errors:
                print(f"  - {error}")
        
        return self.failed_tests == 0

def test_imports():
    """Test if all required modules can be imported"""
    results = TestResults()
    
    modules_to_test = [
        "document_processor",
        "vector_store", 
        "content_generator",
        "file_generators",
        "rag_pipeline",
        "api_server"
    ]
    
    for module in modules_to_test:
        try:
            __import__(module)
            results.add_test(f"Import {module}", True)
        except ImportError as e:
            results.add_test(f"Import {module}", False, str(e))
    
    return results

def test_dependencies():
    """Test if all required dependencies are available"""
    results = TestResults()
    
    dependencies = [
        "fastapi",
        "uvicorn", 
        "streamlit",
        "chromadb",
        "sentence_transformers",
        "python-pptx",
        "reportlab",
        "PyPDF2",
        "python-docx",
        "pandas",
        "matplotlib",
        "seaborn"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep.replace("-", "_"))
            results.add_test(f"Dependency {dep}", True)
        except ImportError as e:
            results.add_test(f"Dependency {dep}", False, str(e))
    
    return results

def test_core_components():
    """Test core RAG components"""
    results = TestResults()
    
    try:
        # Test document processor
        from document_processor import DocumentProcessor
        doc_processor = DocumentProcessor()
        results.add_test("DocumentProcessor initialization", True)
        
        # Test vector store
        from vector_store import VectorStoreManager
        vector_store = VectorStoreManager(collection_name="test_collection")
        results.add_test("VectorStoreManager initialization", True)
        
        # Test content generator
        from content_generator import InstructionalContentGenerator
        content_gen = InstructionalContentGenerator()
        results.add_test("InstructionalContentGenerator initialization", True)
        
        # Test file generators
        from file_generators import PowerPointGenerator, PDFGenerator
        ppt_gen = PowerPointGenerator()
        pdf_gen = PDFGenerator()
        results.add_test("File generators initialization", True)
        
        # Test main RAG pipeline
        from rag_pipeline import InstructionalDesignRAG
        rag = InstructionalDesignRAG(storage_dir="test_storage")
        results.add_test("RAG pipeline initialization", True)
        
    except Exception as e:
        results.add_test("Core components", False, str(e))
    
    return results

def create_test_document():
    """Create a test document for testing"""
    test_content = """
    Test Document for Instructional Design

    This is a test document containing instructional design content.
    
    Adult Learning Principles:
    1. Adults are self-directed learners
    2. Adults bring experience to learning
    3. Adults are goal-oriented
    4. Adults are practical learners
    
    Assessment Strategies:
    - Formative assessment during learning
    - Summative assessment at the end
    - Authentic assessment with real-world applications
    
    Best Practices:
    - Engage learners actively
    - Provide immediate feedback
    - Use varied instructional methods
    - Create supportive environment
    """
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        return f.name

def test_document_processing():
    """Test document processing functionality"""
    results = TestResults()
    
    try:
        from rag_pipeline import InstructionalDesignRAG
        rag = InstructionalDesignRAG(storage_dir="test_storage")
        
        # Create test document
        test_file = create_test_document()
        
        # Test document upload
        result = rag.upload_document(test_file)
        success = result.get('success', False)
        results.add_test("Document upload", success, result.get('error'))
        
        if success:
            # Test document search
            search_result = rag.search_content("adult learning")
            search_success = search_result.get('success', False)
            results.add_test("Document search", search_success, search_result.get('error'))
        
        # Clean up
        os.unlink(test_file)
        
    except Exception as e:
        results.add_test("Document processing", False, str(e))
    
    return results

def test_content_generation():
    """Test content generation functionality"""
    results = TestResults()
    
    try:
        from rag_pipeline import InstructionalDesignRAG
        rag = InstructionalDesignRAG(storage_dir="test_storage")
        
        # Create and upload test document
        test_file = create_test_document()
        upload_result = rag.upload_document(test_file)
        
        if upload_result.get('success'):
            # Test content generation
            gen_result = rag.generate_training_content(
                prompt="Create a 5-minute training on adult learning",
                output_format='ppt',
                duration_minutes=5,
                learning_level='beginner'
            )
            
            success = gen_result.get('success', False)
            results.add_test("Content generation", success, gen_result.get('error'))
            
            if success and gen_result.get('output_files'):
                results.add_test("Output file creation", True)
            else:
                results.add_test("Output file creation", False, "No output files generated")
        else:
            results.add_test("Content generation setup", False, "Failed to upload test document")
        
        # Clean up
        os.unlink(test_file)
        
    except Exception as e:
        results.add_test("Content generation", False, str(e))
    
    return results

def wait_for_api_server():
    """Wait for API server to be ready"""
    print("⏳ Waiting for API server to start...")
    
    for attempt in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print("✅ API server is ready")
                return True
        except:
            pass
        
        time.sleep(1)
    
    print("❌ API server failed to start within timeout")
    return False

def test_api_endpoints():
    """Test API endpoints"""
    results = TestResults()
    
    if not wait_for_api_server():
        results.add_test("API server startup", False, "Server not responding")
        return results
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        results.add_test("Health endpoint", response.status_code == 200, 
                        f"Status: {response.status_code}")
    except Exception as e:
        results.add_test("Health endpoint", False, str(e))
    
    # Test stats endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/stats", timeout=5)
        results.add_test("Stats endpoint", response.status_code == 200,
                        f"Status: {response.status_code}")
    except Exception as e:
        results.add_test("Stats endpoint", False, str(e))
    
    # Test upload endpoint with test file
    try:
        test_file = create_test_document()
        
        with open(test_file, 'rb') as f:
            files = {'files': ('test.txt', f, 'text/plain')}
            response = requests.post(f"{API_BASE_URL}/upload", files=files, timeout=10)
        
        upload_success = response.status_code == 200
        results.add_test("Upload endpoint", upload_success,
                        f"Status: {response.status_code}")
        
        if upload_success:
            # Test generation endpoint
            gen_data = {
                "prompt": "Create a 5-minute training on test content",
                "output_format": "ppt",
                "duration_minutes": 5,
                "learning_level": "beginner"
            }
            
            response = requests.post(f"{API_BASE_URL}/generate", json=gen_data, timeout=30)
            gen_success = response.status_code == 200
            results.add_test("Generate endpoint", gen_success,
                            f"Status: {response.status_code}")
        
        # Clean up
        os.unlink(test_file)
        
    except Exception as e:
        results.add_test("API upload/generate", False, str(e))
    
    return results

def test_file_generation():
    """Test PowerPoint and PDF generation"""
    results = TestResults()
    
    try:
        from file_generators import PowerPointGenerator, PDFGenerator
        
        # Test PowerPoint generation
        ppt_gen = PowerPointGenerator()
        
        # Create test slide data
        test_slides = [
            {
                'slide_number': 1,
                'type': 'title',
                'title': 'Test Presentation',
                'content': {
                    'main_title': 'Test Training Module',
                    'subtitle': 'Testing PPT Generation',
                    'duration': '5 minutes',
                    'date': '2024-01-01'
                }
            },
            {
                'slide_number': 2,
                'type': 'bullet_points',
                'title': 'Test Content',
                'content': {
                    'title': 'Key Points',
                    'bullet_points': ['Point 1', 'Point 2', 'Point 3']
                }
            }
        ]
        
        # Test PPT creation
        with tempfile.NamedTemporaryFile(suffix='.pptx', delete=False) as tmp:
            ppt_path = ppt_gen.create_presentation(test_slides, tmp.name)
            if os.path.exists(ppt_path):
                results.add_test("PowerPoint generation", True)
                os.unlink(ppt_path)
            else:
                results.add_test("PowerPoint generation", False, "File not created")
        
        # Test PDF generation
        pdf_gen = PDFGenerator()
        
        # Create test module data
        test_module = {
            'metadata': {
                'title': 'Test Training Module',
                'duration_minutes': 5,
                'learning_level': 'beginner',
                'format_type': 'document',
                'created_date': '2024-01-01T00:00:00'
            },
            'learning_objectives': ['Objective 1', 'Objective 2'],
            'content_outline': [
                {
                    'section': 'Introduction',
                    'duration_minutes': 2,
                    'key_points': ['Point 1', 'Point 2']
                }
            ],
            'detailed_content': [
                {
                    'type': 'introduction',
                    'title': 'Test Introduction',
                    'content': {'overview': 'Test overview'}
                }
            ],
            'activities': [],
            'assessment': {'questions': []},
            'resources': []
        }
        
        # Test PDF creation
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            pdf_path = pdf_gen.create_training_manual(test_module, tmp.name)
            if os.path.exists(pdf_path):
                results.add_test("PDF generation", True)
                os.unlink(pdf_path)
            else:
                results.add_test("PDF generation", False, "File not created")
                
    except Exception as e:
        results.add_test("File generation", False, str(e))
    
    return results

def run_all_tests():
    """Run all tests"""
    print("🧪 INSTRUCTIONAL DESIGN RAG SYSTEM - TEST SUITE")
    print("="*60)
    
    all_results = []
    
    print("\n📦 Testing Dependencies...")
    all_results.append(test_dependencies())
    
    print("\n📥 Testing Imports...")
    all_results.append(test_imports())
    
    print("\n🔧 Testing Core Components...")
    all_results.append(test_core_components())
    
    print("\n📄 Testing Document Processing...")
    all_results.append(test_document_processing())
    
    print("\n🎨 Testing Content Generation...")
    all_results.append(test_content_generation())
    
    print("\n📊 Testing File Generation...")
    all_results.append(test_file_generation())
    
    # API tests require server to be running
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print("\n🌐 Testing API Endpoints...")
            all_results.append(test_api_endpoints())
        else:
            print("\n⚠️  Skipping API tests (server not running)")
    except:
        print("\n⚠️  Skipping API tests (server not accessible)")
    
    # Calculate overall results
    total_tests = sum(r.total_tests for r in all_results)
    total_passed = sum(r.passed_tests for r in all_results)
    total_failed = sum(r.failed_tests for r in all_results)
    
    print("\n" + "="*60)
    print("🏆 OVERALL TEST RESULTS")
    print("="*60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_failed}")
    print(f"Success Rate: {(total_passed/total_tests)*100:.1f}%")
    
    if total_failed == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready to use.")
        return True
    else:
        print(f"\n⚠️  {total_failed} tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    # Clean up any existing test storage
    import shutil
    if os.path.exists("test_storage"):
        shutil.rmtree("test_storage")
    
    success = run_all_tests()
    
    # Clean up test storage
    if os.path.exists("test_storage"):
        shutil.rmtree("test_storage")
    
    sys.exit(0 if success else 1)