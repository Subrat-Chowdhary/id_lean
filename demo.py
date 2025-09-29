"""
Demonstration script for Instructional Design RAG System
Shows system capabilities and usage examples
"""

import os
import json
import time
from pathlib import Path
from rag_pipeline import InstructionalDesignRAG, create_sample_rag_system

def demonstrate_system():
    """Demonstrate the RAG system capabilities"""
    
    print("🎭 INSTRUCTIONAL DESIGN RAG SYSTEM DEMONSTRATION")
    print("="*60)
    
    # Initialize the system with sample data
    print("\n🚀 Step 1: Setting up RAG system with sample data...")
    rag = create_sample_rag_system()
    
    # Get system statistics
    print("\n📊 Step 2: Checking knowledge base statistics...")
    stats = rag.get_knowledge_base_stats()
    if stats['success']:
        print(f"✅ Knowledge base ready!")
        print(f"   - Documents: {stats['stats']['unique_documents']}")
        print(f"   - Content chunks: {stats['stats']['total_chunks']}")
        print(f"   - File types: {list(stats['stats']['file_types'].keys())}")
    
    # Demonstrate search functionality
    print("\n🔍 Step 3: Demonstrating search functionality...")
    search_queries = [
        "adult learning principles",
        "assessment strategies", 
        "instructional design models"
    ]
    
    for query in search_queries:
        print(f"\n   Searching for: '{query}'")
        search_result = rag.search_content(query, n_results=3)
        if search_result['success']:
            print(f"   Found {len(search_result['results'])} relevant chunks")
            for i, result in enumerate(search_result['results'][:1], 1):
                print(f"   {i}. {result['metadata']['filename']} (Score: {result['similarity_score']:.3f})")
                preview = result['text'][:100] + "..." if len(result['text']) > 100 else result['text']
                print(f"      Preview: {preview}")
    
    # Demonstrate content generation
    print("\n🎨 Step 4: Demonstrating content generation...")
    
    training_examples = [
        {
            "prompt": "Create a 15-minute training module on adult learning principles",
            "duration": 15,
            "level": "intermediate",
            "format": "ppt"
        },
        {
            "prompt": "Generate a 10-minute beginner training on assessment strategies",
            "duration": 10,
            "level": "beginner", 
            "format": "pdf"
        },
        {
            "prompt": "Make a 20-minute advanced workshop on instructional design models",
            "duration": 20,
            "level": "advanced",
            "format": "both"
        }
    ]
    
    generated_files = []
    
    for i, example in enumerate(training_examples, 1):
        print(f"\n   Example {i}: {example['prompt']}")
        print(f"   Duration: {example['duration']} minutes | Level: {example['level']} | Format: {example['format']}")
        
        result = rag.generate_training_content(
            prompt=example['prompt'],
            output_format=example['format'],
            duration_minutes=example['duration'],
            learning_level=example['level']
        )
        
        if result['success']:
            print(f"   ✅ Generated content for topic: {result['topic']}")
            print(f"   📊 Used {result['sources_used']} source documents")
            
            for file_info in result['output_files']:
                print(f"   📄 Created: {file_info['filename']} ({file_info['type'].upper()})")
                generated_files.append(file_info)
        else:
            print(f"   ❌ Generation failed: {result['message']}")
    
    # Show generated files
    print(f"\n📁 Step 5: Generated files summary...")
    if generated_files:
        print(f"✅ Successfully generated {len(generated_files)} files:")
        for file_info in generated_files:
            file_path = Path(file_info['path'])
            size_mb = file_path.stat().st_size / (1024 * 1024)
            print(f"   • {file_info['filename']} ({file_info['type'].upper()}) - {size_mb:.1f} MB")
    
    # Demonstrate document management
    print(f"\n📚 Step 6: Document management capabilities...")
    docs_result = rag.list_documents()
    if docs_result['success']:
        print(f"✅ Document library contains {docs_result['total_documents']} documents:")
        for file_type, docs in docs_result['documents'].items():
            print(f"   • {file_type}: {len(docs)} files")
    
    print(f"\n🎉 Demonstration completed successfully!")
    print(f"📁 Check the 'storage/outputs/' directory for generated files")
    
    return rag, generated_files

def create_custom_training_example():
    """Show how to create custom training content"""
    
    print("\n" + "="*60)
    print("🎯 CUSTOM TRAINING CREATION EXAMPLE")
    print("="*60)
    
    # Initialize system
    rag = InstructionalDesignRAG()
    
    # Create custom content document
    custom_content = """
    Project Management Fundamentals
    
    Introduction to Project Management:
    Project management is the application of knowledge, skills, tools, and techniques 
    to project activities to meet project requirements.
    
    Key Project Management Processes:
    1. Initiation - Defining the project scope and objectives
    2. Planning - Developing a comprehensive project plan
    3. Execution - Carrying out the project activities
    4. Monitoring & Controlling - Tracking progress and performance
    5. Closing - Finalizing all project activities
    
    Project Constraints (Triple Constraint):
    - Scope: What needs to be accomplished
    - Time: When the project needs to be completed
    - Cost: Budget allocated for the project
    
    Stakeholder Management:
    - Identify all project stakeholders
    - Understand their expectations and requirements
    - Communicate regularly and effectively
    - Manage stakeholder engagement throughout the project
    
    Risk Management:
    - Identify potential risks early
    - Assess probability and impact
    - Develop mitigation strategies
    - Monitor and review risks regularly
    
    Best Practices:
    - Define clear objectives and success criteria
    - Create detailed project plans with realistic timelines
    - Establish regular communication channels
    - Monitor progress against milestones
    - Be prepared to adapt and adjust as needed
    """
    
    # Save custom document
    custom_doc_path = "storage/uploads/custom_project_management.txt"
    os.makedirs("storage/uploads", exist_ok=True)
    
    with open(custom_doc_path, 'w', encoding='utf-8') as f:
        f.write(custom_content)
    
    print("📝 Step 1: Created custom project management document")
    
    # Upload the document
    upload_result = rag.upload_document(custom_doc_path)
    
    if upload_result['success']:
        print(f"✅ Step 2: Uploaded document successfully")
        print(f"   - Document ID: {upload_result['document_id']}")
        print(f"   - Chunks created: {upload_result['chunks_created']}")
    
    # Generate various training formats
    training_scenarios = [
        {
            "name": "Quick Overview",
            "prompt": "Create a 10-minute overview of project management fundamentals for new team members",
            "duration": 10,
            "level": "beginner",
            "format": "ppt"
        },
        {
            "name": "Comprehensive Training",
            "prompt": "Generate a 30-minute comprehensive training on project management processes and best practices",
            "duration": 30,
            "level": "intermediate",
            "format": "both"
        },
        {
            "name": "Advanced Workshop",
            "prompt": "Create a 45-minute advanced workshop on project risk management and stakeholder engagement",
            "duration": 45,
            "level": "advanced",
            "format": "pdf"
        }
    ]
    
    print(f"\n🎨 Step 3: Generating training content in different formats...")
    
    for scenario in training_scenarios:
        print(f"\n   Creating: {scenario['name']}")
        
        result = rag.generate_training_content(
            prompt=scenario['prompt'],
            output_format=scenario['format'],
            duration_minutes=scenario['duration'],
            learning_level=scenario['level']
        )
        
        if result['success']:
            print(f"   ✅ Success: Generated {scenario['format'].upper()} for '{result['topic']}'")
            for file_info in result['output_files']:
                print(f"      📄 {file_info['filename']}")
        else:
            print(f"   ❌ Failed: {result['message']}")
    
    print(f"\n🎯 Custom training creation completed!")

def api_usage_example():
    """Show how to use the system via API"""
    
    print("\n" + "="*60)
    print("🌐 API USAGE EXAMPLE")
    print("="*60)
    
    import requests
    
    api_url = "http://localhost:8000"
    
    # Check if API is running
    try:
        health_response = requests.get(f"{api_url}/health", timeout=5)
        if health_response.status_code != 200:
            print("❌ API server is not running. Start it with: python api_server.py")
            return
    except:
        print("❌ Cannot connect to API server. Make sure it's running on localhost:8000")
        return
    
    print("✅ API server is running")
    
    # Example API calls
    print("\n📊 Getting system statistics...")
    stats_response = requests.get(f"{api_url}/stats")
    if stats_response.status_code == 200:
        stats = stats_response.json()
        if stats['success']:
            print(f"   Documents: {stats['stats']['unique_documents']}")
            print(f"   Chunks: {stats['stats']['total_chunks']}")
    
    print("\n🔍 Searching knowledge base...")
    search_params = {"query": "project management", "n_results": 3}
    search_response = requests.get(f"{api_url}/search", params=search_params)
    if search_response.status_code == 200:
        search_data = search_response.json()
        if search_data['success']:
            print(f"   Found {len(search_data['results'])} results")
    
    print("\n🎨 Generating training content via API...")
    generate_data = {
        "prompt": "Create a 15-minute training on leadership skills",
        "output_format": "ppt",
        "duration_minutes": 15,
        "learning_level": "intermediate"
    }
    
    generate_response = requests.post(f"{api_url}/generate", json=generate_data)
    if generate_response.status_code == 200:
        result = generate_response.json()
        if result['success']:
            print(f"   ✅ Generated training on: {result['topic']}")
            for file_info in result['output_files']:
                print(f"   📄 Created: {file_info['filename']}")
                download_url = f"{api_url}/download/{file_info['filename']}"
                print(f"   🔗 Download: {download_url}")
    
    print("\n📁 Listing generated files...")
    files_response = requests.get(f"{api_url}/files")
    if files_response.status_code == 200:
        files_data = files_response.json()
        if files_data['success']:
            print(f"   Total files: {files_data['total_files']}")
            for file_info in files_data['files'][:3]:  # Show first 3
                print(f"   📄 {file_info['filename']} ({file_info['type'].upper()})")

def performance_test():
    """Test system performance with multiple operations"""
    
    print("\n" + "="*60)
    print("⚡ PERFORMANCE TEST")
    print("="*60)
    
    rag = InstructionalDesignRAG()
    
    # Test document processing speed
    print("📄 Testing document processing speed...")
    
    test_docs = [
        ("Small document", "This is a small test document with minimal content."),
        ("Medium document", "This is a medium-sized document. " * 100),
        ("Large document", "This is a large document with extensive content. " * 500)
    ]
    
    for doc_name, content in test_docs:
        # Create test file
        test_path = f"storage/uploads/test_{doc_name.replace(' ', '_').lower()}.txt"
        os.makedirs("storage/uploads", exist_ok=True)
        
        with open(test_path, 'w') as f:
            f.write(content)
        
        # Time the upload
        start_time = time.time()
        result = rag.upload_document(test_path)
        end_time = time.time()
        
        if result['success']:
            print(f"   ✅ {doc_name}: {end_time - start_time:.2f}s ({result['chunks_created']} chunks)")
        else:
            print(f"   ❌ {doc_name}: Failed")
    
    # Test content generation speed
    print("\n🎨 Testing content generation speed...")
    
    generation_tests = [
        ("5-minute PPT", 5, "ppt"),
        ("15-minute PDF", 15, "pdf"),
        ("30-minute Both", 30, "both")
    ]
    
    for test_name, duration, format_type in generation_tests:
        start_time = time.time()
        result = rag.generate_training_content(
            prompt=f"Create a {duration}-minute training on test content",
            output_format=format_type,
            duration_minutes=duration,
            learning_level="intermediate"
        )
        end_time = time.time()
        
        if result['success']:
            print(f"   ✅ {test_name}: {end_time - start_time:.2f}s ({len(result['output_files'])} files)")
        else:
            print(f"   ❌ {test_name}: Failed - {result['message']}")

def main():
    """Main demonstration function"""
    
    print("🎭 Welcome to the Instructional Design RAG System Demo!")
    print("This demonstration will show you the system's capabilities.\n")
    
    try:
        # Run main demonstration
        rag, files = demonstrate_system()
        
        # Show custom training creation
        create_custom_training_example()
        
        # Show API usage if available
        api_usage_example()
        
        # Run performance tests
        performance_test()
        
        print("\n" + "="*60)
        print("🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n✨ What you've seen:")
        print("• Document upload and processing")
        print("• Intelligent content search")
        print("• AI-powered training generation")
        print("• Professional file creation (PPT/PDF)")
        print("• API integration capabilities")
        print("• Performance characteristics")
        
        print("\n🚀 Next steps:")
        print("• Upload your own instructional design documents")
        print("• Try different training prompts and scenarios")
        print("• Explore the web interface at http://localhost:8501")
        print("• Use the API for integration with your systems")
        
        print(f"\n📁 Generated files are in: storage/outputs/")
        print("📖 Full documentation available in README.md")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Demonstration interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demonstration failed: {str(e)}")
        print("🔧 Please check the system setup and try again")

if __name__ == "__main__":
    main()